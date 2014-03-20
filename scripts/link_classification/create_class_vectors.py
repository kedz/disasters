import os
import argparse
import disasters.data as data
from disasters.document import WCDocument
import re
import codecs
import pickle
import scipy as sp
from multiprocessing import Pool
from math import log, sqrt
import sys

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
                        help=u'DocFreqs object in yaml',
                        type=unicode, required=True)

    
    parser.add_argument('-n', '--normalize',
                        help=u'Subtract mean values from vectors.',
                        action='store_true',
                        default=False)

    args = parser.parse_args()
    idir = args.inputdir
    ofile = args.outputfile
    dffile = args.docfreqs
    norm = args.normalize
    
    if not os.path.exists(idir) or not os.path.isdir(idir):
        import sys
        sys.stderr.write((u'Input directory argument {} either does not exist '
                          + u'or is not a directory!\n').format(idir))
        sys.stderr.flush()
        sys.exit()

    if os.path.isdir(ofile):
        import sys
        sys.stderr.write((u'Output file argument '
                          + u'{} is a directory!\n').format(idir))
        sys.stderr.flush()
        sys.exit()

    odir = os.path.split(ofile)[0]
    if odir != '' and not os.path.exists(odir):
        os.makedirs(odir)

    if not os.path.exists(dffile) or not os.path.isfile(dffile):
        import sys
        sys.stderr.write((u'DocFreqs file argument '
                          + u'{} does not exists or '
                          + ' is a directory!\n').format(dffile))
        sys.stderr.flush()
        sys.exit()

    return idir, ofile, dffile, norm

def dfile2dname(dfilename):
    dname = dfilename.split(u'_', 7)[7]
    m = re.match(r'(.+?)_(impact|history|abstract)', dname)
    if m:
        dname = m.group(1)
    return dname

def file2vector(filename, df):
    doc = WCDocument(filename)
    vsize = df.vocab_size
    v = sp.sparse.lil_matrix((1, vsize))

    norm = 0
    for word, count in doc.wc_dict().items():
        idx = df.word_index(word)
        if idx is not None:
            tfidf = (1 + log(count, 2)) * log(float(df.ndocs) / df[word])
            v[0, idx] = tfidf
            norm += tfidf ** 2
    norm = sqrt(norm)
    if norm != 0:
        v /= norm
    return v

def _load_jobs(idir, df):
    jobs = []
    for cat in data.get_cats():
        catdir = os.path.join(idir, cat)
        if not os.path.exists(catdir) or not os.path.isdir(catdir):
            import sys
            sys.stderr.write(u'{} does not exist or is not a directory.\n')
            sys.stderr.flush()
            continue
        for disasterfile in os.listdir(catdir):
            dpath = os.path.join(catdir, disasterfile)
            dname = dfile2dname(disasterfile)
            jobs.append((cat, dname, dpath, df)) 
    return jobs

def vector_maker(datum):
    try:
        dclass, dname, dpath, df, u = datum
        
        doc = WCDocument(dpath)
        v = sp.sparse.lil_matrix((1, df.vocab_size))

        norm = 0
        for word, count in doc.wc_dict().items():
            idx = df.word_index(word)
            if idx is not None:
                tfidf = (1 + log(count, 2)) * log(float(df.ndocs) / df[word])
                if u is not None:
                    tfidf -= u[0, idx]
                v[0, idx] = tfidf
            norm += tfidf ** 2
        norm = sqrt(norm)
        if norm != 0:
            v /= norm
 
        return {'class': dclass, 
                'disaster': dname,
                'file': dpath,
                'vector': v}

    except KeyboardInterrupt, e:
        pass

def create_vectors(jobs, df, pool, u, ofile):
    try:
        jobs = [(dclass, dname, dpath, df, u)
                for (dclass, dname, dpath, df) in jobs]
        njobs = len(jobs)
        with codecs.open(ofile, 'wb') as pf:
            pickle.dump(njobs, pf)
            results = pool.imap_unordered(vector_maker, jobs)
            for i, result in enumerate(results, 1):
                pickle.dump(result, pf)
                per = 100 * (float(i) / njobs)
                sys.stdout.write(u'\rPercent Complete: {:2.3f}%'.format(per))
                sys.stdout.flush()
            sys.stdout.write(u'\rPercent Complete: 100%    \n')
            sys.stdout.flush()

    except KeyboardInterrupt:
        sys.stdout.write(u'\rPercent Complete: {:2.3f}%  \n'.format(per))
        sys.stdout.write(u'Shutting down.\n')
        sys.stdout.flush()
        sys.exit()


def mean_vec_worker(datum):
    try:
        dclass, dname, dpath, df = datum
        doc = WCDocument(dpath)

        results = [] 
        for word, count in doc.wc_dict().items():
            idx = df.word_index(word)
            if idx is not None:
                tfidf = (1 + log(count, 2)) * log(float(df.ndocs) / df[word])
                results.append((0, idx, tfidf))
        return results 
    except KeyboardInterrupt, e:
        pass
 
def compute_mean_vector(jobs, df, pool):
    try:
        u = sp.zeros((1, df.vocab_size)) 
        njobs = len(jobs)
        results = pool.imap_unordered(mean_vec_worker, jobs)
        for idx, result in enumerate(results, 1):
            for i, j, val in result:
                u[i, j] += val
                
            per = 100 * (float(idx) / njobs)
            sys.stdout.write(u'\rComputing mean vector: {:2.3f}%'.format(per))
            sys.stdout.flush()
        
        u /= float(njobs)

        sys.stdout.write(u'\rComputing mean vector: 100%    \n')
        sys.stdout.flush()
        
        return u

    except KeyboardInterrupt:
        sys.stdout.write(u'\rComputing mean vector: {:2.3f}%  \n'.format(per))
        sys.stdout.write(u'Shutting down.\n')
        sys.stdout.flush()
        sys.exit()


def main():

    idir, ofile, dffile, norm = _parse_cmdline()

    print u'Loading doc-freqs file {}...'.format(dffile)
    with open(dffile, 'rb') as f:
        df = pickle.load(f)    

    print u'Reading input directory: {}'.format(idir)
    jobs = _load_jobs(idir, df)

    # Do the work.
    pool = Pool(4)
    if norm:
        u = compute_mean_vector(jobs, df, pool)
    else:
        u = None

    create_vectors(jobs, df, pool, u, ofile)

    print u'Complete!'


if __name__ == u'__main__':
    main()
