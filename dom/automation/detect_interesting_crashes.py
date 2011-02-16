#!/usr/bin/env python

import os, sys, platform, signal
ready = False

def amiss(knownPath, crashLogFilename, verbose, msg):
    if not ready:
        readIgnoreList(knownPath)

    resetCounts()

    igmatch = []
    
    if os.path.exists(crashLogFilename):
        currentFile = file(crashLogFilename, "r")
        for line in currentFile:
            if isKnownCrashSignature(line):
                igmatch.append(ig)
        currentFile.close()
        
        if len(igmatch) == 0:
            # Would be great to print [@ nsFoo::Bar] in addition to the filename, but
            # that would require understanding the crash log format much better than
            # this script currently does.
            print "Unknown crash: " + crashLogFilename
            return True
        else:
            if verbose:
                print "@ Known crash: " + ", ".join(igmatch)
            return False
    else:
        if platform.mac_ver()[0].startswith("10.4") and msg.find("SIGABRT") != -1:
            # Tiger doesn't create crash logs for aborts.  No cause for alarm.
            return False
        else:
            print "Unknown crash (crash log is missing)"
            return True

TOO_MUCH_RECURSION_MAGIC = "[TMR] "

def readIgnoreList(knownPath):
    global ignoreList
    global ready
    ignoreList = []
    ignoreFile = file(os.path.join(knownPath, "crashes.txt"), "r")
    for line in ignoreFile:
        line = line.rstrip()
        if line.startswith(TOO_MUCH_RECURSION_MAGIC):
            ignoreList.append({"seenCount": 0, "needCount": 20, "theString": line[len(TOO_MUCH_RECURSION_MAGIC):]})
        elif len(line) > 0 and not line.startswith("#"):
            ignoreList.append({"seenCount": 0, "needCount": 1,  "theString": line})
    ignoreFile.close()
    ready = True
    #print "detect_interesting_crashes is ready (ignoring %d strings)" % (len(ignoreList))


def isKnownCrashSignature(line):
    global ignoreList
    for ig in ignoreList:
        if line.find(ig["theString"]) != -1:
            ig["seenCount"] += 1
            if ig["seenCount"] >= ig["needCount"]:
                return True
    return False

def resetCounts():
    global ignoreList
    for ig in ignoreList:
        ig["seenCount"] = 0
