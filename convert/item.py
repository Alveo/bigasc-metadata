'''
Created on Sep 14, 2012

@author: steve

Convert item level metadata to RDF
'''
from xml.etree import ElementTree
from rdflib import Literal
import os, urllib2, re

import map
from namespaces import *
from session import component_map
from participant import participant_uri


def parse_item_filename(filename):
    """Get the session, component and item ids
    from the file name, return a dictionary with keys 'session', 'component', 'item'"""

    import re
    result = dict()
    parse_it = re.compile(r'^(\d*)_(\d*)_(\d*)_(\d*)_(\d*)')
    match = parse_it.search(filename)
    if match:
        groups = match.groups() 
        result['session']   = groups[2]
        result['component'] = groups[3]
        result['item']      = str(int(groups[4]))  # do this to trim leading zeros
    else:
        print filename, "doesn't match the filename pattern"
    return result



class ItemMapper:
    
    def __init__(self, server):
        """Initialise an item mapper with a SesameServer instance"""
        
        self.server = server
        self.init_map()
        self.component_map = component_map()

    
    def init_map(self):
        """Initialise the RDF map"""
        
        self.itemmap = map.FieldMapper()
        self.itemmap.add("path", ignore=True)
        self.itemmap.add('colour', ignore=True)
        self.itemmap.add('animal', ignore=True)
        self.itemmap.add('item', ignore=True) # will be replaced with a link to item
        self.itemmap.add('participant', ignore=True) # will replace with pointer to participant
        self.itemmap.add('component', mapper=self.map_component)
        self.itemmap.add('files', mapper=self.map_files)
        self.itemmap.add('session', mapper=self.map_session)
    
    
    
    def item_site_name(self, spkruri):
        """Given a speaker URI, return the short name of the
        the recording site for inclusion in the file path"""
        
        q = """
PREFIX austalk: <http://ns.austalk.edu.au/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

select ?name where {
    <%s>  austalk:recording_site ?site .
    ?site rdfs:label ?name .
}""" % spkruri
     
        result = self.server.query(q)
        bindings = result['results']['bindings']
         
        if len(bindings) > 0:
            name = bindings[0]['name']['value']
        else:
            name = "UNKNOWN"
            
        # set an instance variable so that map_files can use this
        self.site_name = name
        
        return name
            
    
    def media_uri(self, itemuri, filename):
        """Given a filename, return a URI for
        this file on the data server"""
        
    
        info = parse_item_filename(filename)
        info['filename'] = filename
        info['component'] = self.component_map[int(info['component'])]
        # here we reference the 'current' site name which
        # was generated in item_rdf
        info['site'] = self.site_name
        #info['component'] = component_map[info['component']]
        path = DATA_URI_TEMPLATE % info
        
        return DATA_NS[path]
        
        
    def map_files(self, subj, prop, value):
        """Map the file list
        we create 'media' entities for each file
        and attach various properties to them"""
        
        result = []
        for filename in value.keys():
            
            m_uri = self.media_uri(subj, filename)
            result.append((subj, NS.media, m_uri))
            # add file properties
            result.append((m_uri, RDF.type, NS.MediaFile))
            for prop in ['version', 'checksum', 'type', 'channel']:
                result.append((m_uri, NS[prop], Literal(value[filename][prop]))) 
        
        return result    
    
        
        
    def map_component(self, subj, prop, value):
        """Map the component field to point to the 
        appropriate component URI"""
        
        cid = PROTOCOL_NS[COMPONENT_URI_TEMPLATE % value]
        
        return [(subj, NS.component, cid)]
    
    def map_session(self, subj, prop, value):
        """Map the session field to point to the 
        appropriate session URI"""
        
        # fold 3/4
        if value == "4":
            value = "3"
    
        sid = PROTOCOL_NS[SESSION_URI_TEMPLATE % value]
        
        return [(subj, NS.session, sid)]
    
    
    def item_rdf(self, url):
        """Given the url of an item xml file, read the metadata and map
        to RDF, returning a graph
    
    >>> import sys
    >>> sys.path.append("..")
    >>> from ingest import SesameServer
    >>> mdurl = "https://austalk.edu.au/dav/bigasc/data/real/Australian_National_University,_Canberra/Spkr1_178/Spkr1_178_Session2/Session2_16/1_178_2_16_001.xml"
    >>> serverurl = "http://115.146.94.199/openrdf-sesame/repositories/bigasc"
    >>> server = SesameServer(serverurl)
    >>> im = ItemMapper(server)
    >>> graph = im.item_rdf(mdurl)
    
    >>> print graph.serialize(format='turtle')
    # need to test some properties of the graph
        
        """
        
        md = read_metadata(url)
        
        item_uri = NS[md['basename']]
        # generate participant uri and from that query the
        # remote db for the site name which we'll use
        # later in mapping file names to uris
        
        self.participant_uri = participant_uri(md['colour'], md['animal'])
        self.item_site_name(self.participant_uri)
        
        graph = self.itemmap.mapdict(item_uri, md)
        
        # add link to participant

        graph.add((item_uri, OLAC.speaker, self.participant_uri))
        graph.add((item_uri, RDF.type, AUSNC.AusNCObject))
        
        # add link to item prototype
        iid = PROTOCOL_NS[ITEM_URI_TEMPLATE % (md['component'], md['item'])]
        graph.add((item_uri, NS.item, iid))
        
        # add some namespaces to make output prettier
        graph.bind('austalk', NS)
        graph.bind('olac', OLAC)
        graph.bind('ausnc', AUSNC)
        graph.bind('rdf', RDF)
        
        return graph


