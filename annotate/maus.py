'''
Send audio to MAUS for forced alignment

Created on Oct 31, 2012

@author: steve
'''

import urllib2
import MultipartPostHandler
import os
from StringIO import StringIO

#MAUS_URL = "http://webapp.phonetik.uni-muenchen.de/BASWebServices/services/runMAUS"
MAUS_URL = "http://webapp.phonetik.uni-muenchen.de/BASWebServicesTest/services/runMAUS"
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
    
>>> txt = maus("../test/bassinette-sample-16.wav", "bassinette")
>>> txt.find('xmax')
62
>>> txt.find('b{s@net')
896
>>> txt = maus("../test/bassinette-sample-16.wav", "not in the lexicon")
Traceback (most recent call last):
MausException: Can't generate phonetic transcription for text 'not in the lexicon'

# a bad request, send a text file
>>> maus("maus.py", "bassinette")
Traceback (most recent call last):
MausException: MAUS execution did not exit properly and exited with message ERROR: unknown signal type extension py        Please use either 'wav' or 'nis' or 'sph' or 'al' or 'dea' 
<BLANKLINE>

# another bad request, an unknown language
>>> maus("../test/bassinette-sample-16.wav", "bassinette", language='unknown')
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
        ort = words[0]
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
>>> print text_phb('hello world', lex)
Not in lexicon:  hello
Not in lexicon:  world
None
    """
    
    words = text.split()
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
            print "Not in lexicon: ", word
            error = True
                        
        n += 1
    
    result = "\n".join(ort) + "\n" + "\n".join(kan)
    
    if error:
        return None
    
    return result


if __name__=='__main__':
        
        import doctest
        doctest.testmod()
    
    
    