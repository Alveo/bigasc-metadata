'''
Created on Jul 19, 2013

@author: steve

gather together annotation files into an appropriate directory structure

'''

import configmanager
configmanager.configinit()
from convert.namespaces import DATA_URI_TEMPLATE, DATA_NS, generate_item_uri
from convert.item import parse_item_filename
from convert.participant import participant_uri, item_site_name
from convert.session import component_map
import ingest
from rdflib import Graph

import hashlib
import os
import shutil

def normalise_filename(filename, ext='.TextGrid'):
    """Given an annotation filename, return a path that we can 
    use to store it in the right place"""
    
    try:
        p = parse_item_filename(filename)

    
        p['site'] = item_site_name(participant_uri(p['colour'], p['animal']))
        
        m = component_map()
        p['componentName'] = m[int(p['component'])]
        
        p['item'] = int(p['item'])
        
        basename = "%(speaker)s_%(session)s_%(component)s_%(item)03d" % p
        p['filename'] = basename + ext
        
        return DATA_URI_TEMPLATE % p

    except:
        return ''


def md5hexdigest(filename):
    """Compute an md5 signature for the given file,
    return the signature as a Hex digest string.
    filename is an absolute filename."""

    # if there is no file here, return a dummy checksum
    if not os.path.exists(filename):
        return "missing file"
            
    md5 = hashlib.md5()
    with open(filename,'rb') as f:
        for chunk in iter(lambda: f.read(1024*md5.block_size), ''):
            md5.update(chunk)
    return md5.hexdigest()


def check_file_versions(files):
    """Given a list of files, check that they are all
    the same (via a checksum), return True if they are and
    False if not"""
    
    checksum = md5hexdigest(files[0])
    for f in files[1:]:
        cs = md5hexdigest(f)
        if cs != checksum:
            return False
    return True


def newest_file(files):
    """Given a list of filenames, return the one
    corresponding to the newest file"""
    
    newest = files[0]
    newest_s = os.stat(newest).st_mtime
    for f in files[1:]:
        s = os.stat(f).st_mtime
        if s > newest_s:
            newest = f
            newest_s = s
            
    return newest

def process_results(server, results, outdir, origin, format):
    
    for key in sorted(results.keys()):

        graph = ann_metadata(key, origin, format)
        server.output_graph(graph)
        
        source = newest_file(results[key])            
        copy_file(source, os.path.join(outdir, key))
        


def copy_file(src, dest):
    """Copy src to dest but make sure that the directories in dest exist"""
    
    if not os.path.exists(os.path.dirname(dest)):
        os.makedirs(os.path.dirname(dest))
    
    shutil.copy(src, dest)
    
    
def ann_metadata(annfile, origin, format):

    (path, ext) = os.path.splitext(annfile)

    ann_uri = DATA_NS[annfile]
    
    item_uri = generate_item_uri(path)
    
    graph = Graph()
    graph.add((URIRef(item_uri), NS['has_annotation'], ann_uri))
    graph.add((maus_uri, RDF.type, NS.AnnotationFile))
    graph.add((maus_uri, NS['origin'], Literal(origin)))
    graph.add((maus_uri, NS['format'], Literal(format)))
    
    return graph

if __name__ == '__main__':
    
    import sys, os
    
    if len(sys.argv) != 5:
        print "Usage: harvest_annotations.py <input dir> <ext> <output dir> <origin>"
        exit()
    
    dirname = sys.argv[1]
    ext = sys.argv[2]
    outdir = sys.argv[3]
    origin = sys.argv[4]
    
    server_url = configmanager.get_config("SESAME_SERVER")
    server = ingest.SesameServer(server_url)

    for dirpath, dirnames, filenames in os.walk(dirname):
        results = dict()
        for fn in filenames:
            if fn.find(ext) >= 0:
                newfn = normalise_filename(fn, ext)
                if newfn != '':
                    fullpath = os.path.join(dirpath, fn)
                    
                    if results.has_key(newfn):
                        results[newfn].append(fullpath)
                    else:
                        results[newfn] = [fullpath]
        process_results(server, results, outdir, origin, ext)
                    

            
            
            
                
                
                