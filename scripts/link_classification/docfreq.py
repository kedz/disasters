import argparse
import os
import disasters.document
import pickle

def _parse_cmdline():
    parser = argparse.ArgumentParser()
    parser.add_argument(u'-id', u'--inputdir',
                        help=u'input directory containing corenlp xml files',
                        type=unicode, required=True)
    
    parser.add_argument(u'-of', u'--outputfile', 
                        help=u'Output file to write term '
                             + u'doc frequencies object',
                        type=unicode, required=True)

    args = parser.parse_args()
    idir = args.inputdir
    ofile = args.outputfile

    if not os.path.exists(idir) or not os.path.isdir(idir):
        import sys
        errmsg = (u'Input directory argument {} either does not exist '
                 + u'or is not a directory!\n').format(idir)
        sys.stderr.write(errmsg)
        sys.stderr.flush()
        sys.exit()

    odir = os.path.split(ofile)[0]
    if odir != '' and not os.path.exists(odir):
        os.makedirs(odir)

    if os.path.isdir(ofile):
        import sys
        errmsg = u'Output file argument {} is a directory!\n'.format(idir)
        sys.stderr.write(errmsg)
        sys.stderr.flush()
        sys.exit()

    return idir, ofile

def build_filelist(idir):
    
    return [os.path.join(path, fname) 
            for path, dirs, fnames in os.walk(idir)
            for fname in fnames]
    

def main():

    idir, ofile = _parse_cmdline()

    print u'Ingesting all .xml files below {}...'.format(idir)

    filelist = build_filelist(idir)
    df = disasters.document.DocFreqs(filelist)

    print u'Writing output to {}'.format(ofile)
    with open(ofile, 'wb') as f:
        pickle.dump(df, f)

if __name__ == u'__main__':
    main()
