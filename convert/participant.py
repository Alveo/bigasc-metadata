'''
Created on Sep 18, 2012

@author: Steve Cassidy

Convert meta-data about participants harvested from the web server database to RDF
'''
from rdflib import Literal
import urllib2
import json
import map
from namespaces import *

#PARTICIPANT_URI = "https://echidna.science.mq.edu.au/forms/export/participants/"
PARTICIPANT_URI = "https://austalk.edu.au/forms/export/participants/"


# list exceptions to our site short name generator
SITE_SHORTNAMES = {
"UOCC": "UC",    # "University of Canberra"        "Canberra"
"UOTH": "UTAS", # "University of Tasmania"        "Hobart"
"ANUC":  "ANU",  # "Australian National University"        "Canberra"
"USYDS": "USYD", # "University of Sydney"  "Sydney"
"UWAP": "UWA",   # "University of Western Australia"       "Perth"
"UOSCM": "USCM", # "University of the Sunshine Coast"      "Maroochydore"
"UNEA": "UNE",   # "University of New England"     "Armidale"
"UNSWS": "UNSW", # "University of New South Wales" "Sydney"
"UOMM": "UMELBM", # "University of Melbourne"       "Melbourne"
"UOMC": "UMELBC", # "University of Melbourne"       "Castlemaine"
"UOQT": "UQT",  # "University of Queensland"      "Townsville"
"UOQB": "UQB",  # "University of Queensland"      "Townsville"
}


def get_participant_list():
    """Return a list of participant ids"""
    
    uri = PARTICIPANT_URI
    
    h = urllib2.urlopen(uri)
    data = h.read()
    h.close()
    
    result = json.loads(data)
    # we just want the 'id' field from each record
    result = [r['id'] for r in result]
    
    return result
    

def get_participant(id):
    """id is a numerical participant identifier (1_123),
    get the participant metadata from the server and 
    return as a dictionary
     
>>> p = get_participant('2_450') 
>>> p['animal']['id']
450
>>> p['colour']['id']
2
>>> p = get_participant('1_978') 
>>> p['animal']['id']
978
>>> p['colour']['id']
1
    """
    
    #print "get_participant", id
    
    uri = PARTICIPANT_URI + id
    
    h = urllib2.urlopen(uri)
    data = h.read()
    h.close()
        
    result = json.loads(data)
    #print "result", result['animal']
    
    return result


def get_participant_from_file(filename):
    """id is a numerical participant identifier (1_123),
    get the participant metadata from the given filename and 
    return as a dictionary (mainly for testing)
    
>>> part_file = "../test/participant.json"
>>> p = get_participant_from_file(part_file) 
>>> p['animal']['id']
450
>>> p['colour']['id']
2
    
    """
    
    h = open(filename)
    data = h.read()
    h.close()
    
    result = json.loads(data)
    
    return result

def birth_geolocation(m):
    """Using the POB fields in the metadata dictionary m, 
    return a geonames URI for the place of birth"""
    
    from geonames import GeoNames
    
    g = GeoNames()
    
    uri = g.placename_uri(m['pob_town'], m['pob_state'], m['pob_country'])
    
    return uri
    

def map_gender(subj, prop, value):
    """Map gender (M or F) to FOAF.gender (male or female)
>>> map_gender('foo', 'sex', 'M')
[('foo', rdflib.term.URIRef(u'http://xmlns.com/foaf/0.1/gender'), rdflib.term.Literal(u'male'))]
>>> map_gender('foo', 'sex', 'F')
[('foo', rdflib.term.URIRef(u'http://xmlns.com/foaf/0.1/gender'), rdflib.term.Literal(u'female'))]
>>> map_gender('foo', 'sex', 'U')
Unknown value for SEX: U
[('foo', rdflib.term.URIRef(u'http://xmlns.com/foaf/0.1/gender'), rdflib.term.Literal(u'U'))]

    """
    
    
    if value == "M":
        value = "male"
    elif value == "F":
        value = "female"
    else:
        print "Unknown value for SEX: %s" % value
        #raise Exception("Unknown value for SEX in ICE: %s" % value)
    
    return [(subj, FOAF.gender, Literal(value))]

def map_dob(subj, prop, value):
    """Map date of birth, only retain the year
>>> map_dob('foo', 'dob', '1992-01-21')
[('foo', rdflib.term.URIRef(u'http://dbpedia.org/ontology/birthYear'), rdflib.term.Literal(u'1992', datatype=rdflib.term.URIRef(u'http://www.w3.org/2001/XMLSchema#integer')))]
    """
    
    (y, m, d) = value.split('-')
    return [(subj, DBP.birthYear, Literal(int(y)))]


def map_ra(subj, prop, value):
    """Map the RA (Research Assistant) field to a 
    unique but anonymous identifier for the RA - the md5hash of their email address in lowercase

>>> ra_info = {u'username': u'steve', u'first_name': '', u'last_name': '', u'is_active': True, u'email': u'steve.cassidy@mq.edu.au', u'is_superuser': True, u'is_staff': True, u'last_login': u'2012-02-01 18:00:05', u'id': 1, u'date_joined': u'2011-06-24 15:20:35'}
>>> map_ra('foo', 'RA', ra_info)
[('foo', rdflib.term.URIRef(u'http://ns.austalk.edu.au/RA'), rdflib.term.Literal(u'b6816945deae3ab28748cd509a5f21e1'))]
    """
    import hashlib
    
    if value.has_key('email'):
        email = value['email'].lower()
        hash = hashlib.md5(email).hexdigest()
    else:
        user = value['username'].lower()
        hash = hashlib.md5(user).hexdigest()
    
    return [(subj, NS.RA, Literal(hash))]
    
    
