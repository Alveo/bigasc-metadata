
from sesameupload import SesameServer

def ingest_session(server, baseurl):
    """Given the URL of a session and an instance of SesameServer, slurp the metadata and 
    upload it to the server"""
     
    assert(isinstance(server, SesameServer))
    import convert
    items = convert.read_manifest(baseurl)
    
    mapper = convert.ItemMapper(server)
    
    for item in items:
        graph = mapper.item_rdf(item)
        print "Uploading", len(graph), "triples for item", item[-19:]
        server.upload_graph(graph)
        
        
def ingest_protocol(server):
    """Generate RDF for the protocol and upload it 
    to the server (an instance of SesameServer)"""
    
    assert(isinstance(server, SesameServer))
    import convert
    graph = convert.protocol_metadata()
    
    print "Uploading", len(graph), "triples for protocol"
    server.upload_graph(graph)
    

def ingest_participants(server):
    """Generate RDF for all participants and upload it 
    to the server (an instance of SesameServer)"""
    
    assert(isinstance(server, SesameServer))
    import convert
    participants = convert.get_participant_list()
    
    for p in participants:
        p_info = convert.get_participant(p)
        graph = convert.participant_rdf(p_info)
    
        print "Uploading", len(graph), "triples for participant", p
        server.upload_graph(graph)
        
        
        