#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Libraries needed
from __future__ import print_function
import fileinput, optparse
import os, sys, csv, getpass, socket, shutil, re

import Bio
from Bio import Entrez, SeqIO
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord
from Bio.Alphabet import generic_protein

from FileLocator import *
from GenbankHandler import *

RECOMMENDED_BIOPYTHON_VERSION = 1.61

'''
Produce an ITEP-compatible tab-delimited file ("raw file") from a Genbank file.

Standards enforced:
0: All organism IDs must match the regex \d+\.\d+
1: All raw files must be in the raw/ directory and named [organismid].txt
2: All genbank files must be in the genbank/ directory and named [organismid].gbk
3: All genbank files must have a corresponding raw file.
4: All raw files must have a corresponding genbank file.
5: If there are multiple genbank files (for multiple contigs) they should be concatinated and placed in the genbank folder as a single file with the name [organismid].gbk
6: The raw files must have a specific format (this is to be dealt with automatically if using standardized input functions):
    - Column order as specified in the help files.
    - Gene IDs are in the format fig\|\d+\.\d+\.peg\.\d+ where the first \d+\.\d+ is the organism ID of the corresponding genes
    - Strand must be + or -
    - "Start" is the nucleotide position of the first transcribed base (i.e. for - strand genes, the start position will be bigger than the stop).

Optionally we add the ITEP IDs to the genbank file, but if you want to do this you must
be prepared for the contig IDs to be truncated to 16 characters (due to Biopython limitations we
cannot write the genbank file if they are longer than this).
'''

def lookupStrainID(accession):
    #search NCBI for all IDs (the unique numerical key, not just accession)
    genbank = Entrez.read(Entrez.esearch(db="nucleotide", term=accession))
    IDlist = genbank['IdList']
    strainIDs=[]
    #there can me multiple records returned
    for thisID in IDlist:
        summaries = Entrez.read(Entrez.esummary(db="nucleotide", id=thisID))
        for s in summaries:
            strainIDs.append(s['TaxId'])
    strainIDs = list(set(strainIDs))
    assert len(strainIDs)==1, "Note: more than one ID returned from query of NCBI % s" % accession
    return strainIDs[0]

def info_from_genbank(gb_seqrec):
    info = {}
    # Not all Genbank files (i.e. those from RAST fall into this category) actually
    # assign the contig ID in the ID field but they call it a "name" instead...
    # Biopython automatically gives those an ID of "unknown".
    if gb_seqrec.id == "unknown":
        info["id"] = gb_seqrec.name
    else:
        info["id"] = gb_seqrec.id

    info["number_of_features"] = len(gb_seqrec.features)
    numcds = len([f for f in gb_seqrec.features if (f.type =='CDS')])
    info["number_of_cds"] = numcds

    if gb_seqrec.description:
        info["gb_description"] = gb_seqrec.description
    else:
        info["gb_description"] = "unknown"

    # The "try" part will only work for Entrez-derived GBK files but we want to be more
    # generic. If we can't find it from tehre we try to get it from the dbxref and if it fails there too
    # there's nothing we can do.
    sys.stderr.write("Attempting to query Entrez for the taxID...\n")
    try:
        info["gi"]= gb_seqrec.annotations['gi']
        if gb_seqrec.name:
            info["gb_name"] = gb_seqrec.name
        info["taxon"] = lookupStrainID(gb_seqrec.id)
    except:
        sys.stderr.write("Querying Entrez failed. Getting taxID from the genbank file...\n")
        for record in gb_seqrec.features:
            if record.type == "source":
                for xref in record.qualifiers["db_xref"]:
                    if "taxon" in xref:
                        taxid = re.search("(\d+)", xref).group(1)
                        info["taxon"] = taxid
                        break
            if "taxon" in info:
                break

    if "taxon" not in info:
        sys.stderr.write("ERROR: Could not identify taxonID from querying Entrez or from the Genbank file itself...\n")
        exit(2)

    if gb_seqrec.annotations:
        info.update([("gb_annotation: "+k,v) for k, v in list(gb_seqrec.annotations.items())])

    return info

