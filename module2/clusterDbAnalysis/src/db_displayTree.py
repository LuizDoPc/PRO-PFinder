#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Display a tree or reroot.
#
# Comes with a decent set of options.

from __future__ import print_function
import numpy
import optparse
import os
import sys

from FileLocator import *
from sanitizeString import *

####################################
# Lets read input arguments first.
####################################
usage = "%prog (-s -b basename|-p -b basename|-n -b basename|-d) [options] Newick_file"
description="""Display a tree with annotations and specified root and formats.
There is no default activity; one of -s, -p, -n, or -d must be specified.."""
parser = optparse.OptionParser(usage=usage, description=description)
parser.add_option("-d", "--display", help="Display result", action="store_true", dest="display", default=False)
parser.add_option("-s", "--savesvg", help="Convert the file to svg (requires -b)", action="store_true", dest="savesvg", default=False)
parser.add_option("-p", "--savepng", help="Convert the file to png (requires -b, implies -s)", action="store_true", dest="savepng", default=False)
parser.add_option("-n", "--savenewick", help="Save re-rooted tree as a newick file (requires -b)", action="store_true", dest="savenewick", default=False)
parser.add_option("-b", "--basename", help="Base name for file outputs (ignored without -s or -p)", action="store", type="str", dest="basename", default=None)
parser.add_option("-t", "--no_bootstraps", help="Omit bootstrap values when drawing tree.", action="store_true", dest="no_bootstraps", default=False)
parser.add_option("-r", "--rootgene", help="Root on this gene (default = keep same root as nwk file).", action="store", type="str", dest="rootgene", default=None)
parser.add_option("-o", "--rootorg", help="Root on this organism ID (e.g. 83333.1) (default = keep same root as nwk file)", action="store", type="str", dest="rootorg", default=None)

parser.add_option("-f", "--data_file", help = """Table of _numeric_ data with gene ID (leaf name, which must match the leaf names in the newick file exactly)
on the first column and data to attach to the leaves on the rest.

Note that the first row must look like this:
#names [column_label1] [column_label2] ...

Do not make a column label for the leaf name column. The #names is just a place holder - 
but the ETE parser will fail without it.
The ETE parser will also fail without a label row with the right number of entries!
""",
                  action = "store", type="str", dest="datafile", default=None)
parser.add_option("-w", "--data_width", help="Desired width of each data point on a heatmap (only valid with -f, default = 60)", action="store", type="int", dest="data_width", default=60)

parser.add_option("-m", "--data_textfile", help="""Table of _arbitrary text__ data with gene ID (leaf name, which must match the leaf names in the newick file exactly)
on the first column and data to attach to the leaves on the rest. See -f text for file format to use.""", action="store", dest="textfile", type="str", default=None)
parser.add_option("-z", "--fontsize", help="(only with -m) Font size for arbitrary text.", action="store", dest="fontsize", type="int", default=40)

(options, args) = parser.parse_args()

# Must specify a newick file
if len(args) < 1:
    sys.stderr.write("ERROR: Newick file must be specified. Use -h for help details\n")
    exit(2)

# Have to tell us to do something.
if not ( options.savesvg or options.savepng or options.display or options.savenewick):
    sys.stderr.write("ERROR: At least one of -p, -s, -n or -d must be specified. Use -h for help details\n")
    exit(2)

# Must specify a base file name if you want to save a file
if ( options.savesvg or options.savepng or options.savenewick ) and options.basename == None:
    sys.stderr.write("ERROR: Calling with -p (savepng) or -s (savesvg) requires specification of a base filename to save to\n")
    exit(2)

# Cannot root on both genes and organisms
if ( not options.rootgene == None ) and ( not options.rootorg == None ):
    sys.stderr.write("ERROR: Can only specify one of -o and -r (rooting options)\n")
    exit(2)

# Currently using both data file (for a heatmap) and text file is not supported
if options.textfile is not None and options.datafile is not None:
    sys.stderr.write("ERROR: Currently both adding a heatmap and arbitrary data is not supported.Please pick one or the other.\n")
    exit(2)

# Since we need SVG to get PNG the savepng option overrides the savesvg option
if options.savepng:
    options.savesvg = True

####################################
# Import lots of stuff for drawing...
####################################

from ete2 import Tree, faces, TreeStyle, NodeStyle, AttrFace, ClusterTree, ProfileFace
import fileinput
import sqlite3
from TreeFuncs import *

# Read Newick file
sys.stderr.write("Reading tree file...\n")

if options.datafile is None:
    t = Tree(args[0])
else:
    t = ClusterTree(args[0], options.datafile)
    
# If outgroup is specified, re-root now before doing anything else.
# This will just fail if the specified protein isn't present in the tree.
t = rerootEteTree(t, root_leaf = options.rootgene, root_leaf_part = options.rootorg)

##############################################
# Get various gene / organism / annotation information out of the database
##############################################

# Annotation and organism
geneToAnnote = {}
geneToOrganism = {}
sys.stderr.write("Reading gene annotations and organisms from database...\n")

# FIXME - This should call the library functions to get geneinfo for specific sets of genes
# instead of doing this.
con = sqlite3.connect(locateDatabase())
cur = con.cursor()
cur.execute("SELECT * FROM processed;")

