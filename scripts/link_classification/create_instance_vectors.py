import sys
import os
import argparse
import disasters.data as data
from disasters.document import WCDocument
import codecs
import pickle
import scipy as sp
from multiprocessing import Pool
import cPickle as pickle
from math import sqrt

def _parse_cmdline():

    parser = argparse.ArgumentParser()
    parser.add_argument('-id', '--inputdir',
                        help=u'input directory containing corenlp xml files',
                        type=unicode, required=True)
    
    parser.add_argument('-of', '--outputfile', 
                        help=u'Output file to write category type, \
                              disaster name, and instance path.',
                        type=unicode, required=True)

    parser.add_argument('-df', '--docfreqs',
                        help=u'Pickled DocFreqs object',
                        type=unicode, required=True)


    args = parser.parse_args()
    idir = args.inputdir
    ofile = args.outputfile
    dffile = args.docfreqs

    if not os.path.exists(idir) or not os.path.isdir(idir):
        sys.stderr.write((u'Input directory argument {} either does not exist '
                          + u'or is not a directory!\n').format(idir))
        sys.stderr.flush()
        sys.exit()

    if os.path.isdir(ofile):
        sys.stderr.write((u'Output file argument '
                          + u'{} is a directory!\n').format(idir))
        sys.stderr.flush()
        sys.exit()

    odir = os.path.split(ofile)[0]
    if odir != '' and not os.path.exists(odir):
        os.makedirs(odir)

    if not os.path.exists(dffile) or not os.path.isfile(dffile):
        sys.stderr.write((u'DocFreqs file argument '
                          + u'{} does not exists or '
                          + ' is a directory!\n').format(dffile))
        sys.stderr.flush()
        sys.exit()


    return idir, ofile, dffile

def ddir2dname(ddir):
    dname = ddir.split(u'_', 7)[7]
    return dname

def file2vector(filename, df):
    doc = WCDocument(filename)
    vsize = df.vocab_size
    v = sp.sparse.lil_matrix((vsize, 1))

    norm = 0
    for word, count in doc.wc_dict().items():
        idx = df.word_index(word)
        if idx is not None:
            v[idx] = 1
            norm += 1
    norm = sqrt(norm)
    if norm != 0:
        v /= norm
    return v.tocsr()
    

def _load_jobs(idir, df):
    jobs = [] 
    for cat in data.get_cats():
        catdir = os.path.join(idir, cat)
        if not os.path.exists(catdir) or not os.path.isdir(catdir):
            import sys
            sys.stderr.write(u'{} does not exist or is not a directory.\n')
            sys.stderr.flush()
            continue
        for disasterdir in os.listdir(catdir):
            dpath = os.path.join(catdir, disasterdir)
            for fname in os.listdir(dpath):
                fpath = os.path.join(dpath, fname)
                dname = ddir2dname(disasterdir)
                jobs.append((cat, dname, fpath, df))
    return jobs

def worker(datum):
    try:
        dclass, dname, dpath, df = datum
        vector = file2vector(dpath, df)
        return {'class': dclass, 
                'disaster': dname,
                'file': dpath,
                'vector': vector}
    except KeyboardInterrupt, e:
        pass

def main():
    idir, ofile, dffile = _parse_cmdline()

    print u'Loading doc-freqs file {}...'.format(dffile)
    with open(dffile, 'rb') as f:
        df = pickle.load(f)    

    print u'Reading input directory: {}'.format(idir)
    jobs = _load_jobs(idir, df)

    # Do the work.
    pool = Pool(4)
    njobs = len(jobs)

    try:
        import sys
        with codecs.open(ofile, 'wb') as pf:
            pickle.dump(njobs, pf)
            results = pool.imap_unordered(worker, jobs)
            for i, result in enumerate(results, 1):
                pickle.dump(result, pf)
                per = 100 * (float(i) / njobs)
                sys.stdout.write(u'\rPercent Complete: {:2.3f}%'.format(per))
                sys.stdout.flush()
            sys.stdout.write(u'\rPercent Complete: 100%    \n')
            sys.stdout.flush()

    except KeyboardInterrupt:
        sys.stdout.write(u'\rPercent Complete: {:2.3f}%    \n'.format(per))
        sys.stdout.write(u'Shutting down.\n')
        sys.stdout.flush()
        sys.exit()

    print u'Complete!'

if __name__ == u'__main__':
    main()
