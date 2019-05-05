#!/usr/bin/env python

# Given a list of organisms to stdin and a cluster run,
# identify clusters within that run that only have representatives
# within the specified list of organisms

from __future__ import print_function
import fileinput, operator, optparse, sqlite3, sys, os
from FileLocator import *
from sanitizeString import *

# This is necessary becuase ETE uses Print instaed of printing to stdout for
# import errors (e.g. if you're missing mysql interfaces for phylomedb)
tmp = sys.stdout
sys.stdout = sys.stderr
from ete2 import TextFace
sys.stdout = tmp

def addCoreDataToTree(ete_tree, runid, sanitized = False, any_org = False, all_org = False, only_org = False, none_org = False, uniq_org = False, color = "Black", compare_to_adj_clade = False):
    '''A function to add data related to gene and organism distribution across clusters
    to a core gene tree.

    Optionally (with compare_to_adj_clade) instead of comparing to the organisms in the whole tree,
    we compare to only the organisms in the sister clade at each node.

    See http://packages.python.org/ete2/reference/reference_treeview.html#color-names for a list
    of valid color names.'''

    cl = getClusterOrgsByRun(runid)

    outgroup = None
    nodenum = 0
    nodeNumToClusterList = {}
    # The strategy really doesn't matter, it's just for aesthetics... and to make sure its always the same.
    for node in ete_tree.traverse("postorder"):
        nodenum += 1
        leafnames = node.get_leaf_names()

        if compare_to_adj_clade:
            outgroup = []
            if node.is_root():
                # The root node has no sisters
                continue
            else:
                # This is a list - there can be more than one sister node
                sisters = node.get_sisters()
                for sister in sisters:
                    outgroup += sister.get_leaf_names()
                    pass
                pass
            pass
        
        clusters = findGenesByOrganismList(leafnames, runid, cl = cl, sanitized=True, 
                                           all_org = all_org, any_org = any_org, only_org = only_org, none_org = none_org, uniq_org = uniq_org, outgroup = outgroup)
        numclusters = len(clusters)
        # This is mostly so that I can keep track of progress.
        sys.stderr.write("%d (N%d)\n" %(numclusters, nodenum))
        numFace = TextFace("%d (N%d)" %(numclusters, nodenum), ftype="Times", fsize=24, fgcolor=color)
        node.add_face(numFace, 0, position="branch-bottom")
        nodeNumToClusterList[nodenum] = clusters

    return ete_tree, nodeNumToClusterList

def getClusterOrgsByRun(runid):
    '''
    Get a list of cluster IDs and organisms found in a cluster run.

    I separated this call from the findGenesByOrganismList below because we often need to call the latter
    many times and this one is the same for all of them (if the run ID is the same).

    The return object is a list of (runid, clusterid, organism) tuples sorted by cluster ID and then by organism.
    '''
    # From the sqlite database, download the list of clusterorgs

    con = sqlite3.connect(locateDatabase())
    cur = con.cursor()

    cl = []
    cur.execute("SELECT runid, clusterid, organism FROM clusterorgs WHERE clusterorgs.runid=?", (runid, ) )
    for res in cur:
        ls = [ str(s) for s in res ]
        cl.append(ls)

    # This is far faster than using ORDER BY in sqlite (at least unless I try to hack the SQL command to make it
    # get the order of operations right...)
    cl = sorted(cl, key=operator.itemgetter(1,2) )

    con.close()

    return cl

