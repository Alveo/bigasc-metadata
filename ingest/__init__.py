
from sesameupload import SesameServer
from convert.ra_maptask import RAMapTask
import convert
from data import map_session
import os, sys

      
def ingest_session_map(server, sessiondir, csvdata):
    """Given a base directory for a session, upload the metadata
    for the session to the server"""

    mapper = convert.ItemMapper(server)
    
    def process_item(site, spkr, session, component, item_path):
        """upload metadata for a single item"""
        
        try:
            graph = mapper.item_rdf(item_path+".xml", csvdata)
            sys.stdout.write('.')
            sys.stdout.flush()
            server.upload_graph(graph)
        except:
            print "Problem with item: ", item_path
            
    
    sys.stdout.write(os.path.basename(sessiondir))
    sys.stdout.flush()
    result = [x for x in map_session(sessiondir, process_item)]
    sys.stdout.write('\n')

def ingest_protocol(server):
    """Generate RDF for the protocol and upload it 
    to the server (an instance of SesameServer)"""
    
    assert(isinstance(server, SesameServer))
    import convert
    graph = convert.session_metadata()
    
    print "Uploading", len(graph), "triples for sessions"
    server.upload_graph(graph)
    
    graph = convert.component_metadata()
    
    print "Uploading", len(graph), "triples for components"
    server.upload_graph(graph)
        
    graph = convert.item_metadata()
    
    print "Uploading", len(graph), "triples for items"
    server.upload_graph(graph)
        

def ingest_participants(server):
    """Generate RDF for all participants and upload it 
    to the server (an instance of SesameServer)"""
    
    assert(isinstance(server, SesameServer))
    import convert
    participants = convert.get_participant_list()
    print "Uploading", len(participants), "participants"
    
    maptask = RAMapTask()
    (spkr, map) = maptask.read_all()
    
    for p in participants:
        
        if spkr.has_key(p):
            csvdata = spkr[p]
        else:
            csvdata = None
        
        p_info = convert.get_participant(p)
        graph = convert.participant_rdf(p_info, csvdata)
    
        print "Uploading", len(graph), "triples for participant", p
        server.upload_graph(graph)
        
    
def ingest_participant(server, participant):
    """Generate RDF for one participant and upload it 
    to the server (an instance of SesameServer)"""
    
    assert(isinstance(server, SesameServer))
    import convert

    p_info = convert.get_participant(participant)
    graph = convert.participant_rdf(p_info)

    print "Uploading", len(graph), "triples for participant", participant
    server.upload_graph(graph)
        
        