def map_location(subj, prop, value):
    """Map the location value to one of the defined site names

>>> loc = {u'city': u'Bathurst', u'state': u'NSW', u'name': u'Charles Sturt University', u'id': 4} 
>>> map_location('foo', 'location', loc)
[('foo', rdflib.term.URIRef(u'http://ns.austalk.edu.au/recording_site'), rdflib.term.URIRef(u'http://id.austalk.edu.au/protocol/site/CSUB')), (rdflib.term.URIRef(u'http://id.austalk.edu.au/protocol/site/CSUB'), rdflib.term.URIRef(u'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'), rdflib.term.URIRef(u'http://ns.austalk.edu.au/RecordingSite')), (rdflib.term.URIRef(u'http://id.austalk.edu.au/protocol/site/CSUB'), rdflib.term.URIRef(u'http://www.w3.org/2000/01/rdf-schema#label'), rdflib.term.Literal(u'CSUB')), (rdflib.term.URIRef(u'http://id.austalk.edu.au/protocol/site/CSUB'), rdflib.term.URIRef(u'http://ns.austalk.edu.au/city'), rdflib.term.Literal(u'Bathurst')), (rdflib.term.URIRef(u'http://id.austalk.edu.au/protocol/site/CSUB'), rdflib.term.URIRef(u'http://ns.austalk.edu.au/institution'), rdflib.term.Literal(u'Charles Sturt University'))]
   """

    # get initials of name
    inits = [w[0] for w in value['name'].split()]
    # and first letter of city
    inits += value['city'][0]
    inits = "".join(inits).upper()
    
    # pull in the exception if present
    if SITE_SHORTNAMES.has_key(inits):
        inits = SITE_SHORTNAMES[inits]
    
    site_uri = PROTOCOL_NS["site/"+inits]
    
    
    return [(subj, NS.recording_site, site_uri),
            (site_uri, RDF.type, NS.RecordingSite),
            (site_uri, RDFS.label, Literal(inits)),
            (site_uri, NS.city, Literal(value['city'])),
            (site_uri, NS.institution, Literal(value['name']))]



def map_ratings(graph, p_md):
    """generate triples to record the ratings for 
    sessions and add them to the graph"""
    
    
    for rating in p_md['rating']:
        
        c_uri = generate_component_uri(p_md['colour']['id'], p_md['animal']['id'], rating['session'], rating['component'])
        graph.add((c_uri, NS.videorating, Literal(rating['video'])))
        graph.add((c_uri, NS.audiorating, Literal(rating['audio'])))
        graph.add((c_uri, NS.comment, Literal(rating['comment'])))

# a map for nested properties (education and professional history)
submap = map.FieldMapper()
submap.add('_state', ignore=True)
submap.add("id", ignore=True)

partmap = map.FieldMapper()
partmap.add("dob", mapper=map_dob)
partmap.add("_state", ignore=True)
partmap.add("id", ignore=True)
partmap.add("participant_id", ignore=True)
partmap.add("colour", ignore=True)
partmap.add("animal", ignore=True)
partmap.add("gender", mapper=map_gender)
partmap.add('profession_history', mapper=map.dictionary_blank_mapper(NS.profession_history, submap))
partmap.add('education_history', mapper=map.dictionary_blank_mapper(NS.education_history, submap))
partmap.add('language_usage', mapper=map.dictionary_blank_mapper(NS.language_usage, submap))
partmap.add('RA', mapper=map_ra)
partmap.add('location', mapper=map_location)
partmap.add('rating', ignore=True)


def participant_uri(colour, animal):
    """Generate the URI for a participant given their colour and animal ids"""
    
    p_id = "participant/%s_%s" % (colour, animal)
    return ID_NS[p_id]


def participant_rdf(part_md):
    """part_md is a dictionary of participant metadata from 
    the web server, generate corresponding RDF, returning a 
    graph object
    
    
>>> part_file = "../test/participant.json"
>>> p = get_participant_from_file(part_file) 
>>> graph = participant_rdf(p)
>>> len(graph)
149
>>> print graph.serialize(format='turtle')
    """
    
    p_id = "%s_%s" % (part_md['colour']['id'], part_md['animal']['id'])
    p_name = "%s - %s" % (part_md['colour']['name'], part_md['animal']['name'])
    
    
    p_uri = participant_uri(part_md['colour']['id'], part_md['animal']['id'])
    graph = partmap.mapdict(p_uri, part_md)
    
    graph.add((p_uri, RDF.type, FOAF.Person))
    graph.add((p_uri, NS.id, Literal(p_id)))
    graph.add((p_uri, NS.name, Literal(p_name)))
    
    pob_uri = birth_geolocation(part_md)
    if pob_uri:
        graph.add((p_uri, NS.birthPlace, pob_uri))
        
    if part_md.has_key('rating'):
        map_ratings(graph, part_md)

    # add some namespaces to make output prettier
    graph.bind('austalk', NS)
    graph.bind('dc', DC)
    graph.bind('foaf', FOAF)
    graph.bind('dbpedia', DBP)

    return graph


if __name__=='__main__':
            
    import doctest
    doctest.testmod()


        
        