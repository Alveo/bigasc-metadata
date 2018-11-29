About this Project
------------------

This project contains scripts to process the files and metadata for the Big Australian Speech Corpus (BigASC).  
The original data is collected using the BlackBox application and then uploaded to a central server 
via a custom Django application (bigasc).  These scipts convert the various forms of metadata to RDF and
process the audio and video files into a form ready for publication.  The final published version of
the data is served via another Django application (smallasc).


Notes on metadata format for Austalk
------------------------------------

Metadata is ingested from the following sources into a single triple store:

- blackbox protocol (sessions, components, prompts, etc)
- website database (participants, QA ratings)
- item xml metadata (items, files)
- RA spreadsheets (map task speakers, DOBs)


Ingest Process
--------------

A number of scripts harvest different bits of data and upload it to the RDF store.

```
#!bash
# generate metadata and upload
harvest_protocol.py
harvest_participants.py
harvest_sites.py
upload_graphs.py OUTPUT_DIR/metadata

# copy audio files and upload metadata
resample_audio.py 
copy_files.py audio 
upload_graphs.py OUTPUT_DIR/metadata

# copy video files and upload metadata
copy_files video
upload_graphs OUTPUT_DIR/metadata

# optional steps
# harvest any annotations and upload them
harvest_annotations.py <input dir> <ext> <origin>
upload_graphs OUTPUT_DIR/annotations/metadata

# generate MAUS annotations for some speakers
maus_session.py maus <speakerlist>
upload_graphs OUTPUT_DIR/MAUS

```

The file config.ini contains settings that control the location of source data, 
the location of the output and the Sesame endpoint that data will be uploaded to.
See config.ini.dist for example settings. 

```
#!bash
harvest_protocol.py 
```

 this script harvests meta-data about the prompts and sessions from the blackbox
 software and converts to RDF.   
 
 This script is generally run first.

```
#!bash
harvest_participants.py
```
 
 this script harvests participant meta-data from the austalk.edu.au webserver
 (i.e. the questionnaire data and QA data stored there) and converts to RDF.
 
 Some pruning of meta-data is done for privacy protection, so that not all of
 the meta-data is uploaded. The level of pruning is controlled by the 
 setting PARTICIPANT_DETAIL in config.ini.  
 
 The script also reads the RA spreadsheets (converted to CSV and stored with the 
 source code of this project) and harvests additional data from there if 
 possible.   DOB is checked and if different, the DOB from the spreadsheet 
 is used.   

```
#!bash
harvest_sites.py  <limit>?
```

 this script harvests meta-data for all of the items in all sessions 
 in all the sites in the data directory. 
 It needs direct access to the stored data so must be run
 on the austalk.edu.au server.   
 
 the script reads the XML metadata for each item and converts it to RDF
 which is uploaded.  It also looks at the data on disk and generates 
 URLs for audio and video files ALTHOUGH THE AUDIO AND VIDEO FILES ARE 
 NOT MOVED OR ALTERED.  
 
 The script also reads the RA spreadsheets to get information on Map Task
 partners that might not be present in the XML metadata.
 
 The script must be run after the upload_participants script because it
 relies on querying the data store to find the site name for a given
 participant.  
 
 if the optional limit argument is given it should be an integer and
 the uploads will stop after processing this many sessions
 
```
#!bash
upload_graphs.py <directory> <server uri>?
```

 this script uploads the generated RDF graphs in the given directory
 to the Sesame server. It normally finds the server URI from the 
 config.ini file but this can be overridden on the command line.
 
 
```
#!bash
resample_audio.py <limit>?
```

 this script generates a downsampled version of the audio files for 
 the sessions in a given site directory.   It stores the resulting
 audio in the target directory in a 'downsampled' directory using 
 the new directory structures.  
 
 RDF is generated to describe the resulting audio files and link
 them to the items, this is stored in the 'metadata/downsampled'
 subdirectory of the output directory.
 
 If the downsampled audio file already exists, it isn't generated
 again, but the meta-data will be regenerated.
 
 if the optional limit argument is given it should be an integer and
 the script will stop after processing this many sessions
  
