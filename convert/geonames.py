'''
Created on Sep 20, 2012

@author: steve
'''

import urllib, urllib2
import json
from rdflib import Namespace

class GeoNames:
    """Communicate with the geonames server to get identifiers for
    place names"""
    
    SERVER_URL = "http://api.geonames.org/searchJSON"
    GEONS = Namespace("http://sws.geonames.org/")
    
    USERNAME = 'austalk'
    
    def placename_info(self, city, state, country):
        """Return a dictionary of information about this placename
        from the geonames service or None if nothing can be found.
        Dictionary will have keys: geoname, placename, countryname, countrycode

>>> g = GeoNames()
>>> g.placename_info(u"Sydney", u"NSW", u"Australia")
{'town': u'Sydney', 'countrycode': u'AU', 'geoname': 2147714, 'long': u'151.20732', 'countryname': u'Australia', 'state': u'New South Wales', 'lat': u'-33.86785'}
>>> g.placename_info(u"dksjh\xe4dfkjskdjf", u"Vic", u"Australia")

>>> g.placename_info("Sidney", "NSW", "Australia")
{'town': u'Sydney', 'countrycode': u'AU', 'geoname': 2147714, 'long': u'151.20732', 'countryname': u'Australia', 'state': u'New South Wales', 'lat': u'-33.86785'}
        """
        
        place = unicode(city+u" "+state+u" "+country).encode('utf-8')
        query_enc = urllib.urlencode({'q': place,'username': self.USERNAME})
        headers = {'Accept': 'application/json'}
        req = urllib2.Request(self.SERVER_URL+'?' + query_enc, headers=headers)
        
        try: 
            h = urllib2.urlopen(req)
            response = h.read()
            h.close()
        except urllib2.URLError, e: 
            return None

        #print "Looking for ", place

        info = json.loads(response)
        # check that we have at least one geoname for our query
        if info['totalResultsCount'] > 0:
             
            # find a good match, name should match our place name
            # and it should be a populated place
            for gn in info['geonames']:
                #TODO test: I suspect checking this gn['name']==city will be a problem for misspelt places
                if 'fcode' in gn and gn['fcode'].startswith('PPL'):
                    location = gn 
                    
                    result = dict()
                    result['geoname'] = location['geonameId']
                    result['town'] = location['name']
                    result['countryname'] = location['countryName']
                    result['countrycode'] = location['countryCode']
                    result['lat'] = location['lat']
                    result['long'] = location['lng']
                    if 'adminName1' in location.keys():
                        result['state'] = location['adminName1']
                    else:
                        result['state'] = ''
                    #print result
                    return result
        #print "nothing found"
        return None
        
    def placename_uri(self, info):
        """Return a URIRef for the given place given the 
        info dictionary returned by placename_info, 
        Return None if nothing found"""
        
        if info:
            return self.GEONS[unicode(info['geoname'])]
        else:
            return None
        
        
if __name__=='__main__':
        
        import doctest
        doctest.testmod(verbose=True)
        
            
        