def info_from_feature(feature):
    info = {}
    # An extra space in the amino acid sequences exists which 
    # throws off the validator and may cause downstream problems.
    info["aa_sequence"] = feature.qualifiers['translation'][0].strip()
    if "protein_id" in info:
        info["aliases"] = feature.qualifiers['protein_id'][0]
    else:
        info["aliases"] = ""
    if "product" in feature.qualifiers:
        info["function"] = feature.qualifiers['product'][0]
    else:
        info["function"] = "NO_FUNCTION_ASSIGNED"
    info["figfam"] = ""
    info["evidence_codes"] = ""
    if feature.type =='CDS':
        info["type"] = 'peg'
    #add this to preserve other types
    #info["type"] = feature.type
    #Must add one to biopython's 0 indexed to get the original genbank one indexed counting
    #However the stop is slice notation so it is already 1 higher than it "should" be.
    # Thus we only add 1 to the start.
    # I verified that this gives the correct answer relative to what is in the PubSEED
    # for some + and - strand genes in E. coli.
    try:
        info["start"] = int(feature.location.start) + 1
        info["stop"] = int(feature.location.end)
    except TypeError:
        # Old versions of Biopython use an access function instead of casting ExactLocation as an int.
        # This syntax is marked as obsolete and will probably go away in a future version of Biopython.
        info["start"] = feature.location.start.position + 1
        info["stop"] = feature.location.end.position
    except:
        raise

    if feature.strand == +1:
        info["strand"] = str("+")
    if feature.strand == -1:
        info["strand"] = str("-")
        # invert the start and stop locations...
        info["start"], info["stop"] = info["stop"], info["start"]
    return info

def info_from_record(record):
    info = {}
    info["nucleotide_sequence"] = str(record.seq)
    #info["Nucleotide ID"] = record.id
    #info["Nucleotide Description"] = record.description
    #if record.dbxrefs:
    #    info["Database cross-references"] = ";".join(record.dbxrefs)
    return info

