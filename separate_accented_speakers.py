"""Separate out the non-austalk speakers"""
import sys, os, shutil

SPEAKERS = ['1_1027',
        '1_1035','1_1056','1_1077','1_1092',
        '1_1182','1_1258','1_1263','1_179',
        '1_280','1_360','1_431','1_553',
        '1_558','1_682','1_781','1_951',
        '1_959','1_997','2_1033','2_1223',
        '2_1334','2_451','2_560','2_653',
        '2_677','2_888','2_91','2_961',
        '3_1005','3_102','3_1189','3_1309',
        '3_136','3_322','3_347','3_431',
        '3_443','3_579','3_707','3_736',
        '3_751','3_862','3_949','4_1003',
        '4_1028','4_1049','4_1061','4_1299',
        '4_17','4_175','4_384','4_508',
        '4_595','4_732','4_734','4_842',
        '4_964']

basedir = sys.argv[1]
outdir = sys.argv[2]

def move(src,dst):
    print "Move", src, dst
    shutil.move(src, dst)

def copy(src,dst):
    print "Copy", src, dst
    shutil.copytree(src, dst)


for fname in os.listdir(basedir):
    if os.path.splitext(fname)[0] in SPEAKERS:
        move(os.path.join(basedir, fname), os.path.join(outdir, fname))

exit()

# copy all of protocol directory
protdir = os.path.join(basedir, 'metadata/protocol')
targetdir = os.path.join(outdir, 'metadata/protocol')
copy(protdir, targetdir)

# first get participants
partdir = os.path.join(basedir, 'metadata/participants')
targetdir = os.path.join(outdir, 'metadata/participants')
for filename in os.listdir(partdir):
    if os.path.splitext(filename)[0] in SPEAKERS:
        # move to new location
        move(os.path.join(partdir, filename), targetdir)

# now copy over all other files
for topdir in os.listdir(basedir):
    # metadata, audio, downsampled etc
    for sitedir in os.listdir(os.path.join(basedir, topdir)):
        for speakerdir in os.listdir(os.path.join(basedir, topdir, sitedir)):
            if speakerdir in SPEAKERS:
                move(os.path.join(basedir, topdir, sitedir, speakerdir),
                     os.path.join(outdir, topdir, sitedir))
