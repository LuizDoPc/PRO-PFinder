#!/usr/bin/env python

# Input: a raw file
#
# Outputs (up to k=12) the k-nearest neighbors of a gene on both sides. 
# Does not include circularity in general...
#
# Unlike the other version, this one will generate a neighbor table including
# BOTH strands as equivalent, rather than just ONE.

from __future__ import print_function
import sys
from operator import itemgetter
import re
import fileinput
import optparse

usage = "%prog < raw_file > neighborhood_file"
description = "Compute neighbors of each gene from their location (the neighbors do not have to share a strand). Neighborhood is based on number of genes, not on number of base pairs. The function correctly deals with multiple contigs present in the file"
parser = optparse.OptionParser(usage=usage, description=description)
parser.parse_args()

MAXK = 10

geneTuples = []
for line in fileinput.input("-"):
    spl = line.strip('\r\n').split("\t")

    # Protein-coding genes only
    if not spl[2] == "peg":
        continue

    # Gene ID contains the organism ID
    orgid = re.search("\|(\d+\.\d+)", spl[1])
    if orgid == None:
        sys.stderr.write("WARNING: No organism ID found with expected format ...\n")
        orgid = ''
    else:
        orgid = orgid.group(1)

    # Gene ID, Organism+Contig, Start, Stop, Strand, Annotation
    # Add organism to contig name to avoid non-unique contig names like "contig00001" conflicting when
    # we concatinate all of them.
    geneTuples.append( (spl[1], orgid + "." + spl[0], int(spl[4]), int(spl[5]), spl[6], spl[7]) )

# Sort by contig first, then by start
sortGeneTuples = sorted(geneTuples, key=itemgetter(1,3))

# Separate them by contig
contigToTuple = {}
for tup in sortGeneTuples:
    if tup[1] in contigToTuple:
        contigToTuple[tup[1]].append(tup)
    else:
        contigToTuple[tup[1]] = [ tup ]

# Iterate through them and make a nice file
for contig in contigToTuple:
    currentTuples = contigToTuple[contig]
    for ii in range(len(currentTuples)):
        # range() function cuts off the end so we need to actually do MAXK + 1 for the rhs...
        for jj in range(-MAXK, MAXK+1):
            # No circularity - just continue if we're out of bounds.
            if ii+jj < 0:
                continue
            if ii+jj > len(currentTuples) - 1:
                continue
            # Print the gene as a neighbor - also print location and contig as a sanity check
            print("%s\t%s\t%d\t%s\t%d\t%d\t%s\t%s" %(currentTuples[ii][0], currentTuples[ii+jj][0], 
                                              jj, 
                                              currentTuples[ii+jj][1], currentTuples[ii+jj][2], currentTuples[ii+jj][3], currentTuples[ii+jj][4], currentTuples[ii+jj][5]))
