#!/usr/bin/env python

from __future__ import print_function
import json
import re
import sys

# This is from the lib/ directory of this repo
from sanitizeString import *

# These are from Biopython
from Bio import SeqIO
from Bio.Alphabet import IUPAC
from Bio.SeqFeature import SeqFeature, FeatureLocation
from Bio.SeqRecord import SeqRecord
from Bio.Seq import Seq

def strip_control_characters(input):  
    '''Taken from http://chase-seibert.github.com/blog/2011/05/20/stripping-control-characters-in-python.html'''
    if input:  
        # unicode invalid characters  
        RE_XML_ILLEGAL = '([\u0000-\u0008\u000b-\u000c\u000e-\u001f\ufffe-\uffff])' + '|' + '([%s-%s][^%s-%s])|([^%s-%s][%s-%s])|([%s-%s]$)|(^[%s-%s])' % (chr(0xd800),chr(0xdbff),chr(0xdc00),chr(0xdfff), chr(0xd800),chr(0xdbff),chr(0xdc00),chr(0xdfff), chr(0xd800),chr(0xdbff),chr(0xdc00),chr(0xdfff) )
        input = re.sub(RE_XML_ILLEGAL, "", input)  
        # ascii control characters  
        input = re.sub(r"[\x01-\x1F\x7F]", "", input)              
    return input

def getFieldFromRelationship(seedRelationship, fieldName, objtype):
    '''
    INPUTS:
    seedRelationship: The result of one of the get_relationship_xxx functions
    fieldName: The field you want to extract from the object.
    objtype: "TO", "REL", or "FROM"

    OUTPUTS:
    A list (in the same order as the list from the get_relationship function)
    of the values with the specified field name.

    The get_relationship_xxx functions return lists of lists.
    The first list is a list of all the links
    The second list has three dictionaries in it: the TO dictionary, the REL dictionary and the FROM dictionary
    describing properties on either end of the link and of the link itself...

    If you want to  maintain duplicicate relationships (many-to-one, one-to-many, many-to-many), this function should be called at
    least twice (once on each end of the relationship, or once on an end and once in the middle)..
    '''
    if seedRelationship is None:
        sys.stderr.write("INTERNAL ERROR: The provided relationship was None - usually this means you were searching for something that doesn't exist in the database.\n")
        raise ValueError
    objidx = None
    if objtype.lower() == "from":
        objidx = 0
    elif objtype.lower() == "rel":
        objidx = 1
    elif objtype.lower() == "to":
        objidx = 2
    else:
        sys.stderr.write("INTERNAL ERROR: In getFieldFromRelationship - objtype must be TO, REL, or FROM\n")
        raise ValueError
    if not isinstance(seedRelationship, list):
        sys.stderr.write("INTERNAL ERROR: getFieldFromRelationship expects a list - perhaps you meant to call getFieldFromEntity?\n")
        raise ValueError
    # Unravel
    f = []
    for entry in seedRelationship:
        # TO CHECK: Is it possible to have one of the links lead to nothing?
        # Check field name validity - if it links to something there has to be the data request there
        # or else something is wrong.
        if fieldName not in entry[objidx]:
            sys.stderr.write("INTERNAL ERROR: Field name %s not found in provided relationship\n" %(fieldName))
            raise ValueError
        f.append(entry[objidx][fieldName])
    return f

