import argparse
import os
import narrative
import cPickle as pickle

parser = argparse.ArgumentParser()
parser.add_argument('-id', '--inputdir', help='input directory containing corenlp xml files',
                    type=unicode, required=True)

parser.add_argument('-p', '--pickle-file', help='Filename for pickled pmi counts. If none exists will make new. If file exists, this file will be updated.',
                    type=unicode, required=True)

parser.add_argument('-r', '--recursive', help='recursively descend through inputdir',
                    action='store_true')

args = parser.parse_args()

idir = args.inputdir
pfile = args.pickle_file
pdir = os.path.split(pfile)[0]

if not os.path.exists(idir) or not os.path.isdir(idir):
    import sys
    sys.stderr.write(u'Input directory argument {} either does not exist or is not a directory!\n'.format(idir))
    sys.stderr.flush()
    sys.exit()

if pdir != '' and not os.path.exists(pdir):
    os.makedirs(pdir)

if os.path.exists(pfile):
    print u'Loading pmi counts from {}'.format(pfile)
    with open(pfile, 'rb') as f:
        pmis = pickle.load(f)
else:
    print u'Creating new pmi counts.' 
    pmis = narrative.NarrativeBank()

print u'Building filelist at location: {}...'.format(idir)

# Build a filelist, by either walking the input directory recursively or
# listing all files in the input directory.
filelist = []
if args.recursive:
    for path, dirs, fnames in os.path.walk(idir):
        for fname in fnames:
            fpath = os.path.join(path, fname)
            filelist.append(fpath)
else:
    for fname in os.listdir(idir):
        fpath = os.path.join(idir, fname)
        if os.path.isfile(fpath):
            filelist.append(fpath)

import sys
sys.stdout.write(u'Building pmi counts... (0.00%)')
sys.stdout.flush()
nfiles = len(filelist)
for i, fname in enumerate(filelist, 1):
    pmis.build([fname])
    sys.stdout.write('\rBuilding pmi counts... ({:3.2f}%)'.format(100 * float(i) / nfiles))
    sys.stdout.flush()

print u'\nPickling pmi counts to {}'.format(pfile)
with open(pfile, 'wb') as f:
    pickle.dump(pmis, f)
print u'Complete!'
