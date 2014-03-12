import argparse
import os
import sys
import corenlp
import corenlp.pipeline

parser = argparse.ArgumentParser()

parser.add_argument('--inputdir', help='root input location',
                    type=str, required=True)
parser.add_argument('--outputdir', help='directory to write xml',
                    type=str,
                    default='xml')
parser.add_argument('--flat',
                    action='store_true')
args = parser.parse_args()

print 'flat', args.flat
print 'inputdir', args.inputdir

is_flat = args.flat
indir = args.inputdir
outdir = args.outputdir

if not os.path.exists(indir) or not os.path.isdir(indir):
    sys.stderr.write(
        u'Input directory: {} does not exist or is not a directory\n'.format(
            unicode(indir)))
    sys.stderr.flush()
    sys.exit()

print u'Output root directory set to: {}'.format(unicode(outdir))
if is_flat:
    print u'Output directory will be a flat list of processed xml files.'
else:
    print u'Output directory will mirror input directory structure.'

filelist = []

for path, dirs, files in os.walk(indir):
    for fname in files:
        filelist.append(os.path.join(path, fname))


corenlp.pipeline.files2dir(filelist, outdir, annotators=['tokenize',
                                                         'ssplit',
                                                         'pos',
                                                         'lemma'])

import shutil
if is_flat:
    for fname in os.listdir(outdir):
        if fname.endswith('.txt.xml'):
            new_fname = fname.replace('.txt.xml', '.xml')
            src = os.path.join(outdir, fname)
            dest = os.path.join(outdir, new_fname)
            shutil.move(src, dest)

if not is_flat:
    for fpath in filelist:
        rel_path = os.path.normpath(fpath.split(indir)[1])
        if rel_path[0] == os.path.sep:
            rel_path = rel_path[1:]
        dest = os.path.join(outdir,
                            os.path.splitext(rel_path)[0] + '.xml')
        src = os.path.join(outdir,
                           os.path.basename(fpath) + '.xml')
        if not os.path.exists(os.path.split(dest)[0]):
            os.makedirs(os.path.split(dest)[0])  
        shutil.move(src, dest)
