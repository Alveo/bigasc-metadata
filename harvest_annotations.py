'''
Created on Jul 19, 2013

@author: steve

gather together annotation files into an appropriate directory structure

'''

import configmanager
configmanager.configinit()
from convert.namespaces import DATA_URI_TEMPLATE
from convert.item import parse_item_filename
from convert.participant import participant_uri, item_site_name
from convert.session import component_map

import hashlib
import os
import shutil

def normalise_filename(filename, ext='.TextGrid'):
    """Given an annotation filename, return a path that we can 
    use to store it in the right place"""
    
    
    p = parse_item_filename(filename)
    p['site'] = item_site_name(participant_uri(p['colour'], p['animal']))
    
    m = component_map()
    p['componentName'] = m[int(p['component'])]
    
    p['item'] = int(p['item'])
    
    basename = "%(speaker)s_%(session)s_%(component)s_%(item)03d" % p
    p['filename'] = basename + ext
    
    return DATA_URI_TEMPLATE % p


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

def process_results(results, outdir):
    

    for key in sorted(results.keys()):
        if len(results[key]) > 1:
            if check_file_versions(results[key]):
                copy_file(results[key][0], os.path.join(outdir, key))
            else:
                print "Files Differ:"
                for f in results[key]:
                    print "\t", f
        else:
            copy_file(results[key][0], os.path.join(outdir, key))

def copy_file(src, dest):
    """Copy src to dest but make sure that the directories in dest exist"""
    
    if not os.path.exists(os.path.dirname(dest)):
        os.makedirs(os.path.dirname(dest))
    
    shutil.copy(src, dest)
    
    


if __name__ == '__main__':
    
    import sys, os
    
    dirname = sys.argv[1]
    ext = sys.argv[2]
    outdir = sys.argv[3]
    
    
    
    for dirpath, dirnames, filenames in os.walk(dirname):
        results = dict()
        for fn in filenames:
            if fn.find(ext) >= 0:
                newfn = normalise_filename(fn, ext)
                fullpath = os.path.join(dirpath, fn)
                
                if results.has_key(newfn):
                    results[newfn].append(fullpath)
                else:
                    results[newfn] = [fullpath]
        process_results(results, outdir)
                    

            
            
            
                
                
                