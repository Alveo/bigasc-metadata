
from sesameupload import SesameServer
from convert.ra_maptask import RAMapTask

def ingest_session(server, baseurl, csvdata):
    """Given the URL of a session and an instance of SesameServer, slurp the metadata and 
    upload it to the server"""
     
    assert(isinstance(server, SesameServer))
    import convert
    items = convert.read_manifest(baseurl)
    
    mapper = convert.ItemMapper(server)
    
    participants = []
    
    for item in items:
        graph = mapper.item_rdf(item, csvdata)
        print "Uploading", len(graph), "triples for item", item[-19:]
        server.upload_graph(graph)
        
        #p = mapper.item_participant(item)
        #if not p in participants:
        #    participants.append(p)
        #    ingest_participant(server, p)
        
        
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
        
        