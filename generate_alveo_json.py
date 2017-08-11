'''
Created on 7 Sep 2016

@author: Michael
'''

import os,re,json,shutil,glob,sys
from rdflib import Graph,Namespace,Literal,URIRef #UnresolvedImport
from __builtin__ import str
import argparse
import time
import configmanager
configmanager.configinit()

DEFAULT_CHUNK_SIZE = 5000
ITEM_PREFIX = 'http://app.alveo.edu.au/catalog/austalk/'

FILES_FILE_SUFFIX = "-files"
DOWNSAMPLED_FILE_SUFFIX = "-ds"
METADATA_FILE_SUFFIX = "-metadata"

ALVEO = Namespace(u"http://alveo.edu.au/vocabulary/")

CATALOG = u'austalk'

# log file for missing files
MISSING_LOG = 'missing.dat'

#Create context stuffs, I'm assuming contexts are constant
ITEM_CONTEXT = {
            "dcterms": "http://purl.org/dc/terms/",
            "austalk": "http://ns.austalk.edu.au/",
            "olac": "http://www.language-archives.org/OLAC/1.1/",
            "ausnc": "http://ns.ausnc.org.au/schemas/ausnc_md_model/",
            "foaf": "http://xmlns.com/foaf/0.1/",
            "alveo": "http://alveo.edu.au/vocabulary/",
            "austalkid":"http://id.austalk.edu.au/",
            "rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#",
            "ausnc:document": {"@type": "@id"},
            "alveo:display_document": {"@type": "@id"},
            "alveo:indexable_document": {"@type": "@id"},
            "austalk:speech_style": {"@type": "@id"},
            "austalk:information_giver": {"@type": "@id"},
            "austalk:component": {"@type": "@id"},
            "austalk:prototype": {"@type": "@id"},
            "austalk:map": {"@type": "@id"},
            "olac:speaker": {"@type": "@id"},
            "austalk:information_follower": {"@type": "@id"}
           }

SPEAKER_CONTEXT = {
            "dc": "http://purl.org/dc/terms/",
            "austalk": "http://ns.austalk.edu.au/",
            "olac": "http://www.language-archives.org/OLAC/1.1/",
            "ausnc": "http://ns.ausnc.org.au/schemas/ausnc_md_model/",
            "foaf": "http://xmlns.com/foaf/0.1/",
            "alveo": "http://alveo.edu.au/vocabulary/",
            "austalkid":"http://id.austalk.edu.au/",
            "rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#",

            "dcterms:isPartOf":  {"@type": "@id"},
            "austalk:birthPlace": {"@type": "@id"},
            "austalk:father_birthPlace": {"@type": "@id"},
            "austalk:mother_birthPlace": {"@type": "@id"},
            "austalk:residential_history": {"@type": "@id"},
            "austalk:first_language": {"@type": "@id"},
            "austalk:father_first_language": {"@type": "@id"},
            "austalk:mother_first_language": {"@type": "@id"},
            "austalk:recording_site": {"@type": "@id"},
            "austalk:language_usage": {"@type": "@id"},
            "olac:recorder": {"@type": "@id"}
           }


SPEAKERS_TO_NOT_PROCESS = ['1_1027',
        '1_1035','1_1056','1_1077','1_1092',
        '1_1182','1_1258','1_1263','1_179',
        '1_280','1_360','1_431','1_553',
        '1_558','1_682','1_781','1_951',
        '1_959','1_997','2_1033','2_1223',
        '2_1334','2_451','2_560','2_653',
        '2_677','2_888','2_91','2_961',
        '3_1005','3_102','3_1189','3_1309',
        '3_136','3_322','3_347','3_431',
        '3_443','3_579','3_707','3_736',
        '3_751','3_862','3_949','4_1003',
        '4_1028','4_1049','4_1061','4_1299',
        '4_17','4_175','4_384','4_508',
        '4_595','4_732','4_734','4_842',
        '4_964']

def get_files(srcdir, item_pattern=''):
    ''' This function generates a sequence of files that
    the Austalk ingest should actually process
    Note this is a generator (using yield)'''

    res = []
    src_depth = len(srcdir.split(os.path.sep))
    for root, dirnames, filenames in os.walk(srcdir):
        for filename in filenames:
            spkr = '_'.join(filename.split('.')[0].split('_')[:2])
            if spkr not in SPEAKERS_TO_NOT_PROCESS:
                if re.match(item_pattern, filename):
                    res.append(os.path.join(root, filename))

                    if len(res)>=DEFAULT_CHUNK_SIZE:
                        yield res
                        res = []

    if len(res)>0:
        yield res

def get_item_files(srcdir):
    ''' This function generates a sequence of files that
    the Austalk ingest should actually process
    Note this is a generator (using yield)'''

    item_pattern = ".*-files\..*"
    return get_files(os.path.join(srcdir, 'metadata'), item_pattern)


def get_speaker_files(srcdir):
    ''' This function generates a sequence of files that
    the Austalk ingest should actually process
    Note this is a generator (using yield)'''

    for d in ('participants', 'protocol'):
        for i in get_files(os.path.join(srcdir, 'metadata', d), ''):
            yield i


