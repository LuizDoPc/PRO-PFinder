#!/usr/bin/env python

# This is a pipe command.
#
# Pipe in a FASTA file
# The command will first substitute each gene ID in the fasta file with a 10-digit temporary identifier
# consistent with PHYLIP format
#

from __future__ import print_function
import fileinput
import sys
from Bio import AlignIO
from Bio import SeqIO
import optparse

usage = "%prog [options] < fasta_file > phylip file"
description = "Convert a fasta file to a phylip file"
parser = optparse.OptionParser(description=description, usage=usage)
parser.add_option("-c", "--convfile", help="File to convert new IDs back to original IDs (D = don't save file)", action="store", type="str", dest="convfile", default=None)
(options, args) = parser.parse_args()

# Read the FASTA file from stdin and convert it into a phylip file
# Use list so we actually edit in-place rather than
# just editing a copy that gets destroyed later!
aln = list(AlignIO.read(sys.stdin, "fasta"))

if not options.convfile == None:
    fid = open(options.convfile, "w")

# We will use this to convert back to the IDs in the fasta file
for i in range(len(aln)):
    newid = "S%09d" %(i)
    if not options.convfile == None:
        fid.write("%s\t%s\n" %(newid, aln[i].id))
    aln[i].id = newid

SeqIO.write(aln, sys.stdout, "phylip")
