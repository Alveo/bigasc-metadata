'''
Created on Sep 14, 2012

@author: steve

Convert metadata from the Blackbox Recorder software to RDF
 This metadata describes the sessions and components recorded

'''
blackbox_path = '/Users/steve/projects/eclipse-workspace/blackbox-gui/src'

import sys
sys.path.append(blackbox_path)
from recorder import Persistence

from rdflib import Namespace, Graph, Literal
from rdflib.term import URIRef

from namespaces import *


### classes
CLASS_COMPONENT = NS.Component
CLASS_WORDS = NS.Words
CLASS_SENTENCES = NS.Sentences
CLASS_MAPTASK = NS.MapTask
CLASS_YESNO = NS.YesNo

def session_metadata(graph):
    """Return a dictionary containing all of the metadata
    from the session and component descriptions"""
    
    # generate a list of session numbers and descriptors
    for session in Persistence.Session.GetInstances():
        id = PROTOCOL_NS[SESSION_URI_TEMPLATE % session.GetId()]
        
        graph.add((id, NS.id, Literal(session.GetId())))
        graph.add((id, NS.name, Literal(session.GetName())))
        
        for comp in session.getComponents():
            cid = PROTOCOL_NS[COMPONENT_URI_TEMPLATE % comp.GetId()]
            graph.add((cid, DC.partOf, id))
            


def component_metadata(graph):
    """Return a dictionary of metadata for each component"""
    
    for comp in Persistence.Component.GetInstances():
        cid = PROTOCOL_NS[COMPONENT_URI_TEMPLATE % comp.GetId()]
        
        graph.add((cid, NS.id, Literal(comp.GetId())))
        graph.add((cid, NS.name, Literal(comp.GetName())))
        
        for item in comp.getItems():
            iid = PROTOCOL_NS[ITEM_URI_TEMPLATE % (comp.GetId(), item.GetId())]
            graph.add((iid, DC.partOf, cid))
            
        # add some class info based on component name
        name = comp.GetName()
        if name.startswith('Words'):
            graph.add((cid, RDF.type, CLASS_WORDS))
        elif name.startswith('Sentences'):
            graph.add((cid, RDF.type, CLASS_SENTENCES))
        elif name.startswith('Map Task'):
            graph.add((cid, RDF.type, CLASS_MAPTASK))
        elif name.startswith("Yes/No"):
            graph.add((cid, RDF.type, CLASS_YESNO))
        else:
            graph.add((cid, RDF.type, CLASS_COMPONENT))
        
            
    # TODO: include modified powerpoint and map file for session 17 - the early sentences
    # otherwise the metadata will be wrong


def item_metadata(graph):
    """Return a dictionary of metadata for each item"""
    
    for comp in Persistence.Component.GetInstances():
        for item in comp.getItems():
            iid = PROTOCOL_NS[ITEM_URI_TEMPLATE % (comp.GetId(), item.GetId())]
            graph.add((iid, NS.id, Literal(item.GetId())))
            graph.add((iid, NS.prompt, Literal(item.GetPrompt())))
            
def protocol_metadata():
    
    graph = Graph()
    graph.bind('austalk', NS)
    graph.bind('dc', DC)
    graph.bind('protocol', PROTOCOL_NS)
    
    ## add top level of class hierarchy
    graph.add((CLASS_WORDS, RDF.type, CLASS_COMPONENT))
    graph.add((CLASS_SENTENCES, RDF.type, CLASS_COMPONENT))
    graph.add((CLASS_MAPTASK, RDF.type, CLASS_COMPONENT))
    graph.add((CLASS_YESNO, RDF.type, CLASS_COMPONENT))
    
    sm = session_metadata(graph)
    cm = component_metadata(graph)
    im = item_metadata(graph)

    return graph
    
            
if __name__=='__main__':
    
    protocol_metadata(graph)

    print "Graph has ", len(graph), "statements"
    s = graph.serialize(format='turtle')
    print s