def clear_output(outdir):
    ''' Clears the output file '''
    if os.path.exists(outdir):
        shutil.rmtree(outdir)
    os.mkdir(outdir)

def identify_display_document(graph):
    """Find the ch6-speaker16 document for this item and mark it as the
    display document by adding a triple to the graph"""

    for s, o in graph.subject_objects(URIRef("http://ns.ausnc.org.au/schemas/ausnc_md_model/document")):
        if "ch6-speaker16" in o:
            graph.add((s, ALVEO.display_document, o))

def files_to_graphs(files):
    '''Generate RDF graphs for a list of RDF files'''
    graphs = []
    count = 0
    for filename in files:
        g = Graph()
        g.parse(filename, format=configmanager.get_config('RDF_GRAPH_FORMAT') )

        (basename, ext) = os.path.splitext(filename)
        graphs.append((g,basename.split(os.sep)[-1]))

        count += 1

    return graphs

def log_missing(filename):

    with open(MISSING_LOG, 'a') as out:
        out.write(str(time.asctime()) + ": " + filename+'\n')


def item_files_to_graphs(files):
    ''' Generate RDF graphs for a list of item -files.nt files
    this needs to look for other associated files and group them all
    together. '''
    graphs = []
    count = 0
    for filename in files:
        item_metadata = filename.replace(FILES_FILE_SUFFIX, "")
        downsampled_doc = filename.replace(FILES_FILE_SUFFIX, DOWNSAMPLED_FILE_SUFFIX)

        if not os.path.exists(item_metadata) or not os.path.exists(downsampled_doc):
            log_missing(item_metadata)
            continue

        g = Graph()

        # concatenate all metadata files
        (basename, ext) = os.path.splitext(item_metadata)
        itemfiles = glob.glob(basename + "*")

        for filename in itemfiles:
            g.parse(filename, format=configmanager.get_config('RDF_GRAPH_FORMAT'))

        # determine which document will be the display document
        identify_display_document(g)

        graphs.append((g,basename.split(os.sep)[-1]))

        count += 1

    return graphs

def fix_context(predicate, object, CONTEXT=ITEM_CONTEXT):

    return (prefix(predicate, CONTEXT), prefix(object, CONTEXT))


# memoize this function
prefix_m = dict()

def prefix(uri_or_literal, context):

    global prefix_m

    if uri_or_literal in prefix_m:
        return prefix_m[uri_or_literal]

    result = uri_or_literal

    if type(uri_or_literal) == Literal or uri_or_literal.startswith('http://data.austalk.edu.au'):
        # don't cache literals or data URIs
        return uri_or_literal
    else:
        for key, val in context.items():
            if type(val) == str and str(uri_or_literal).startswith(val):
                result = uri_or_literal.replace(val, key+":",1)
                break
    prefix_m[uri_or_literal] = result

    return result

def graph_speakers_to_json(graphs, indent=False):
    ''' Process an rdf graph into a JSON-ND file '''
    result = {'items':[]}
    for graph,itemName in graphs:
        #put all metadata here, remember ausnc:document is a list
        #and will count towards the ausnc:document sibling of metadata

        item = {"@context":[SPEAKER_CONTEXT],'@graph':[],'alveo:metadata':{'dcterms:isPartOf':CATALOG},'ausnc:document':[]}

        for subject in graph.subjects():
            meta = graph_subject_to_json(graph, subject)
            item['@graph'].append(meta)

        result['items'].append(item)

    return json.dumps(result, indent=indent)

def graph_subject_to_json(graph, subject):

    meta = {}
    data = graph.triples((URIRef(subject), None, None))
    for s, p,o in data:
        p,o = fix_context(p, o)
        if type(o) == Literal and o.datatype == URIRef(u'http://www.w3.org/2001/XMLSchema#integer'):
            meta[p] = int(o)
        else:
            meta[p] = o

    # set the subject
    meta['@id'] = subject

    if 'rdf:type' in meta:
        meta['@type'] = meta['rdf:type']
        meta.pop('rdf:type')
        if meta['@type'] == 'foaf:Person':
            meta['@id'] = subject

    elif 'protocol' in subject:
        #  Item in the protocol doesn't have a type
        meta['@type'] = 'austalk:Item'

    # special case for empty comments
    if 'austalk:comment' in meta and meta['austalk:comment'] == '':
        meta.pop('austalk:comment')

    return meta


def document_uri(doc):
    """Generate a URI for a document"""

    # now it should be correct already
    return doc


