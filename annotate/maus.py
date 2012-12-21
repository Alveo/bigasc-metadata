'''
Send audio to MAUS for forced alignment

Created on Oct 31, 2012

@author: steve
'''

import urllib, urllib2
import MultipartPostHandler
import os, sys
from StringIO import StringIO
import configmanager
configmanager.configinit()

LEXICON = os.path.join(os.path.dirname(__file__), "AUSTALK.lex")

class MausException(Exception):
    pass

def maus_boolean(value):
    """Turn a Python boolean value into a
    'true' or 'false for MAUS"""
    
    if value:
        return 'true'
    else:
        return 'false'

def maus(wavfile, text, language='ae', canonly=False, minpauselen=5, startword=0, endword=999999, mausshift=10, insprob=0.0):
    """Send the given wavfile to MAUS for forced alignment
    text is the orthographic transcription
    
    returns the text of the textgrid returned by MAUS
    raises MausException if there was an error, the exception
    contains any error text returned by the MAUS web service
    
>>> txt = maus("test/bassinette-sample-16.wav", "bassinette")
>>> txt.find('xmax')
62
>>> txt.find('b{s@net')
896
>>> txt = maus("test/bassinette-sample-16.wav", "not in the lexicon")
Traceback (most recent call last):
MausException: Can't generate phonetic transcription for text 'not in the lexicon'

# a bad request, send a text file
>>> maus("annotate/maus.py", "bassinette")
Traceback (most recent call last):
MausException: MAUS execution did not exit properly and exited with message ERROR: unknown signal type extension py        Please use either 'wav' or 'nis' or 'sph' or 'al' or 'dea' 
<BLANKLINE>

# another bad request, an unknown language
>>> maus("test/bassinette-sample-16.wav", "bassinette", language='unknown')
Traceback (most recent call last):
MausException: Internal Server Error
    """
    
    lex = load_lexicon()
    phb = text_phb(text, lex)
    
    if phb == None:
        raise MausException("Can't generate phonetic transcription for text '%s'" % text)
    
    params = dict((('LANGUAGE', language),
                ('CANONLY', maus_boolean(canonly)),
                ('MINPAUSELEN', str(minpauselen)),
                ('STARTWORD', str(startword)),
                ('ENDWORD', str(endword)),
                ('MAUSSHIFT', str(mausshift)),
                ('INSPROB', str(insprob)),
                ('SIGNAL', open(wavfile)),
                ('BPF', StringIO(phb)),
                ))
    
    opener = urllib2.build_opener(MultipartPostHandler.MultipartPostHandler)
    
    MAUS_URL = configmanager.get_config("MAUS_URL")
    try:
        response = opener.open(MAUS_URL, params)
    except urllib2.HTTPError as e:
        raise MausException(e.msg)
    
    result = response.read()
    
    if result.startswith('File type = "ooTextFile"'):
        # everything was ok
        return result
    else:
        # some kind of error
        raise MausException(result)


def load_lexicon():
    """Load the lexicon from AUSTALK.lex and return 
    a dictionary with words as keys
    
>>> lex = load_lexicon()
>>> lex['actually']
'{ktS@li:'
>>> lex['zoo']
'z}:'
    """

    h = open(LEXICON)
    lines = h.readlines()
    h.close()
    
    result = dict()
    for line in lines:
        words = line.split()
        if len(words) > 2:
            print "Too many fields:", line
        ort = words[0].lower()
        phn = words[1]
        result[ort] = phn
        
    return result
    
    
    
def text_phb(text, lex):
    """Generate a PHB format orthographic transcript
    corresponding to the given text. Text is split 
    on whitespace into words.  
    
    PHB formatted text is returned unless some of the
    words are not in the lexicon, in which case return None
    and print out messages 
    
>>> lex = load_lexicon()
>>> print text_phb('before', lex)
ORT: 0 before
KAN: 0 b@fo:
>>> print text_phb('before zombie', lex)
ORT: 0 before
ORT: 1 zombie
KAN: 0 b@fo:
KAN: 1 zOmbi:
>>> print text_phb('Before, zombie.', lex)
ORT: 0 before
ORT: 1 zombie
KAN: 0 b@fo:
KAN: 1 zOmbi:
>>> print text_phb('hello world', lex)
Not in lexicon: 'hello'
Not in lexicon: 'world'
None
    """
    import re
    
    words = [x.lower() for x in re.split("[\s.,!?]", text) if x != '']
    error = False
    ort = []
    kan = []
    n = 0
    for word in words:
        if lex.has_key(word):
            phon = lex[word] 
            ort.append("ORT: %d %s" % (n, word))
            kan.append("KAN: %d %s" % (n, phon))
        else:
            print "Not in lexicon: '%s'"  % word
            error = True
                        
        n += 1
    
    result = "\n".join(ort) + "\n" + "\n".join(kan)
    
    if error:
        return None
    
    return result

# list of component ids that we can run MAUS over because they are read
MAUSABLE_COMPONENTS = [5, 2, 22, 32, 43, 23, 33, 13, 14, 6, 16, 17] # 3 is story

def make_maus_processor(server, outputdir):
        
    def maus_item(site, spkr, session, component, item_path):
        """Procudure for use with map_session to send the audio data
        for one item to MAUS and store the resulting annotation 
        files"""
        
        
        if not int(component) in MAUSABLE_COMPONENTS:
            print "Can't MAUS", component
            return
        
        item = os.path.basename(item_path)
        outfile = os.path.join(outputdir, "MAUS", site, spkr, session, component, item + ".TextGrid")
        if not os.path.exists(os.path.dirname(outfile)):
            os.makedirs(os.path.dirname(outfile))
        
        # query to find the media file URL and prompt text
        qq = """
            PREFIX austalk:<http://ns.austalk.edu.au/>
            PREFIX ausnc:<http://ns.ausnc.org.au/schemas/ausnc_md_model/>
            
            select distinct ?media ?prompt where {
              ?i a ausnc:AusNCObject .
              ?i austalk:basename "%s" .
              ?i austalk:media ?media .
              ?media austalk:channel "ch6-speaker16" .
              ?i austalk:prototype ?ip .
              ?ip austalk:prompt ?prompt .
            }
            """ % item
         
        qresult = server.query(qq)
        if qresult != None and qresult['results']['bindings'] != []:
            row = qresult['results']['bindings'][0]
            media = row['media']['value']
            prompt = row['prompt']['value']
            # if the prompt contains 'sounds like' then we want just the first word
            if prompt.find("sounds like") >= 0:
                prompt = prompt.split()[0]
            
            media_file = url_to_path(media)
            try:
                annotation = maus(media_file, prompt)
                sys.stdout.write('.')
                sys.stdout.flush()
                
                h = open(outfile, 'w')
                h.write(annotation)
                h.close()
            except MausException as e:
                print "ERROR", item, e
        else:
            print "Item has no media/prompt: ", item
    
    return maus_item
    

def url_to_path(media):
    """Convert a media URL to a path on the local
    file system"""
    
    root = "/var/syndisk/published"

    (ignore, tmp) = urllib.splittype(media)
    (ignore, path) = urllib.splithost(tmp)
    
    return root + path
    
    
    
    



if __name__=='__main__':
        
        import doctest
        doctest.testmod()
    
    
    