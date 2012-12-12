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
"UOSS": "USYD", # "University of Sydney"  "Sydney"
"UOWAP": "UWA",   # "University of Western Australia"       "Perth"
"UOTSCM": "USCM", # "University of the Sunshine Coast"      "Maroochydore"
"UONEA": "UNE",   # "University of New England"     "Armidale"
"UONSWS": "UNSW", # "University of New South Wales" "Sydney"
"UOMM": "UMELBM", # "University of Melbourne"       "Melbourne"
"UOMC": "UMELBC", # "University of Melbourne"       "Castlemaine"
"UOQT": "UQT",  # "University of Queensland"      "Townsville"
"UOQB": "UQB",  # "University of Queensland"      "Townsville"
"FUA": "FLIN", 
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

def birth_geolocation(p_uri, m, graph):
    """Using the POB fields in the metadata dictionary m, 
    find a geonames URI for the place of birth and add
    some triples to the graph"""
    
    from geonames import GeoNames
    
    g = GeoNames()
    
    info = g.placename_info(m['pob_town'], m['pob_state'], m['pob_country'])

    if info == None:
        return
    
    pob_uri = g.placename_uri(info)
    
    graph.add((p_uri, NS.birthPlace, pob_uri))
    graph.add((pob_uri, RDF.type, GEO.Feature))
    graph.add((pob_uri, GEO.lat, Literal(info['lat'])))
    graph.add((pob_uri, GEO.long, Literal(info['long'])))

    

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
[('foo', rdflib.term.URIRef(u'http://ns.austalk.edu.au/research_assistant'), rdflib.term.Literal(u'b6816945deae3ab28748cd509a5f21e1'))]
    """
    import hashlib
    import time
    
    # add some salt so that we can't discover the identity if we know the email address or name
    salt = str(time.time())
    
    if value.has_key('email'):
        email = value['email'].lower()
        hash = hashlib.md5(salt+email).hexdigest()
    else:
        user = value['username'].lower()
        hash = hashlib.md5(salt+user).hexdigest()

    # make a person ID and record them as a foaf:Person
    return [(subj, NS.research_assistant, ID_NS[hash]),
            (ID_NS[hash], RDF.type, FOAF.Person)]
    
    
def map_location(subj, prop, value):
    """Map the location value to one of the defined site names

>>> loc = {u'city': u'Bathurst', u'state': u'NSW', u'name': u'Charles Sturt University', u'id': 4} 
>>> map_location('foo', 'location', loc)
[('foo', rdflib.term.URIRef(u'http://ns.austalk.edu.au/recording_site'), rdflib.term.URIRef(u'http://id.austalk.edu.au/protocol/site/CSUB')), (rdflib.term.URIRef(u'http://id.austalk.edu.au/protocol/site/CSUB'), rdflib.term.URIRef(u'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'), rdflib.term.URIRef(u'http://ns.austalk.edu.au/RecordingSite')), (rdflib.term.URIRef(u'http://id.austalk.edu.au/protocol/site/CSUB'), rdflib.term.URIRef(u'http://www.w3.org/2000/01/rdf-schema#label'), rdflib.term.Literal(u'CSUB')), (rdflib.term.URIRef(u'http://id.austalk.edu.au/protocol/site/CSUB'), rdflib.term.URIRef(u'http://ns.austalk.edu.au/city'), rdflib.term.Literal(u'Bathurst')), (rdflib.term.URIRef(u'http://id.austalk.edu.au/protocol/site/CSUB'), rdflib.term.URIRef(u'http://ns.austalk.edu.au/institution'), rdflib.term.Literal(u'Charles Sturt University'))]
>>> loc = {u'city': u"Maroochydore", u'state': u'QLD', u'name': u'University of the Sunshine Coast', u'id': 6} 
>>> for t in map_location('bar', 'location', loc):
...   print t
('bar', rdflib.term.URIRef(u'http://ns.austalk.edu.au/recording_site'), rdflib.term.URIRef(u'http://id.austalk.edu.au/protocol/site/USCM'))
(rdflib.term.URIRef(u'http://id.austalk.edu.au/protocol/site/USCM'), rdflib.term.URIRef(u'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'), rdflib.term.URIRef(u'http://ns.austalk.edu.au/RecordingSite'))
(rdflib.term.URIRef(u'http://id.austalk.edu.au/protocol/site/USCM'), rdflib.term.URIRef(u'http://www.w3.org/2000/01/rdf-schema#label'), rdflib.term.Literal(u'USCM'))
(rdflib.term.URIRef(u'http://id.austalk.edu.au/protocol/site/USCM'), rdflib.term.URIRef(u'http://ns.austalk.edu.au/city'), rdflib.term.Literal(u'Maroochydore'))
(rdflib.term.URIRef(u'http://id.austalk.edu.au/protocol/site/USCM'), rdflib.term.URIRef(u'http://ns.austalk.edu.au/institution'), rdflib.term.Literal(u'University of the Sunshine Coast'))
   """

    site_id = map_site_name(value['name'], value['city'])
    
    site_uri = PROTOCOL_NS["site/"+site_id]
    
    
    return [(subj, NS.recording_site, site_uri),
            (site_uri, RDF.type, NS.RecordingSite),
            (site_uri, RDFS.label, Literal(site_id)),
            (site_uri, NS.city, Literal(value['city'])),
            (site_uri, NS.institution, Literal(value['name']))]

def map_site_name(name, city):
    """Given a site name and city, generate the short name that we're going to 
    use in future
    