def graph_items_to_json(src_dir, graphs, indent=None):
    ''' Process an rdf graph into a JSON-ND file '''
    result = {'items':[]}

    for graph,itemName in graphs:
        #put all metadata here, remember ausnc:document is a list
        #and will count towards the ausnc:document sibling of metadata
        metadata = {}
        item = {"@context":[ITEM_CONTEXT],'@graph':[],'alveo:metadata':{},'ausnc:document':[]}

        metadata['@id'] = ITEM_PREFIX+itemName
        metadata['dcterms:isPartOf'] = CATALOG
        metadata['ausnc:document'] = []

        documents = []

        itemURI = URIRef(ITEM_PREFIX+itemName)
        subjects_processed = [itemURI]


        res = graph.predicate_objects(itemURI)

        for predicate,object in res:

            predicate, object = fix_context(predicate,object)

            #ausnc:document is special and needs to be a list
            if predicate=='ausnc:document':
                metadata['ausnc:document'].append(document_uri(object))
                documents.append(object)
            elif predicate=='alveo:display_document':
                #if we change the @id for documents we need to change this
                metadata[predicate] = document_uri(object)
            elif predicate=='rdf:type':
                metadata['@type'] = object
            else:
                metadata[predicate] = object

            #This needs to just be 'austalk' not austalkid:component...etc
            if predicate=='dcterms:isPartOf':

                metadata['dcterms:isPartOf'] = CATALOG

        item['alveo:metadata'] = metadata

        #Add documents
        for doc in documents:
            docmeta = {}

            res = graph.predicate_objects(URIRef(doc))

            subjects_processed.append(URIRef(doc))

            docmeta['@id'] = doc

            for predicate,object in res:

                predicate,object = fix_context(predicate,object)

                if predicate=='rdf:type':
                    docmeta['@type'] = object
                elif type(object) == Literal and object.datatype == URIRef(u'http://www.w3.org/2001/XMLSchema#integer'):
                    docmeta[predicate] = int(object)
                elif predicate=='dcterms:source':
                    docmeta[predicate] = os.path.join(src_dir, object)
                    if not os.path.exists(docmeta[predicate]):
                        log_missing(docmeta[predicate])
                else:
                    docmeta[predicate] = object

            item['ausnc:document'].append(docmeta)

        # mop up any extra subjects (eg. recordedsession)
        for subject in graph.subjects():
            if not subject in subjects_processed:
                subjects_processed.append(subject)
                meta = graph_subject_to_json(graph, subject)
                item['@graph'].append(meta)

        result['items'].append(item)

    return json.dumps(result, indent=indent)

def process_speakers(src_dir, output_dir, indent=None):

    start_time = time.time()
    tally = 0
    count = 0
    for files in get_speaker_files(src_dir):
        #get all the .nt files and process them into graphs
        graphs = files_to_graphs(files)
        tally += len(graphs)
        #write out the graph into a json format
        json_string = graph_speakers_to_json(graphs, indent=indent)

        #Open up the destination JSON file and write json output
        with open(os.path.join(output_dir, "speaker-%d.json" % count),"w") as out_json:
            out_json.write(json_string)
        count += 1

    print "Processed %d speaker files in %s" % (tally, time.time()-start_time)


def process_items(src_dir, output_dir, limit, indent=None):

    start_time = time.time()
    tally = 0
    count = 0
    for files in get_item_files(src_dir):
        #get all the .nt files and process them into a graph
        graphs = item_files_to_graphs(files)
        tally += len(graphs)
        #write out the graph into a json format
        json_string = graph_items_to_json(src_dir, graphs, indent=indent)

        #Open up the destination JSON file and write json output
        with open(os.path.join(output_dir, "items-%d.json" % count),"w") as out_json:
            out_json.write(json_string)

        count += 1

        if count >= limit:
            break

    print "Processed %d items in %s" % (tally, time.time()-start_time)

def parser():
    parser = argparse.ArgumentParser(description="Process Austalk RDF Files for Alveo ingest")
    parser.add_argument('--items', required=False, action="store_const", const=True, default=False, help="process items")
    parser.add_argument('--speakers', required=False, action="store_const", const=True, default=False, help="process speakers")
    parser.add_argument('--all', required=False, action="store_const", const=True, default=False, help="process everything")
    parser.add_argument('--indent', required=False, action="store_const", const=2, default=None, help="indent JSON")
    parser.add_argument('--clear', required=False, action="store_const", const=True, default=False, help="remove previous JSON output")
    parser.add_argument('--output_dir', required=True, action="store", type=str, help="Output Directory")
    parser.add_argument('--input_dir', required=False, action="store", type=str, help="Input Directory (default to output of RDF generation)")
    parser.add_argument('--limit', required=False, action="store", type=int, default=10000, help="Max Items to process")
    return parser.parse_args()


if __name__ == '__main__':

    args = parser()

    if not args.all and not args.speakers and not args.items:
        print "one of --all, --items or --speakers is required"
        exit()

    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)

    if args.clear:
        print "Clearing old JSON"
        clear_output(args.output_dir)

    # out input is the output of the other steps unless overridden
    if args.input_dir:
        inputdir = args.input_dir
    else:
        inputdir = configmanager.get_config('OUTPUT_DIR')

    if args.speakers or args.all:
        process_speakers(inputdir, args.output_dir, indent=args.indent)
    if args.items or args.all:
        process_items(inputdir, args.output_dir, limit=args.limit, indent=args.indent)

    print "Finished, Exiting Program"