def findGenesByOrganismList(orglist, runid, cl = None, sanitized = False, any_org = False, all_org = False, only_org = False, none_org = False, uniq_org = False, pct_cutoff = None, outgroup = None):
    '''Identify clusters that have a specific set of properties with respect to a given set of
    organisms (orglist). The valid properties are ANY, ALL, ONLY, and NONE.

    Specifiy sanitized=TRUE if the organism names passed here are sanitized (spaces, periods, etc. replaced by
    underscores - see sanitizeString.py for the standard way to sanitize names).

    If the list of runid, clusterid, organismid tuples has already been computed, pass it in via the "cl"
    argument to avoid computing it again. Otherwise, it will be (re)computed within this function.

    You can also use the "cl" argument to restrict analysis to a specific set of (run ID, cluster ID) pairs
    by just passing that subset to the function. If no "cl" is passed then it is assumed you want to compare against
    ALL clusters in a run. 

    INGROUP: orglist
    OUTGROUP: How this is computed depends on how you call this function.
         By default: The outgroup is computed for each cluster as the group of organisms that are in that cluster but not in the ingroup.
         IF outgroup is passed to this function: The below are evaluated IGNORING any organisms that are not in the ingroup or the outgroup.

    Outgroup if specified is a list of organism names to use as part of the outgrpup.

    Clusters are pulled out according to the following table
    where the number in the entry corresponds to the number of represented ORGANISMS (NOT GENES) IN THE INGROUP
    (other combinations are possible - this is just a representative set of examples):

      Property  | Ingroup |  Outgroup
    +-----------+---------+-----------
      ALL       |  == N   |    >= 0
    +-----------+---------+-----------
      ANY       |  >= 1   |    >= 0
    +-----------+---------+-----------
      ONLY      |  >= 1   |    == 0
    +-----------+---------+-----------
      NONE      |  == 0   |    >= 1*
    +-----------+---------+-----------
     ALL + ONLY |  == N   |    == 0    - Genes that are only found in the ingroup and that are found in all members of the ingroup
    +-----------+---------+-----------
     ANY + ONLY |  >= 1   |    == 0    - Genes that are found only in the ingroup (but not necessarily in all of its members)
    +-----------+---------+-----------
     PCT_CUTOFF | >=PCT*N |    [Normally >=0 but you can also specify ONLY here]
    +-----------|---------+-----------
     ALL + NONE |
     ANY + NONE | Contradictions (raise errors).
     ONLY + NONE|     
    +-----------+---------+-----------    

    *: No clusters have 0 representatives

    N is the number of organisms in the ingroup

    UNIQ specifies that in addition to any other flags, genes in every organism in the ingroup
    must be uniquely represented in the cluster. Some groups definitions of "core genes" are
    satisfied by using AND and UNIQ as constraints.

    The function returns a list of (runid, clusterid) pairs that adhere to the user-specified criteria.
    '''


    if all_org and none_org:
        raise ValueError("ERROR: all_org and none_org options are contradictory\n")
    if any_org and none_org:
        raise ValueError("ERROR: any_org and none_org options are contradictory\n")
    if only_org and none_org:
        raise ValueError("ERROR: only_org and none_org options are contradictory\n")
    if not (only_org or all_org or any_org or none_org or pct_cutoff is not None):
        raise ValueError("ERROR: At least one of any_org, all_org, none_org, only_org or a pct_cutoff must be specified.\n")
    if pct_cutoff is not None and (float(pct_cutoff) > 100 or float(pct_cutoff) < 0):
        raise ValueError("ERROR: Percent cutoff must be between 0 and 100.\n")
    if pct_cutoff is not None and ( all_org or any_org or none_org ):
        raise ValueError("ERROR: Cannot specify both a percent cutoff and ANY, ALL or NONE\n")

    if pct_cutoff is not None:
        use_pct_cutoff = True
        pct_cutoff = float(pct_cutoff)
    else:
        use_pct_cutoff = False

    # Change sanitized gene names to un-sanitized gene names using the organisms file.
    if sanitized:
        allOrgsDict = {}
        p = locateOrganismFile()
        orgfile = open(p, "r")
        for line in orgfile:
            spl = line.strip("\r\n").split("\t")
            allOrgsDict[sanitizeString(spl[0], False)] = spl[0]

        for ii in range(len(orglist)):
            orglist[ii] = allOrgsDict[orglist[ii]]

        if outgroup is not None:
            for ii in range(len(outgroup)):
                outgroup[ii] = allOrgsDict[outgroup[ii]]

    # If no list of cluster\run\organism triplets is specified as an input,
    # we want to test the criteria with all of them.
    if cl is None:
        cl = getClusterOrgsByRun(runid)

    if outgroup is not None:
        outgroup = set(outgroup)

    previd = -1
    orgset = set(orglist)
    currentorgs = set()
    goodClusters = []
    for l in cl:
        # We slurp up all organisms in a specific cluster (storing in currentorgs)
        # and then once we have all of them we check for the specified conditions.
        if l[1] != previd:
            if previd != -1:
                (anyok, allok, noneok, onlyok, pctok) = False,False,False,False,False
                # Check ANY
                intersection = orgset & currentorgs
                if len(intersection) > 0:
                    anyok = True
                else:
                    noneok = True
                # Check ALL
                if len(intersection) == len(orgset):
                    allok = True
                # Check ONLY
                diff = currentorgs - orgset
                if len(diff) == 0:
                    onlyok = True
                # Check percent
                if pct_cutoff is not None and len(intersection) >= len(orgset) * pct_cutoff/100.0:
                    pctok = True

                # Our criteria: we can't have any of the options be TRUE and not have the corresponding condition also be true
                if not ( ( any_org and not anyok) or ( all_org and not allok) or (none_org and not noneok)
                         or (only_org and not onlyok) or (uniq_org and not uniqok) or ( use_pct_cutoff and not pctok) ):
                    goodClusters.append( (prevrun, previd) )

            # Reset
            uniqok = True
            currentorgs.clear()
            previd = l[1]
            prevrun = l[0]

        # Bugfix 07-05-13 - unique only has to apply to the ingroup (orgset)
        if l[2] in currentorgs and l[2] in orgset:
            uniqok = False

        # If an outgroup is specified and the organism isn't in either the ingroup or the outgroup,
        # don't include it in the analysis.
        if outgroup is not None:
            if l[2] not in outgroup and l[2] not in orgset:
                continue

        currentorgs.add(l[2])

    return goodClusters
