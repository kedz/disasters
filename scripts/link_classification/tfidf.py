import argparse
import os
import sys
import corenlp
from collections import defaultdict
import cPickle as pickle


parser = argparse.ArgumentParser()
parser.add_argument('-id', '--inputdir', help='input directory containing corenlp xml files',
                    type=unicode, required=True)

parser.add_argument('-p', '--pickle-file', help='Filename for pickled pmi counts. If none exists will make new. If file exists, this file will be updated.',
                    type=unicode, required=True)

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
    print u'Loading doc freq and term freq from {}'.format(pfile)
    with open(pfile, 'rb') as f:
        termfq, docfq, ndocs = pickle.load(f)
else:
    print u'Creating new tf-idf counts.' 
    termfq = {}
    docfq = defaultdict(int)
    ndocs = 0

nifiles = len(os.listdir(idir))
for i, fname in enumerate(os.listdir(idir), 1):
    fpath = os.path.join(idir, fname)
    fname
    doc = corenlp.Document(fpath)
    unique_lem = set()
    termfq[fname] = defaultdict(int)
    for s in doc:
        for t in s:
            termfq[fname][t.lem.lower()] += 1
            unique_lem.add(t.lem.lower())

    for lem in unique_lem:
        docfq[lem] += 1
    ndocs += 1
    sys.stdout.write('\rBuilding tf-idf counts... ({:3.2f}%)'.format(
        100 * float(i) / nifiles))
    sys.stdout.flush()

print u'\nPickling tf-idf counts to {}'.format(pfile)
with open(pfile, 'wb') as f:
    pickle.dump((termfq, docfq, ndocs), f)
print u'Complete!'


