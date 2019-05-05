#!/usr/bin/env python

from __future__ import print_function
import optparse
import os
import re
import sys
from FileLocator import *

usage = "%prog -n groupname [match1] [match2] ..."
description = """Add all organims from orgfile that match [match1] [match2] ... to the groups file. 
The groups file is of the form [groupname] matchingorg1;matchingorg2;...
If nothing is specified as a match, this function makes a group with ALL the organisms in the orgfile and
adds it to the groups file.
"""
parser = optparse.OptionParser(usage=usage, description=description)
parser.add_option("-n", "--groupname", help="Group name (REQUIRED)", action="store", type="str", dest="groupname", default=None)
parser.add_option("-r", "--regex", help="Treat input names as regular expressions (D: treat them as literal strings)", action="store_true", dest="regex", default=False)
(options, args) = parser.parse_args()

if options.groupname is None:
    sys.stderr.write("ERROR: group name (-n) is a required argument\n")
    exit(2)

orgfile = locateOrganismFile(raiseError=True)
# VERY IMPORTANT - set raiseError to false here
# (and probably only here) because this is the function
# meant to create a group file if it doesn't already exist!
groupfile = locateGroupsFile(raiseError=False)

orglist = set()
for line in open(orgfile, "r"):
    spl = line.strip("\r\n").split("\t")
    orglist.add(spl[0])

group2orglist = {}
if os.path.exists(groupfile):
    for line in open(groupfile, "r"):
        spl = line.strip("\r\n").split("\t")
        # I use set so that order of organisms doesn't matter...
        group2orglist[spl[0]] = set(spl[1].split(";"))

if options.groupname in group2orglist:
    sys.stderr.write("ERROR: Specified group name %s already exists in groups file \n" %(options.groupname))
    exit(2)

# Look for matching organisms (enforcing uniqueness in case we get multiple possible matches that all match the same organism)
matchingorgs = set()
if len(args) == 0:
    sys.stderr.write("No matches provided - will use all the organisms in the named group...\n")
    matchingorgs = orglist
else:
    for arg in args:
        if options.regex:
            arg = re.compile(arg)
        for org in orglist:
            if options.regex:
                if arg.search(org) is not None:
                    matchingorgs.add(org)
            else:
                if arg.lower() in org.lower():
                    matchingorgs.add(org)

if len(matchingorgs) == 0:
    sys.stderr.write("ERROR: No organisms matched the specified queries.\n")
    exit(2)

# Don't cluster the same group with multiple names.
if matchingorgs in list(group2orglist.values()):
    sys.stderr.write("ERROR: The list of organisms matching your query is already present in the groups file under a different name\n")
    exit(2)

# Now that our sanity checks have passed...
linetoadd = "%s\t%s\n" %(options.groupname, ";".join(sorted(list(matchingorgs))))
groupfid = open(groupfile, "a+")
groupfid.write(linetoadd)
groupfid.close()
sys.stderr.write("New line written to groups file\n")