def kbaseGenomeToGenbank(genome_object, taxid=None):
    '''Convert a KBase genome object into a Genbank file incorporating as much info as we can
    as found in the NCBI genbank files.

    Note - the genome object (not to be confused with a ModelSEED "annotation" object) has both annotations / translations
    AND the DNA sequence. It's obtained by calling annotate_genome on an object that only has the DNA sequence.

    Hopefully they won't change this otherwise I'll have to do more cross-referencing and ask for two files. Sigh...'''

    organism_name = genome_object["scientific_name"]
    organism_domain = genome_object["domain"]
    organism_id = genome_object["id"]
    organism_genetic_code = genome_object["genetic_code"]

    # Get the TaxID
    # If none is specified the user has to provide one (or at least some unique integer, not necessarily a tax ID) for this system to work right.
    if taxid is None:
        # CDMI.py is from the KBase - we need it to get the Taxon ID
        # Download it at http://kbase.science.energy.gov/developer-zone/downloads/
        try:
            from CDMI import CDMI_EntityAPI
        except ImportError:
            sys.stderr.write("ERROR: If no TaxID is provided, the CDMI.py file is necessary (http://kbase.science.energy.gov/developer-zone/downloads/) to attempt to guess it.\n")
            exit(2)
        URL="https://www.kbase.us/services/cdmi_api/"
        cdmi_entity = CDMI_EntityAPI(URL)
        reldict = cdmi_entity.get_relationship_IsInTaxa(organism_id, [], [], ["id"])
        if reldict is None:
            sys.stderr.write("ERROR: TaxID for Organism ID %s not found in the KBase CDMI. You will need to specify it manually if you want it\n" %(organism_id))
            exit(2)
        else:
            taxidlist = getFieldFromRelationship(reldict, "id", "to")
            taxid = taxidlist[0]

    annotations = { 'source': organism_name, 'organism': organism_name }

    # Specify contig data and "source" features for each contig (required by the genbank standard)
    contig_to_sequence = {}
    contig_to_feature_data = {}
    for contig in genome_object["contigs"]:
        contig_to_sequence[contig["id"]] = contig["dna"]
        qualifiers = {}
        qualifiers["organism"] = organism_name
        qualifiers["mol_type"] = "Genomic DNA"
        if taxid is not None:
            qualifiers["db_xref"] = "taxon:%s" %(taxid)
        feature = SeqFeature(FeatureLocation(0, len(contig["dna"])), strand=1, type="source", qualifiers=qualifiers)
        contig_to_feature_data[contig["id"]] = [ feature ]

    # The contig references are inside the feature definitions in the Genome object file, but
    # in a genbank file the features in a contig must all be separated.
    # Therefore I have to keep track of them in one step and then create the SeqRecord objects
    # in a separate step.
    for feature in genome_object["features"]:
        # FIXME - What do I do with things that have more than one location?
        assert(len(feature["location"]) == 1)

        # First lets Deal with start and stop locations...
        # I verified against Pubseed that these semantics and calcualtions are correct, at least
        # for the proteins I checked that are the same between pubseed and KBase...
        loc = feature["location"][0]
        contig = loc[0]
        start = int(loc[1])
        strandstr = loc[2]
        if strandstr == "-":
            strand = -1
        else:
            strand = 1
        featurelen = loc[3]
        if strand == -1:
            stop = start - featurelen + 1
        else:
            stop = start + featurelen - 1
        # Now I need to convert these into Python slicing indexes...because that is what FeatureLocation wants.
        # This includes making the start always less than stop and offsetting the stop by 1 because slide [a,b] only goes up to position b-1
        seqstart = min(start, stop) - 1
        seqstop = max(start, stop)

        feature_id = feature["id"]
        feature_type = feature["type"]

        qualifiers = {}
        # Unfortunately there are features including proteins in the genome objects that have no function (not even "hypothetical protein")
        # Thankfully this isn't a required field in the Genbank file
        if "function" in feature:
            qualifiers["product"] = strip_control_characters(feature["function"])
        if feature_type == "CDS" or feature_type == "peg":
            qualifiers["protein_id"] = feature_id
            qualifiers["translation"] = feature["protein_translation"]

        # "RNA" is not an official type in a GENBANK file.
        # We attempt to figure out based on the annotation whether it is a tRNA, rRNA, or other (misc_RNA) RNA.
        # These are the offiial RNA types (aside from mRNA but those don't have special fields in the Genome object)
        if feature_type == "rna":
            rRNA_finders = [ "rRNA", "ribosomal", "5S", "16S", "23S", "5.8S", "28S", "18S" ]
            tRNA_finders = [ "tRNA", "transfer" ]
            for finder in rRNA_finders:
                if finder in feature["function"]:
                    feature_type = "rRNA"
            for finder in tRNA_finders:
                if finder in feature["function"]:
                    feature_type = "tRNA"
            if feature_type == "rna":
                feature_type = "misc_RNA"

        # I checked that the above formulas give the correct positions in the genbank file (or at least, the same as the PubSEED genabnk files).
        feature = SeqFeature(FeatureLocation(seqstart, seqstop), strand=strand, type=feature_type, id=feature_id, qualifiers=qualifiers)

        # Attach the new features to the appropriate contig...
        if contig in contig_to_feature_data:
            contig_to_feature_data[contig].append(feature)
        else:
            contig_to_feature_data[contig] = [ feature ]

    # Create one record for each contig
    records = []
    for contig in contig_to_feature_data:
        seq = Seq(contig_to_sequence[contig], IUPAC.ambiguous_dna)
        record = SeqRecord(seq, id=sanitizeString(contig, False), description = "%s contig %s" %(organism_name, contig), name=contig, features=contig_to_feature_data[contig], annotations=annotations)
        records.append(record)
    SeqIO.write(records, sys.stdout, "genbank")

    return

if __name__ == '__main__':

    import json
    import optparse

    usage = "%prog [Genome_object] > Concatinated_genbank_file"
    description = '''Converts a KBase genome JSON object into a genbank file (each contig gets its own file and then they are concatinated)'''
    parser = optparse.OptionParser(usage=usage, description=description)
    parser.add_option("-t", "--taxid", help="Taxonomy ID for genome to add to organism (D: Attepmt to look it up but if it fails you will need to specify one)",
                      action="store", type="int", dest="taxid", default=None)
    (options, args) = parser.parse_args()
    if len(args) < 1:
        sys.stderr.write("ERROR: The JSON genome object is a required argument...\n")
        exit(2)

    # The strict=FALSE is necessary because I had issues saving the JSON files from IRIS
    # without invalid control characters being put in by firefox(??)
    genome_object = json.load(open(args[0], "r"), strict=False)
    kbaseGenomeToGenbank(genome_object, taxid=options.taxid)