for l in cur:
    spl = [ str(s) for s in list(l) ]
    # The SVG parser whines with some special characters (i.e. ' )
    # I use the sanitized version as a key here so that the code will work whether or not the leaf names
    # have been sanitized in the input tree.
    geneToAnnote[sanitizeString(spl[0], False)] = sanitizeString(spl[9], False)
    geneToOrganism[sanitizeString(spl[0], False)] = sanitizeString(spl[1], False)

ts = TreeStyle()

# Now we try and add the heatmap
# if the user requests it
#
# I borrowed some of this code from the ETE tutorial.
if options.datafile is not None:
    array = t.arraytable
    numcols = len(array.colNames)
    matrix_dist = [i for r in range(len(array.matrix))\
                       for i in array.matrix[r] if numpy.isfinite(i)]
    matrix_max = numpy.max(matrix_dist)
    matrix_min = numpy.min(matrix_dist)
    matrix_avg = matrix_min+((matrix_max-matrix_min)/2)

    # Max, Min, Center, Width, Height, Type)
    # I give it 60 pixels per column by default
    # (so that the width doesn't shrink down too much when we have more than a few columns)
    # However, the user has the ability to change this if they need to / want to for larger data sets
    profileFace  = ProfileFace(matrix_max, matrix_min, matrix_avg, width=numcols*options.data_width, height=35, style="heatmap")
    for node in t.traverse():
        if node.is_leaf():
            node.add_face(profileFace, 1, position = "aligned")
    
    # Add the color bar (kind of hacked in from matplotlib since there is no convenient way to get it from ETE)
    # I could generate this in situ... for now I just have a file I like and run with it.
    # This doesn't match exactlty becuase I don't have the time or motivation now to mess with QT to do it.
    # It should be pretty close though...
    from ete2 import ImgFace
    imgloc = os.path.join(locateRootDirectory(), "src", "internal", "Colormap.png")
    F1 = faces.TextFace("Minimum: %1.1f" %(matrix_min), ftype="Times", fsize=32 )
    F2 = faces.ImgFace(imgloc)
    F3 = faces.TextFace("%1.1f : Maximum" %(matrix_max), ftype="Times", fsize=32 )
    ts.legend.add_face(F1, 0)
    ts.legend.add_face(F2, 1)
    ts.legend.add_face(F3, 2)
    # Put it on the Bottom-left
    ts.legend_position = 3

if options.textfile is not None:
    fid = open(options.textfile, "r")
    # Our formatting requirements are the same as ETE's, which are:
    # 1: Tab delimited,
    # 2: #names in first row followed by titles,
    # 3: Node names in the first column followed by all the other data
    title_row = fid.readline().strip("\r\n").split("\t")
    n_titles = len(title_row)
    for idx, title in enumerate(title_row[1:]):
        coltitle = TextFace("    " + str(title) + "    ", ftype="Times", fsize=int(options.fontsize*1.2), fstyle = 'Bold')
        coltitle.hz_align = True
        # Organism name has column 0
        ts.aligned_header.add_face(coltitle, column=idx+1)
    for line in fid:
        spl = line.strip("\r\n").split("\t")
        if len(spl) != n_titles:
            sys.stderr.write("ERROR: Formatting error in file %s: Number of data in rows must equal number of column titles\n" %(options.textfile))
            exit(2)
        else:
            nodename_file = spl[0]
            data = spl[1:]
            myleaf = None
            for leaf in t.iter_leaves():
                if nodename_file == leaf.name:
                    myleaf = leaf
                    break
            if myleaf is None:
                sys.stderr.write("WARNING: Node name %s in the file has no equivalent in the tree, so it will be ignored.\n")
                continue
            for idx, datum in enumerate(data):
                text = TextFace("    " + str(datum) + "    " , ftype="Times", fsize=options.fontsize )
                text.hz_align = True
                leaf.add_face(text, idx+1, "aligned")

######################
# Add annotations and
# larger bootstrap values to tree
######################

for node in t.traverse():
    if node.is_leaf():
        sanitizedName = sanitizeString(node.name, False)
        # Dont' crash because of e.g. outgroups put in. We already warned about this so don't need to do it again.
        if sanitizedName in geneToOrganism and sanitizedName in geneToAnnote:
            newname = "_".join( [ node.name, geneToOrganism[sanitizedName], geneToAnnote[sanitizedName] ] )
            node.name = newname

# Standardize font sizes and tree width
# This must be done at the end or displaying node names wont work correctly.
t, ts = prettifyTree(t, show_bootstraps = not options.no_bootstraps, ts=ts)
# Standardize leaf order in equivalent trees (with same root)
t = standardizeTreeOrdering(t)

if options.savenewick:
    t.write(outfile="%s.nwk" %(options.basename), format=0)

if options.savesvg:
    # Some versions of ETE create a "test.svg" and others do not.
    # To avoid confusion (and in case TreeStyle isn't enforced)
    # I just create a new one.
    os.system("rm test.svg 2> /dev/null")
    t.render("%s.svg" %(options.basename), tree_style=ts)

# Convert the svg file into a high-quality (300 dpi) PNG file...
# The PNG converter in ETE gives a terrible quality image 
# 
# Use convert to make something better and then trim the edges off.
if options.savepng:
    os.system("convert -trim -depth 16 -background transparent %s.svg %s.png" %(options.basename, options.basename))

if options.display:
    t.show(tree_style=ts)

con.close()