```
#!bash
maus_session.py maus|bpf <speakerlist>?
```

 send audio data to the MAUS forced alignment service and store
 the results as TextGrid files.  The script will use either
 a local installation of MAUS or the MAUS web service
 depending on settings in config.ini.
 
 Reads session data from the triple store and relies on 
 resample_audio.py having been run before it can work.
 
 The script also generates RDF metadata to record the annotation
 files that are generated. This is stored in the 'metadata' directory
 alongside other item metadata in a file with the -m suffix.

 if the optional limit argument is given it should be an integer and
 the script will stop after processing this many sessions
 
 
```
#!bash
harvest_annotations.py <input dir> <ext> <origin>
```

 scan the directories below <input dir> for files with the 
 extension <ext> (eg. .TextGrid) and copy them to the output directory with the
 appropriate directory structure.  <origin> is a string descriptor of the 
 origin of the annotation eg. 'Manual' that will be used to name the output
 directory (under annotation) and as the suffix of the metadata file.
 
 Writes output to the 'annotation/<origin>' subdirectory of the output directory
 with metadata in 'annotation/metadata' with the suffix -<origin>.  
 

```
#!bash
copy_files.py audio|video <limit>?
```

 Copy either audio or video files from the original directory structure
 to the published directory structure.  This script renames session
 and component directories to more meaningful names and refers
 to the versionselect web service to identify the best version of any
 items that have multiple recordings. 
 
 The output is a canonical publishable version of the data written
 to either the 'audio' or 'video' subdirectory of the output 
 directory. 
 
 Metadata files are generated for each item naming the media files
 and linking them to the item records.  These are written with 
 the -files suffix in the metadata subdirectory.
 

Output Directory Structure
-------------------

All outputs are relative to a base output directory configured in 
config.ini (see config.ini.dist for examples).  Below this directory
there will be the following:

- downsampled: contains 16bit/16khz versions of ch6-speaker generated by
   resample_audio.py
   
- MAUS: contains TextGrid annotation files generated by maus_session.py
- BPF: contains .phb annotation files used as input to MAUS generated by
   maus_session.py (with the bpf flag)

- audio: contains the audio files copied over by copy_files.py

- video: will contain the video files copied over by copy_files.py

- metadata: contains the generated metadata for the corpus in RDF format

- annotation: contains any harvested annotation files with metadata in the
  metadata subdirectory


Directory structures within each of these directories follow the same pattern:

<site>/<speaker>/<session>/<component>/

<site> is ANU, CSU etc
<speaker> is 1_1234 etc
<session> is 1, 2, 3
<component> is words-1, digits, re-told-story etc

item file names are as in the original data.


Namespaces
----------

We use a number of namespaces:

Most classes and properties for austalk metadata use the austalk prefix:
PREFIX austalk: <http://ns.austalk.edu.au/>

Entities in the protocol (components, items etc) use this prefix:
PREFIX protocol: <http://id.austalk.edu.au/protocol/>

This is the location of data files:
PREFIX austalkd: <http://data.austalk.edu.au/>

We use AusNC namespace for items and some corpus level metadata
to build in some compatibility where possible:
PREFIX ausnc: <http://ns.ausnc.org.au/schemas/ausnc_md_model/>

FOAF is used for people:
PREFIX foaf: <http://xmlns.com/foaf/0.1/>

OLAC for some metadata properties:
PREFIX olac: <http://www.language-archives.org/OLAC/1.1/>

The GRAF namespace is used in annotation:
PREFIX graf: <http://www.xces.org/ns/GrAF/1.0/>

Various general namespaces:

PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX dc: <http://purl.org/dc/terms/>

Classes
-------

We use the following (OWL) classes:

