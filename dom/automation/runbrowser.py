#!/usr/bin/env python

import os
import sys
import platform
from optparse import OptionParser

oldcwd = os.getcwd()
#os.chdir(SCRIPT_DIRECTORY)

def runBrowser():
  parser = OptionParser()
  # we want to pass down everything from automation.__all__
  parser.add_option("--valgrind",
                    action = "store_true", dest = "valgrind",
                    default = False,
                    help = "use valgrind with a reasonable set of options")
  parser.add_option("--symbols-dir",
                    action = "store", dest = "symbolsDir",
                    default = None)
  parser.add_option("--leak-log-file",
                    action = "store", dest = "leakLogFile",
                    default = None)
  options, args = parser.parse_args(sys.argv)
  
  reftestScriptDir = args[1]
  utilityDir = args[2]
  profileDir = args[3]
  url = args[4]
  if url == "silent":
    url = "-silent"

  sys.path.append(reftestScriptDir)
  try:
    from automation import Automation
    import automationutils
  finally:
    sys.path.pop()
  automation = Automation()

  # also run automation.py's options parser, but don't give it any input
  aparser = OptionParser()
  automationutils.addCommonOptions(aparser, defaults=dict(zip(automation.__all__, [getattr(automation, x) for x in automation.__all__])))
  automation.addCommonOptions(aparser)
  aOptions = aparser.parse_args([])[0]

  theapp = os.path.join(reftestScriptDir, automation.DEFAULT_APP)
  if not os.path.exists(theapp):
    print "RUNBROWSER ERROR | runbrowser.py | Application %s doesn't exist." % theapp
    sys.exit(1)
  print "theapp: " + theapp

  if aOptions.xrePath is None:
    aOptions.xrePath = os.path.dirname(theapp)

  debuggerInfo = automationutils.getDebuggerInfo(oldcwd, aOptions.debugger, aOptions.debuggerArgs,
     aOptions.debuggerInteractive);

  # browser environment
  browserEnv = automation.environment(xrePath = aOptions.xrePath)
  # stack-gathering is slow and semi-broken on Mac, but it's great on Linux
  browserEnv["XPCOM_DEBUG_BREAK"] = "warn" if platform.system() == "Darwin" else "stack"
  browserEnv["MOZ_GDB_SLEEP"] = "2" # seconds
  if not options.valgrind:
    browserEnv["MallocScribble"] = "1"
    browserEnv["MallocPreScribble"] = "1"
  if automation.IS_DEBUG_BUILD and not options.valgrind and options.leakLogFile:
      browserEnv["XPCOM_MEM_LEAK_LOG"] = options.leakLogFile

  # run once with -silent to let the extension manager do its thing
  # and then exit the app
  print("RUNBROWSER INFO | runbrowser.py | runApp: start.")
  status = automation.runApp(None, browserEnv, theapp, profileDir,
                             [url],
                             utilityPath = utilityDir,
                             xrePath=aOptions.xrePath,
                             symbolsPath=options.symbolsDir,
                             maxTime = 300.0,
                             timeout = 120.0
                             )
  print("RUNBROWSER INFO | runbrowser.py | runApp: exited with status " + str(status))

if __name__ == "__main__":
  runBrowser()


def XXXstrandedCode():
  if options.valgrind:
    print "About to use valgrind"
    assert not debuggerInfo
    debuggerInfo2 = automationutils.getDebuggerInfo(oldcwd, "valgrind", "", False);
    debuggerInfo2["args"] = [
      "--error-exitcode=" + str(VALGRIND_ERROR_EXIT_CODE),
      "--suppressions=" + os.path.join(knownPath, "valgrind.txt"), # xxx knownPath, some of this needs to be in rundomfuzz i guess
      "--gen-suppressions=all"
    ]
    if automation.IS_MAC:
      debuggerInfo2["args"].append("--dsymutil=yes")
  else:
    debuggerInfo2 = debuggerInfo