def read_metadata(url):
    """Read item metadata from the given url
    return a dictionary of values
    
>>> mdfile = "../test/1_1121_1_12_001.xml"
>>> read_metadata(mdfile)
{'files': {'1_1121_1_12_001-ch6-speaker.wav': {'checksum': 'e0012015d6babdce61cb553939d87792', 'version': 1, 'type': 'audio', 'channel': 'ch6-speaker', 'filename': '1_1121_1_12_001-ch6-speaker.wav'}, '1_1121_1_12_001-ch1-maptask.wav': {'checksum': '3a1ac90a5a3940ac1cb9046d5546b574', 'version': 1, 'type': 'audio', 'channel': 'ch1-maptask', 'filename': '1_1121_1_12_001-ch1-maptask.wav'}, '1_1121_1_12_001-ch4-c2Left.wav': {'checksum': 'db028ab9647fe0e04377f338451ed53a', 'version': 1, 'type': 'audio', 'channel': 'ch4-c2Left', 'filename': '1_1121_1_12_001-ch4-c2Left.wav'}, '1_1121_1_12_001-ch5-c2Right.wav': {'checksum': '630d4d53a57e9f5ae01c6d764d8f169a', 'version': 1, 'type': 'audio', 'channel': 'ch5-c2Right', 'filename': '1_1121_1_12_001-ch5-c2Right.wav'}, '1_1121_1_12_001-camera-0.raw16': {'checksum': '6065f4a33f4008b592a1f6d178bea5fb', 'version': 1, 'type': 'unknown', 'channel': 'camera-0', 'filename': '1_1121_1_12_001-camera-0.raw16'}}, 'participant': "Gold-Blainville's Beaked Whale", 'cameraSN1': '10251399', 'cameraSN0': '10251399', 'componentName': 'Words Session 1', 'colour': '1', 'component': '12', 'item': '1', 'session': '1', 'animal': '1121', 'timestamp': 'Mon Jul 18 16:48:43 2011', 'prompt': 'slide2.jpg', 'path': '/tmp/tmph7F7_g', 'basename': '1_1121_1_12_001'}

# an example of regenerated metadata, has no basename so we need to reconstruct it
>>> mdfile = "../test/1_178_4_12_001.xml"
>>> md = read_metadata(mdfile)
>>> md['basename']
'1_178_4_12_001'

# grab an example from the server that has -n files
>>> mdurl = "https://austalk.edu.au/dav/bigasc/data/real/Australian_National_University,_Canberra/Spkr1_178/Spkr1_178_Session2/Session2_16/1_178_2_16_001.xml"
>>> md = read_metadata(mdurl)
>>> md['cameraSN1']
'11072159'
>>> md['files'].keys()
['1_178_2_16_001-ch5-c2Right.wav', '1_178_2_16_001-n-ch6-speaker.wav', '1_178_2_16_001-ch3-strobe.wav', '1_178_2_16_001-n-ch1-maptask.wav', '1_178_2_16_001-ch4-c2Left.wav', '1_178_2_16_001-ch1-maptask.wav', '1_178_2_16_001-camera-0-left.mp4', '1_178_2_16_001-camera-0-right.mp4', '1_178_2_16_001-ch6-speaker.wav', '1_178_2_16_001-n-ch4-c2Left.wav', '1_178_2_16_001-ch2-boundary.wav', '1_178_2_16_001-n-ch5-c2Right.wav', '1_178_2_16_001-n-camera-0-right.mp4', '1_178_2_16_001-n-ch2-boundary.wav', '1_178_2_16_001-n-camera-0-left.mp4', '1_178_2_16_001-n-ch3-strobe.wav']
>>> md['files']['1_178_2_16_001-n-ch5-c2Right.wav']
{'checksum': '2d5b13b05063a4b3b845672d1ca4eb91', 'version': 2, 'type': 'audio', 'channel': 'ch5-c2Right', 'filename': '1_178_2_16_001-n-ch5-c2Right.wav'}


    """

    result = dict()
    
    # parse the xml, might fail but we'll just pass on the exception
    # might have an http url but maybe a local file
    if url.startswith('http'):
        h = urllib2.urlopen(url)
        xmltext = h.read()
        h.close()
    else:
        h = open(url)
        xmltext = h.read()
        h.close()
        
        
    root = ElementTree.fromstring(xmltext)
    
    if root is None:
        # no root element found  => corrupted xml
        # we got nothing
        return result
 
    result['files'] = dict()
    
    for node in root: 
        name = node.tag
        if name == "files":
            # we make a list of the filenames
            for ch in node.findall(".//file"):
                filename = ch.text
                # early versions were writing .xml files into the metadata, we don't
                # want to know about that
                if not filename.endswith(".xml"):
                    
                    # for each file we'll make a dictionary with it's properties
                    if not result['files'].has_key(filename):
                        result['files'][filename] = {'filename': filename}
                    
                    # we're ignoring the 'uploaded' attribute here
                    # since it's not really of interest 
                    
                    if ch.get('md5hash') is not None:
                        result['files'][filename]['checksum'] = ch.get('md5hash')
                    # add new properties for file type and channel
                    info = parse_media_filename(filename)
                    for key in info.keys():
                        result['files'][filename][key] = info[key]


        elif name == "checksums":
            # handle old style checksums in a separate element
            for ch in node.findall(".//md5hash"):
                filename = ch.get('file')
                if not result['files'].has_key(filename):
                    result['files'][filename] = {'filename': filename}
                result["files"][filename]['checksum'] = ch.text

                    
        elif name == "uploaded": 
            pass
        else:
            result[name] = node.text
    
    # regenerated metadata has no basename
    if not result.has_key('basename'):
        result['item'] = int(result['item'])
        result['basename'] = "%(colour)s_%(animal)s_%(session)s_%(component)s_%(item)03d" % result
    
    return result

