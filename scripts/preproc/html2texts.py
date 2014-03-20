import disasters.data as data
import disasters.toctree as toctree
import argparse
import os
import textwrap
import re
import codecs
from multiprocessing import Pool
import time

def write_single_element(element):
    texts = [textwrap.fill(unicode(item)) 
             for item in element.items
             if item.strip() != u'']
    outtext = u'\n\n'.join(texts)
    return outtext

def write_subsection(element, f):

    raw_text = []
    for node in element.dfs_iter():    
        for item in node.items:
            raw_text.append(item)
    
    texts = [textwrap.fill(unicode(text)) 
             for text in raw_text
             if text.strip() != u'']
    outtext = u'\n\n'.join(texts)
    f.write(outtext)
    f.flush()

def worker(datum):
    try:
        outdir, cat, fpath = datum
        
        fname = os.path.basename(fpath)
        
        root = None
        with open(fpath, 'r') as f:
            root = toctree.from_wiki(f)
            outpath = os.path.join(outdir, cat, 'abstract_text')
            outfile = os.path.join(outpath,
                                   fname.replace(u'.html', u'_abstract.txt'))
            roottext = write_single_element(root)
            if roottext != '':
                with codecs.open(outfile, u'w', u'utf-8') as out:
                    out.write(roottext)
                    out.flush()
        
        if root is None:
            return

        itrees = toctree.subtrees_with_label_re(root,
                                                re.compile(r'impact', re.I))
        
        for itree in itrees:
            if sep_sub_file:
                outpath = os.path.join(outdir, cat, u'impact_text')    
                idx = 0
                for child in itree.dfs_iter():
                    text = write_single_element(child)
                    if text != '':
                        txtfname = fname.replace(u'.html',
                                                 u'_impact_{}.txt'.format(idx))
                        outfname = os.path.join(outpath, txtfname)
                        with codecs.open(outfname, u'w', u'utf-8') as out:
                            out.write(text)
                            out.flush()
                        idx += 1
            else:
                outpath = os.path.join(outdir, cat, u'impact_text')    
                txtfname = fname.replace(u'.html',
                                         u'_impact.txt')
                outfname = os.path.join(outpath, txtfname)
                with codecs.open(outfname, u'w', u'utf-8') as out:
                    write_subsection(itree, out)

        itrees = None
        itree = None
        htrees = toctree.subtrees_with_label_re(root,
                                                re.compile(r'history', re.I))
     
        for htree in htrees:
            if sep_sub_file:
                outpath = os.path.join(outdir, cat, u'history_text')    
                idx = 0
                for child in htree.dfs_iter():
                    text = write_single_element(child)
                    if text != '':
                        txtfname = fname.replace(u'.html',
                                                 u'_history_{}.txt'.format(idx))
                        outfname = os.path.join(outpath, txtfname)
                        with codecs.open(outfname, u'w', u'utf-8') as out:
                            out.write(text)
                            out.flush()
                        idx += 1
            else:
                outpath = os.path.join(outdir, cat, u'history_text')    
                txtfname = fname.replace(u'.html',
                                         u'_history.txt')
                outfname = os.path.join(outpath, txtfname)
                with codecs.open(outfname, u'w', u'utf-8') as out:
                    write_subsection(htree, out)
    except KeyboardInterrupt, e:
        pass

parser = argparse.ArgumentParser()
parser.add_argument('--outputdir', help='directory to write text',
                    type=str)
parser.add_argument('--separate-subsection-files',
                    action='store_true')
args = parser.parse_args()

sep_sub_file = args.separate_subsection_files

if args.outputdir is None:
    outdir = 'disaster_text'
else:
    outdir = args.outputdir

for cat in data.get_cats():
    abstract = os.path.join(outdir, cat, 'abstract_text')
    if not os.path.exists(abstract):
        os.makedirs(abstract)
    impact = os.path.join(outdir, cat, 'impact_text')
    if not os.path.exists(impact):
        os.makedirs(impact)
    history = os.path.join(outdir, cat, 'history_text')
    if not os.path.exists(history):
        os.makedirs(history)
 
print u'Output root directory set to: {}'.format(unicode(outdir))

import sys
pool = Pool(4)

jobs = []
for cat in data.get_cats():
    for datum in data.get_html(cat, latest_first=True):
        fpath = datum[0]
        jobs.append((outdir, cat, fpath))

njobs = len(jobs)
try:
    results = pool.imap_unordered(worker, jobs)
    for i, result in enumerate(results, 1):
        per = 100 * (float(i) / njobs)
        sys.stdout.write(u'\rPercent Complete: {:2.3f}%'.format(per))
        sys.stdout.flush()
    sys.stdout.write(u'\rPercent Complete: 100%\n')
    sys.stdout.flush()
except KeyboardInterrupt:
    sys.stdout.write(u'\rPercent Complete: {:2.3f}%  \n'.format(per))
    sys.stdout.write(u'Shutting down.\n')
    sys.stdout.flush()
