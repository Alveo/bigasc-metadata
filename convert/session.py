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
CLASS_SESSION = NS.Session
CLASS_COMPONENT = NS.Component
CLASS_ITEM = NS.Item


# define this here because we want to access Persistance
def component_map():
    """Return a dictionary to map between component numbers
    and the short names we use in media URLs"""
    
    component_map = dict()
    
    for comp in Persistence.Component.GetInstances():
        component_map[comp.GetId()] = comp.GetShortName()

    return component_map


def session_metadata(graph):
    """Return a dictionary containing all of the metadata
    from the session and component descriptions"""
    
    # generate a list of session numbers and descriptors
    for session in Persistence.Session.GetInstances():
        id = PROTOCOL_NS[SESSION_URI_TEMPLATE % session.GetId()]
        
        graph.add((id, NS.id, Literal(session.GetId())))
        graph.add((id, NS.name, Literal(session.GetName())))
        graph.add((id, RDF.type, CLASS_SESSION))
        
        for comp in session.getComponents():
            cid = PROTOCOL_NS[COMPONENT_URI_TEMPLATE % comp.GetId()]
            graph.add((cid, DC.isPartOf, id))
            


def component_metadata(graph):
    """Return a dictionary of metadata for each component"""
    
    for comp in Persistence.Component.GetInstances():
        cid = PROTOCOL_NS[COMPONENT_URI_TEMPLATE % comp.GetId()]
        
        graph.add((cid, NS.id, Literal(comp.GetId())))
        graph.add((cid, NS.name, Literal(comp.GetName())))
        graph.add((cid, NS.shortname, Literal(comp.GetShortName())))
        
        for item in comp.getItems():
            iid = PROTOCOL_NS[ITEM_URI_TEMPLATE % (comp.GetId(), item.GetId())]
            graph.add((iid, DC.isPartOf, cid))
            graph.add((iid, RDF.type, CLASS_ITEM))
            
        # add type info
        graph.add((cid, RDF.type, CLASS_COMPONENT))
        


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

    
    sm = session_metadata(graph)
    cm = component_metadata(graph)
    im = item_metadata(graph)

    return graph
    
            
if __name__=='__main__':
    
    graph = protocol_metadata()

    print "Graph has ", len(graph), "statements"
    s = graph.serialize(format='turtle')
    print s