def genbank_extract(ptr, version_number):
    '''Extract data from a genbank file...returns some organism-specific data,
    a dictionary from gene ID to a list of aliases to that gene ID (including the
    original IDs from the genbank file), and the data needed to build the raw data
    table required by ITEP.'''

    gb_seqrec_multi = SeqIO.parse(ptr, "genbank")

    #lists to store extracted seqs
    genes = []
    geneidToAlias = {}
    counter = 0

    match_SEED_xref = re.compile("SEED\:(fig\|\d+\.\d+\.peg\.\d+)")
    match_KEGG_xref = re.compile("KEGG\:.*?\+(.*)")
    # Have ITEP IDs been added previously?
    match_ITEP_xref = re.compile("ITEP\:(fig\|\d+\.\d+\.peg\.\d+)")

    # If we have a SEED or ITEP ID we want to get the version number out of that.
    get_version_number = re.compile("fig\|\d+\.(\d+)\.peg\.\d+")

    # These are used to help avoid colliding namespaces.
    seedConflictCheck = False
    itepConflictCheck = False

    orginfo = dict()
    cnt = 0
    for gb_seqrec in gb_seqrec_multi:
        orginfo = info_from_genbank(gb_seqrec)
        orginfo["net_version_number"] = version_number
        cnt += 1
        sys.stderr.write("Extracting data on features for genbank record number %d...\n" %(cnt))
        for feature in gb_seqrec.features:
            if feature.type =="CDS":
                #check there is only one translation and get info
                #TODO - Should we attempt to translate manually if no translations are preent in the gbk file?
                if 'translation' not in feature.qualifiers:
                    sys.stderr.write("WARNING: CDS found with no translation\n")
                    sys.stderr.write("Qualifiers:\n")
                    for key in feature.qualifiers:
                        sys.stderr.write("%s\t%s\n" %(key, feature.qualifiers[key]))
                    continue
                assert len(feature.qualifiers['translation'])==1
                counter += 1

                if ( counter % 100 == 0 ):
                    sys.stderr.write("Now working on feature number %d ... \n" %(counter))

                geneinfo = {}
                #get aa info
                geneinfo.update(info_from_feature(feature))
                #get na info
                record = feature.extract(gb_seqrec)
                geneinfo.update(info_from_record(record))

                # Handle supported xrefs: KEGG (locus tags by another name), SEED, and ITEP references
                aliases = []
                geneid = None
                if "db_xref" in feature.qualifiers:
                    for xref in feature.qualifiers["db_xref"]:
                        match = match_SEED_xref.match(xref)
                        if match is not None:
                            geneid = match.group(1)
                            seedConflictCheck = True
                            versionNumberMatch = get_version_number.match(geneid)
                            realVersionNumber = versionNumberMatch.group(1)
                            if realVersionNumber != version_number:
                                sys.stderr.write("WARNING: Version number %s from SEED ID will overwrite provided version number %s\n" %(realVersionNumber, version_number))
                                version_number = realVersionNumber
                                orginfo["net_version_number"] = realVersionNumber                                

                        match = match_ITEP_xref.match(xref)
                        if match is not None:
                            # If there is both an ITEP ID and a SEED ID they must match
                            if geneid is not None and geneid != match.group(1):
                                raise IOError("ERROR: ITEP ID did not match with SEED ID in provided Genbank file - this should never happen.")
                            geneid = match.group(1)
                            itepConflictCheck = True
                            versionNumberMatch = get_version_number.match(geneid)
                            realVersionNumber = versionNumberMatch.group(1)
                            if realVersionNumber != version_number:
                                sys.stderr.write("WARNING: Version number %s from ITEP ID will overwrite provided version number %s\n" %(realVersionNumber, version_number))
                                version_number = realVersionNumber
                                orginfo["net_version_number"] = realVersionNumber                                

                        match = match_ITEP_xref.match(xref)

                        # Note that one SEED gene can have more than one KEGG match (i.e. go with more than one locus tag).
                        # This is OK - I'll just capture all of them here.
                        match = match_KEGG_xref.match(xref)
                        if match is not None:
                            aliases.append(match.group(1))

                # If we got our genbank file from somewhere else (including from RAST) we need to just make an ID in the right format.
                if geneid is None:
                    # This flag is used to make sure that if we pull out ONE SEED ID then ALL of them have to be pulled out in the same manner.
                    # If this is not the case we will most likely get duplicated IDs which is BAD.
                    if seedConflictCheck:
                        raise IOError("ERROR: In order to avoid namespace collisions, if at least one gene has a PubSEED ID attached then ALL of them must.")
                    elif itepConflictCheck:
                        raise IOError("ERROR: In order to avoid namespace collisions, if at least one gene has an ITEP ID already attached then ALL of them must.")
                    else:
                        geneid = "fig|" + str(orginfo["taxon"]) + "." + str(version_number) + ".peg." + str(counter)
                        pass
                    pass

                geneinfo["feature_id"] = geneid
                geneinfo["contig_id"] = orginfo["id"]
                geneinfo["source_description"] = orginfo["gb_description"]

                if "protein_id" in feature.qualifiers:
                    geneinfo["location"] = feature.qualifiers["protein_id"][0]
                else:
                    geneinfo["location"] = ""

                genename = geneinfo["aliases"]
                genedesc = geneinfo["function"] + " " + orginfo["gb_description"]
                geneinfo["gene_description"] = genedesc               

                # Add locus tag and existing feature_id to list of aliases
                if "protein_id" in feature.qualifiers:
                    aliases.append(feature.qualifiers["protein_id"][0])
                if "locus_tag" in feature.qualifiers:
                    aliases.append(feature.qualifiers["locus_tag"][0])

                if "gene" in feature.qualifiers:
                    aliases.append(feature.qualifiers["gene"][0])
                geneidToAlias[geneid] = aliases
                genes.append(geneinfo)

    return orginfo, genes, geneidToAlias

#Entrez requires an email, if not set namually, this guesses one
email = None
guessemail = getpass.getuser() + '@' + socket.getfqdn()
if email == None:
    email = guessemail
Entrez.email = email

