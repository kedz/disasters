import argparse
import os
import sys
import corenlp
from collections import defaultdict, namedtuple
import cPickle as pickle
import numpy as np
from math import log
import scipy

def vector(lems, tfidf, vmap, norm=True):
    vsize = len(vmap)
    vctr = np.zeros([vsize])
    for lem in lems:
        if lem in vmap:
            idx = vmap[lem]
            vctr[idx] = log((float(tfidf.ndocs) / tfidf.docfq[lem]), 2)            

    if norm:
        l2 = scipy.linalg.norm(vctr)
        if l2 != 0:
            vctr /= l2
    return vctr

parser = argparse.ArgumentParser()
parser.add_argument('-id', '--inputdir', help='input directory containing corenlp xml files',
                    type=unicode, required=True)

parser.add_argument('-pf', '--picklefile',
                    help='pickled tfidf counts for wiki section',
                    type=unicode, required=True)

args = parser.parse_args()

idir = args.inputdir
pfile = args.picklefile

if not os.path.exists(idir) or not os.path.isdir(idir):
    import sys
    sys.stderr.write(u'Input directory argument {} either does not exist or is not a directory!\n'.format(idir))
    sys.stderr.flush()
    sys.exit()
if not os.path.exists(pfile) or os.path.isdir(pfile):
    import sys
    sys.stderr.write(u'Pickle file argument {} either does not exist or is a directory!\n'.format(idir))
    sys.stderr.flush()
    sys.exit()

TFIDF = namedtuple('TFIDF', ['termfq', 'docfq', 'ndocs'])
#for pfile in os.listdir(pdir):
with open(pfile, 'rb') as p:
    print u'Loading {} file...'.format(pfile)
    termfq, docfq, ndocs = pickle.load(p)
    tfidf = TFIDF(termfq, docfq, ndocs)
        
# Assign each unique word in the vocabulary to an index.
vmap = {}
#rel_words = ['hurricane', 'tropical', 'storm', 'typhoon', 'cyclone', 'wind', 'damage', 'sandy']
secdocs = {}
vidx = 0
for lem, cnt in tfidf.docfq.items():
    if lem not in vmap and cnt > 2: #and lem in rel_words:
        vmap[lem] = vidx
        vidx += 1

print u'Constructed a vocabulary of {} tokens'.format(vidx)

doc_vcts = []
for dname, tf in tfidf.termfq.items():
    lems = set([lem for lem in tf.keys()])
    v = vector(lems, tfidf, vmap)
    disaster = u'_'.join(dname.split('_')[0:-1])
    doc_vcts.append((disaster, v))


ncorrect = 0
ninstances = 0

dataX = []
dataY = []
for path, subdirs, fnames in os.walk(idir):
    #bname = os.path.split(path)[1]
    for fname in fnames:
        #disaster = u'_'.join(fname.split('_')[0:-1])
        #dataY.append(disaster) 
        disaster = fname
        doc = corenlp.Document(os.path.join(path, fname))
        lems = set()
        for s in doc:
            for t in s:
                lems.add(t.lem.lower())
        v = vector(lems, tfidf, vmap)
        
        maxprod = 0
        max_disaster_name = ''
        for disaster_name, dvctr in doc_vcts:
            cossim = dvctr.dot(v)
            if cossim > maxprod:
                maxprod = cossim
                max_disaster_name = disaster_name
        
        dataX.append(v)
        if max_disaster_name != '':
            max_disaster_name = max_disaster_name.split('_', 7)[7]

        print  'File: {} \tAssignment: {}'.format(disaster, max_disaster_name)
        
        y = u'_'.join(disaster.split('_')[0:-1])
        if y == max_disaster_name:
            ncorrect += 1
        ninstances += 1 


print u'Correct: {}'.format(ncorrect)
print u'Total: {}'.format(ninstances)
print u'Acc: {:2.3f}%'.format( 100 * float(ncorrect) / ninstances) 

#import numpy as np

#for i, x in enumerate(dataX):
#    print os.path.basename(x)
#    for secname, tfidf in counts.items():
#        print '\t', secname
#        v = vector(corenlp.Document(x), tfidf, vmaps[secname])
#        for lem, idx in vmap.items():
#            print u'{}: {:3.3f}'.format(lem, v[idx]), 
#        print 
    
 