>>> map_site_name("University of Queensland", "Brisbane")
'UQB'
>>> map_site_name("Univeristy of Tasmania", "Hobart")
'UTAS'
>>> map_site_name("University of Sydney", "Sydney")
'USYD'
    """
    
    # get initials of name
    inits = [w[0] for w in name.split()]
    # and first letter of city
    inits += city[0]
    inits = "".join(inits).upper()

    # pull in the exception if present
    if SITE_SHORTNAMES.has_key(inits):
        inits = SITE_SHORTNAMES[inits]
        
    return inits


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
partmap.add('language_usage', mapper=map.dictionary_blank_mapper(NS.language_usage, submap))
partmap.add('residence_history', mapper=map.dictionary_blank_mapper(NS.residential_history, submap))
partmap.add('RA', mapper=map_ra)
partmap.add('location', mapper=map_location)
partmap.add('rating', ignore=True)

## the following are ignored because they potentially expose too much
## personal detail on the site
partmap.add('profession_history', ignore=True) 
partmap.add('education_history', ignore=True)  
partmap.add('religion', ignore=True)



def participant_uri(colour, animal, id=None):
    """Generate the URI for a participant given their colour and animal ids
    or their id (1_123), id overrides other args if provided"""
    
    if id == None:
        p_id = "participant/%s_%s" % (colour, animal)
    else:
        p_id = "participant/"+id
        
    return ID_NS[p_id]


def participant_rdf(part_md, csvdata=None):
    """part_md is a dictionary of participant metadata from 
    the web server, generate corresponding RDF, returning a 
    graph object
    
    If csvdata is present it should be a dictionary of speaker 
    properties read from the RA spreadsheets, it will be used
    to override and validate the metadata
    
    
>>> part_file = "../test/participant.json"
>>> p = get_participant_from_file(part_file) 
>>> p = get_participant('1_987') 
>>> graph = participant_rdf(p)
>>> len(graph)
176
>>> print graph.serialize(format='turtle')
    """
    
    p_id = "%s_%s" % (part_md['colour']['id'], part_md['animal']['id'])
    p_name = "%s - %s" % (part_md['colour']['name'], part_md['animal']['name'])
    
    
    p_uri = participant_uri(part_md['colour']['id'], part_md['animal']['id'])
    graph = partmap.mapdict(p_uri, part_md, NS['graphs/participants'])
    
    graph.add((p_uri, RDF.type, FOAF.Person))
    graph.add((p_uri, NS.id, Literal(p_id)))
    graph.add((p_uri, NS.name, Literal(p_name)))
    
    birth_geolocation(p_uri, part_md, graph)
         
    if part_md.has_key('rating'):
        map_ratings(graph, part_md)
        
        
    # check and update some values from csvdata
    if csvdata != None:
        (d, m, y) = csvdata['DOB'].split('/')
        if len(y) == 2:
            if int(y) < 12:
                refyr = "20"+y 
            else:
                refyr = "19"+y
        elif len(y) == 4:
            refyr = y
        else:
            print "Odd year:", y
        
        yobs = graph.objects(subject=p_uri, predicate=DBP.birthYear)
        for yob in yobs:
            if  yob != refyr:
                print "\tDOBs differ for %s, %s changed to %s" % (p_id, yob, refyr)
                
                # modify the graph
                graph.remove((p_uri, DBP.birthYear, yob))
                graph.add((p_uri, DBP.birthYear, Literal(refyr)))
           
        # SES status
        if csvdata.has_key('SES'):
            ses = csvdata['SES']
            if ses.lower().startswith('prof'):
                ses = Literal('Professional')
            elif ses.lower().startswith('nprof'):
                ses = Literal('Non Professional')
            else:
                print "Unknown SES category: ", ses
                
            graph.add((p_uri, NS.ses, ses))

        if csvdata.has_key('Comment'):
            graph.add((p_uri, NS.racomment, Literal(csvdata['Comment'])))
            
        if csvdata.has_key('NOTES'):
            graph.add((p_uri, NS.maptaskcomment, Literal(csvdata['NOTES'])))

    # add some namespaces to make output prettier
    graph.bind('austalk', NS)
    graph.bind('dc', DC)
    graph.bind('foaf', FOAF)
    graph.bind('dbpedia', DBP)

    return graph


if __name__=='__main__':
            
    import doctest
    doctest.testmod()


        
        