def parse_media_filename(filename):
    """Extract the channel name, media type and -n status from a filename
    return a dictionary.
    
>>> parse_media_filename('1_178_1_2_150-ch1-maptask.wav')
{'version': 1, 'type': 'audio', 'channel': 'ch1-maptask'}
    
>>> parse_media_filename('1_178_1_2_150-n-ch1-maptask.wav')
{'version': 2, 'type': 'audio', 'channel': 'ch1-maptask'}
    
>>> parse_media_filename('1_178_1_2_150-n-n-ch1-maptask.wav')
{'version': 3, 'type': 'audio', 'channel': 'ch1-maptask'}

>>> parse_media_filename('1_178_1_2_150-n-n-n-n-n-ch1-maptask.wav')
{'version': 6, 'type': 'audio', 'channel': 'ch1-maptask'}

>>> parse_media_filename('1_178_1_2_150-camera-0-left.mp4')
{'version': 1, 'type': 'video', 'channel': 'camera-0-left'}

>>> parse_media_filename('1_1121_1_12_001-ch4-c2Left.wav')
{'version': 1, 'type': 'audio', 'channel': 'ch4-c2Left'}
    """
    
    
    pattern = "([0-9_]+)-((n-)*)([a-zA-Z0-9-]+)\.(...)"
    
    m = re.match(pattern, filename)
    
    if m:
        (base, alln, n, channel, ext) =  m.groups() #@UnusedVariable
        if ext == "wav":
            type = 'audio'
        elif ext == "mp4":
            type = 'video'
        else:
            type = 'unknown'
            
        if n == None:
            version = 1
        else:
            version = len(alln)/2 + 1
        
        return {'channel': channel, 'type': type, 'version': version}
    else:
        #print "pattern not matched", filename
        return dict()

def read_manifest(baseurl):
    """Read the manifest of a session given the URL of 
    the session directory, return a list
    of URLs for the XML metadata files for each item in the session

>>> session_url = "https://austalk.edu.au/dav/bigasc/data/real/Australian_National_University,_Canberra/Spkr1_178/Spkr1_178_Session1"

>>> items = read_manifest(session_url)
>>> len(items)
371
>>> items[0]
'https://austalk.edu.au/dav/bigasc/data/real/Australian_National_University,_Canberra/Spkr1_178/Spkr1_178_Session1/Session1_2/1_178_1_2_021.xml'
    """
    
    # https://austalk.edu.au/dav/bigasc/data/real/Australian_National_University,_Canberra/Spkr1_178/Spkr1_178_Session1
    TEMPLATE = "Session%(session)s_%(component)s/%(basename)s.xml"
    
    manifest_url = os.path.join(baseurl, 'manifest.txt')

    # grab the manifest
    h = urllib2.urlopen(manifest_url)
    manifest_lines = h.readlines()
    h.close()
    
    items = []
    for line in manifest_lines:
        if line.startswith('@'):
            continue
        elif line.strip() == '':
            continue
        else:
            info = parse_item_filename(line)
            info['basename'] = line.strip()
            itemurl = os.path.join(baseurl, TEMPLATE % info)
            items.append(itemurl)

    return items


if __name__=='__main__':
        
        import doctest
        doctest.testmod()
        
        

        
          