These classes are used to define the protocol, so for example there are
four instances of Session which define our four sessions.

austalk:Session - a session
austalk:Component - a component
austalk:Item - an item

The actual recordings are represented by instances of these classes, they
are linked to the classes above by the austalk:prototype relation.

austalk:RecordedSession - a group of recorded components corresponding to a Session
austalk:RecordedComponent - a group of AusNCObjects corresponding to a Component
ausnc:AusNCObject - an item (single prompted recording)

foaf:Person - a participant
austalk:RecordingSite - a recording site
austalk:MediaFile - a wav or mp4 file

Entities
--------

Here are some examples that show how things are linked together. 

A participant record links to the recording site, includes a birth year (full date
of birth is not copied over to protect privacy) and a reference to birthPlace as 
a Geonames URI which will resolve to an RDF description of that place (this has
been automatically generated via the geonames search service).

Most properties are simple literal values but some are multi-valued with anonymous 
nodes as values, eg. education_history below.  In the RDF graph, this value 
is a node with properties (age_from, etc).  

    <http://id.austalk.edu.au/participant/2_450> a foaf:Person;
        dbpedia:birthYear 1957;
        austalk:birthPlace <http://sws.geonames.org/2146268>;
        austalk:recording_site <http://id.austalk.edu.au/protocol/site/CSUB>;
        foaf:gender "female" .
        austalk:cultural_heritage "Australian";
        austalk:education_history [ austalk:age_from 40;
                austalk:age_to 45;
                austalk:name "Charles Sturt University";
                austalk:participant_id 2 ],
            [ austalk:age_from 8;
                austalk:age_to 12;
                austalk:name "Palmwoods Primary School";


A recording site has an rdfs:label which is the short name that will be used in
URIs for data.  

    <http://id.austalk.edu.au/protocol/site/CSUB> a austalk:RecordingSite;
        rdfs:label "CSUB";
        austalk:city "Bathurst";
        austalk:institution "Charles Sturt University" .


Sessions and components have names in the protocol namespace 
(http://id.austalk.edu.au/protocol/).  Components are linked to the session via
the dc:isPartOf relation, however in a couple of cases there will be no
link to a session - these are old components that aren't currently used 
in recordings -- we may need to add relations manually depending on how we 
make use of this info.

<http://id.austalk.edu.au/protocol/session/4> a austalk:Session;
    austalk:id 4;
    austalk:name "Session 3.2" .

The shortname property of components will be used in URIs for data files:

<http://id.austalk.edu.au/protocol/component/1> a austalk:Component;
    austalk:id 1;
    austalk:name "Yes/No Opening";
    austalk:shortname "yes-no-opening-1";
    dc:isPartOf <http://id.austalk.edu.au/protocol/session/1> .

Actual sessions and components are instances of RecordedSession and RecordedComponent, 
they point to the session or component definition via the austalk:prototype
relation:

<http://id.austalk.edu.au/session/1_530_3> a austalk:RecordedSession;
    austalk:prototype <http://id.austalk.edu.au/protocol/session/3> .

<http://id.austalk.edu.au/component/1_530_3_8> a austalk:RecordedComponent;
    austalk:prototype <http://id.austalk.edu.au/protocol/component/8>;
    dc:isPartOf <http://id.austalk.edu.au/session/1_530_3> .


Items 
-----

Each item in a component is represented by an instance of austalk:Item:

<http://id.austalk.edu.au/protocol/item/11_10> a austalk:Item;
    austalk:id 10;
    austalk:prompt "Turn left 15  (face +45)  11";
    dc:isPartOf <http://id.austalk.edu.au/protocol/component/11> .

The actual data is represented as instances of AusNCObject and includes all of 
the metadata from the XML file associated with the item.  


  The media property
links to the individual media files.

    <http://id.austalk.edu.au/item/1_178_2_16_001> a ausnc:AusNCObject;
        austalk:basename "1_178_2_16_001";
        austalk:cameraSN0 "11051192";
        austalk:cameraSN1 "11072159";
        
        dc:isPartOf <http://id.austalk.edu.au/component/1_178_2_16>;
        
        austalk:prototype <http://id.austalk.edu.au/protocol/item/16_1>;
        
        austalk:media <http://data.austalk.edu.au/ANUC/2/sentences/1_178_2_16_001-camera-0-left.mp4>,
            <http://data.austalk.edu.au/ANUC/2/sentences/1_178_2_16_001-camera-0-right.mp4>,
            <http://data.austalk.edu.au/ANUC/2/sentences/1_178_2_16_001-ch1-maptask.wav>,
            <http://data.austalk.edu.au/ANUC/2/sentences/1_178_2_16_001-ch2-boundary.wav>,
            <http://data.austalk.edu.au/ANUC/2/sentences/1_178_2_16_001-ch3-strobe.wav>,
            <http://data.austalk.edu.au/ANUC/2/sentences/1_178_2_16_001-ch4-c2Left.wav>,
            <http://data.austalk.edu.au/ANUC/2/sentences/1_178_2_16_001-ch5-c2Right.wav>,
            <http://data.austalk.edu.au/ANUC/2/sentences/1_178_2_16_001-ch6-speaker.wav>,
            <http://data.austalk.edu.au/ANUC/2/sentences/1_178_2_16_001-n-camera-0-left.mp4>,
            <http://data.austalk.edu.au/ANUC/2/sentences/1_178_2_16_001-n-camera-0-right.mp4>,
            <http://data.austalk.edu.au/ANUC/2/sentences/1_178_2_16_001-n-ch1-maptask.wav>,
            <http://data.austalk.edu.au/ANUC/2/sentences/1_178_2_16_001-n-ch2-boundary.wav>,
            <http://data.austalk.edu.au/ANUC/2/sentences/1_178_2_16_001-n-ch3-strobe.wav>,
            <http://data.austalk.edu.au/ANUC/2/sentences/1_178_2_16_001-n-ch4-c2Left.wav>,
            <http://data.austalk.edu.au/ANUC/2/sentences/1_178_2_16_001-n-ch5-c2Right.wav>,
            <http://data.austalk.edu.au/ANUC/2/sentences/1_178_2_16_001-n-ch6-speaker.wav>;
        austalk:prompt "He flew round in an instant to look his attacker square in the eye.";
        austalk:timestamp "Tue Feb 21 10:37:05 2012";
        austalk:version "1.4";
        olac:speaker <http://id.austalk.edu.au/participant/1_178> .
        
For a map-task item, there are two participants, we represent this by having both as
olac:speaker and then entering two role based relations austalk:information_giver and
austalk:information_follower. 

    <http://id.austalk.edu.au/item/1_530_3_8_001> a ausnc:AusNCObject;
    	...
        austalk:information_follower <http://id.austalk.edu.au/participant/4_172>;
        austalk:information_giver <http://id.austalk.edu.au/participant/1_530>;
        austalk:map <http://id.austalk.edu.au/protocol/map/B-architecture>;
        olac:speaker <http://id.austalk.edu.au/participant/1_530>,
            <http://id.austalk.edu.au/participant/4_172> .    
        
    
Media files are identified by a URI that links to the actual file, the properties
describe the file including the type (audio or video) and channel name.  The version
property is used to differentiate between sets of recordings for an item.  
Usually there will be just a version 1 but if there was a second recording that
was judged to be 'good' for the item the audio
and video files will have a suffix of A, B etc and they will have a version number
of 2, 3 etc. 

    <http://data.austalk.edu.au/ANUC/2/sentences/1_178_2_16_001-ch1-maptask.wav> a austalk:MediaFile;
        austalk:channel "ch1-maptask";
        austalk:checksum "f4708488df8438edb1f301dfbc43b683";
        austalk:type "audio";
        austalk:version 1 .