if __name__ == '__main__':
    usage="%prog [options] -g genbank_file"
    description='''    The purpose of this script is to take in a Genbank file (.gbk) 
    with multiple contig genbank files concatinated and 
    automatically organize three pieces of information required for input into ITEP:

    1: A genbank file with the coorrect name reflecting the taxID and a version number
    2: A tab-delimited file with the required format (see documentaion in the header of this file)
    3: An augmented aliases file containing locus tag and geneId information from the genbank file if available.

    You should NOT put your original genbank file in the $ROOT/genbank/ folder - instead put it somewhere else and call this
    script. This script will automatically reformat it and put the reformatted file into the /genbank/ folder.

    The genbank file is placed in $ROOT/genbank/, the tab-delimited file in $ROOT/raw/ and the aliases
    file is appended to any existing aliase file in the location $ROOT/aliases/aliases

    '''
    parser = optparse.OptionParser(usage=usage, description=description)
    parser.add_option("-g", "--genbank_file", help="Input genbank file concatinated across contigs (REQUIRED)", action="store", type="str", dest="genbank_file", default=None)
    parser.add_option("-o", "--org_file", help="(OPTIONAL) a file to which to dump organism data.", action="store", type="str", dest="org_file", default=None)
    parser.add_option("-r", "--replace", 
                      help="If specified, replaces old data related to the derived organism ID with the new data (D: Throws an error if an organism already is present with the derived organism ID)",
                      action="store_true", dest="replace", default=False)
    parser.add_option("-v", "--version_number", help="An integer used to distinguish between multiple genbank files with the same taxID (D:88888). This will become the second number in the organism ID",
                      action="store", type="int", dest="version_number", default=88888)
    (options, args) = parser.parse_args()
    
    if options.genbank_file is None:
        sys.stderr.write("ERROR: Genbank_file (-g) is a required argument\n")
        exit(2)

    rootdir = locateRootDirectory()
    gbk_dir = os.path.join(rootdir, "genbank")
    raw_dir = os.path.join(rootdir, "raw")

    # This should never happen but just in case it did, we will 
    if not os.path.exists(gbk_dir):
        sys.stderr.write("WARNING: Genbank output directory %s did not exist (it is part of the repo and should not be deleted). Attempting to create it...\n")
        os.makedirs(gbk_dir)
    if not os.path.exists(raw_dir):
        sys.stderr.write("WARNING: Raw file output directory %s did not exist (it is part of the repo and should not be deleted). Attempting to create it...\n")
        os.makedirs(raw_dir)

     # Extract data from the Genbank file
    orginfo, genes, aliases = genbank_extract(options.genbank_file, options.version_number)
    options.version_number = orginfo["net_version_number"]

    organism_id = str(orginfo["taxon"]) + "." + str(options.version_number)
    geneout_filename = os.path.join(rootdir, "raw", "%s.txt" %(organism_id))
    genbank_filename = os.path.join(rootdir, "genbank", "%s.gbk" %(organism_id))
    alias_filename = os.path.join(rootdir, "aliases", "aliases")

    # Try to prevent conflics between multiple organisms with the same taxID
    if os.path.exists(geneout_filename):
        if options.replace:
            # Note - to make this really robusst I should probably add a timestamp or something...
            bkgeneout_filename = os.path.join(rootdir, "%s.txt.bk" %(organism_id))
            sys.stderr.write("""WARNING: Backing up original gene output file %s to location %s in case something went wrong\n""" %(geneout_filename, bkgeneout_filename))
            shutil.copyfile(geneout_filename, bkgeneout_filename)
        else:
            sys.stderr.write("""ERROR: Gene output file %s already exists!
This could indicate a conflict in taxIDs between multiple organisms. Use -r to override this error and 
replace the existing file with a new one and remove the existing file, or use a different version number (-v)
if the genomes are really different.\n""" %(geneout_filename))
            exit(2)

    if os.path.exists(genbank_filename):
        if options.replace:
            # Note - to make this really robusst I should probably add a timestamp or something...
            bkgenbank_filename = os.path.join(rootdir, "%s.txt.bk" %(organism_id))
            sys.stderr.write("""WARNING: Backing up original gene output file %s to location %s in case something went wrong\n""" %(genbank_filename, bkgenbank_filename))
            shutil.copyfile(geneout_filename, bkgenbank_filename)
        else:
            sys.stderr.write("""ERROR: Genbank output file %s already exists!
This could indicate a conflict in taxIDs between multiple organisms. Use -r to override this error and 
replace the existing file with a new one and remove the existing file, or use a different version number (-v
if the genomes are really different.\n""" %(genbank_filename))
            exit(2)

    if os.path.exists(alias_filename):
        # Lets check to see if we can find our organism in the existing alias file
        bk_file = os.path.join(rootdir, "aliases", "aliases.bk")
        shutil.copyfile(alias_filename, bk_file)
        alias_ptr = open(alias_filename, "w")
        # The entire organism ID must match and we must avoid subsets.
        tosearch = "|" + organism_id + "."
        for line in open(bk_file, "r"):
            if tosearch in line:
                if not options.replace:
                    sys.stderr.write("""ERROR: Entries with organism ID %s already exist in the aliases file.
This could indicate a conflict in taxIDs between multiple organisms. Use -r to override this error and
replace the existing entries in the aliases file with new entries or use a different version number (v) if the
genomes are really different.""" %(organism_id))
                    alias_ptr.close()
                    os.rename(bk_file, alias_filename)
                    exit(2)
                else:
                    continue
            else:
                alias_ptr.write(line)
        alias_ptr.close()

    # Generate raw file.
    names = ["contig_id",          #from gi of gb file
             "feature_id",         #taxonID from NCBI lookup of accession, geneID from the db_xref GI in feature
             "type",               #CDS = peg
             "location",           #ignored by ITEP, source accession here
             "start",              #+1 index and rev if on neg strand
             "stop",               #+1 index and rev if on neg strand
             "strand",             #converted to + or -
             "function",           #from feature product
             "aliases",            #ignored by ITEP, from gene accession
             "figfam",             #ignored by ITEP, empty for all
             "evidence_codes",     #ignored by ITEP, empty for all
             "nucleotide_sequence",#as recorded in feature
             "aa_sequence"]        #as recorded in feature, not translated manually

    geneout_file = open(geneout_filename, 'w')
    geneout = csv.DictWriter(geneout_file, fieldnames = names, delimiter="\t")
        #geneout.writeheader()

    for gene in genes:
        geneout.writerow(dict([(n, gene[n]) for n in names]))
        pass

    geneout_file.close()
    sys.stderr.write("Text file saved as %s\n" % geneout_filename)

    # Now we need to write a new Genbank file.
    # We have to make a temporary one in order to work around biopython issues.
    
    tbl = [ line.strip("\r\n").split("\t") for line in open(geneout_filename, "r") ]
    multi_gbk_object = SeqIO.parse(options.genbank_file, "genbank")

    # Add the ITEP IDs - produces temporary IDs that we need to turn back into the originals
    gb_seqrec_id, newToOriginalName = addItepGeneIdsToGenbank(multi_gbk_object, tbl)

    # Save the resulting file with a temporary name
    import random
    tmp_fname = str(random.randint(0, 10)) + ".gbk"
    tmp_fid = open(tmp_fname, "w")
    SeqIO.write(gb_seqrec_id, tmp_fid, "genbank")
    tmp_fid.close()

    # Replace the temporary IDs with new IDs
    tmp_fid = open(tmp_fname, "r")
    fid = open(genbank_filename, "w")
    replaceTemporaryIdsWithOriginalIds(tmp_fid, newToOriginalName, fid)
    tmp_fid.close()
    fid.close()
    os.remove(tmp_fname)

    sys.stderr.write("Genbank file saved as %s\n" % genbank_filename)

    # IMPORTANT: Append, don't use "w" here (we don't want to blow away all the different organism entries...)
    alias_file = open(alias_filename, "a+")
    for geneid in aliases:
        for alias in aliases[geneid]:
            alias_file.write("%s\t%s\n" %(geneid, alias))
    alias_file.close()

    #Write out the organism data
    if options.org_file is not None:
        names = list(orginfo.keys())
        names.sort()
        orgout_file = open(options.orgout_file, "w")
        orgout = csv.DictWriter(orgout_file, fieldnames = names)
        orgout.writeheader()
        for org in orginfos:
            orgout.writerow(org)
        orgout_file.close()
