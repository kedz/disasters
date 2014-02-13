from os import getenv, listdir, remove, makedirs
from os.path import join, split, exists, basename
import re
from datetime import datetime
from collections import namedtuple, defaultdict
import EventParser.tree as ept
from tempfile import NamedTemporaryFile, mkdtemp
from subprocess import call, check_output
import corenlp_xml
import shutil
import pickle
import cPickle
from multiprocessing import Pool
import clustertree
import corenlp_xml as cnlp

_data_dir = getenv('EVENTPARSER_DATA', '.')
_pickle_dir = join(_data_dir, 'preprocessed')
_wiki_disaster_dir = join(_data_dir, 'disasters')
_wiki_html_dir = join(_data_dir, 'html')
_wiki_impact_links_dir = join(_data_dir, 'linked_pages')

file_pattern = re.compile(r'(\d\d\d\d)_(\d\d)_(\d\d)_(\d\d)_(\d\d)_(\d\d)_(\d+)_(.*?)\.html')


def get_preprocessed_wiki_events(category):
    event_dir = join(get_pickle_dir(), category)
    for fname in listdir(event_dir):
        pkl_file = open(join(event_dir, fname), 'rb')
        wiki = cPickle.load(pkl_file)
        pkl_file.close()
        yield wiki

def get_disasters(disaster_type):
    disasters = []
    dfile = open(join(_wiki_disaster_dir, '{}.txt'.format(disaster_type)), 'r')
    for line in dfile:
        title, date_str = line.strip().split('\t')
        date = datetime.strptime(date_str, "%m/%d/%y")
        disasters.append((title, date))
    dfile.close()
    return disasters

def get_wiki_html_dir(disaster):
    return join(_wiki_html_dir, disaster)

def get_pickle_dir():
    return _pickle_dir

def get_linked_page_dir(category):
    d = join(_wiki_impact_links_dir, category)
    if not exists(d):
        makedirs(d)
    return d

def set_data_dir(directory):
    _data_dir = directory

def get_html(category, num_revs=1, latest_first=False):
    d = join(_wiki_html_dir, category)
    articles = defaultdict(list)
    for fname in listdir(d):
        m = file_pattern.match(fname)
        if m:
            rdate = datetime(year=int(m.group(1)),
                             month=int(m.group(2)),
                             day=int(m.group(3)),
                             hour=int(m.group(4)),
                             minute=int(m.group(5)),
                             second=int(m.group(6)))

            articles[m.group(8)].append((rdate, join(d, fname)))

    pages = []
    for key in articles.keys():
        revs = articles[key]
        revs.sort(key=lambda x: x[0], reverse=latest_first)
        pages.append([rev[1] for rev in revs[0:num_revs]])
    return pages

def get_cat2trees_dict(corenlp=True):
    num_revs = 1
    latest_first = True
    cats = ['cyclones', 'hurricanes', 'tropicalstorms', 'typhoons']

    q = []
    for cat in cats:
        entities = get_html(cat,
                            num_revs=num_revs,
                            latest_first=latest_first)
        
        for revs in entities:
            for html in revs:
                q.append((cat, html))

    pool = Pool(processes=4)       # start 4 worker processes
    results = pool.map(_load_tree_worker, q)

    imp_trees = defaultdict(list)
    for result in results:
        for item in result:
            imp_trees[item[0]].append(item[1])
    for k in imp_trees.keys():
        imp_trees[k].sort(key=lambda x: x[1].n_nodes()) 

    if corenlp:
        process_toctree_dict(imp_trees)
    return imp_trees

def _load_tree_worker(p):
    cat = p[0]
    html = p[1]
    c = clustertree.from_wiki(open(html, 'r'))
    #itrees = clustertree.subtrees_with_label_re(c, re.compile(r'impact', re.I))
    #return [(cat, (html.split('/')[-1], it)) for it in itrees]
    return [(cat, (html.split('/')[-1], c))]

def process_toctree_dict(cat2trees_dict):

    tmpdir = mkdtemp()
    filelist = []
    for cat in cat2trees_dict.keys():
        for label, tree in cat2trees_dict[cat]:
            for n in tree.bfs_iter():
                n.items_meta = []
                for i in n.items:
                    txtfile = NamedTemporaryFile(delete=False)
                    txtfile.write(i)
                    txtfile.flush()
                    txtfile.close()
                    n.items_meta.append('{}.xml'.format(basename(txtfile.name)))
                    filelist.append(txtfile.name)
   
    annotators = ['tokenize', 'ssplit', 'pos', 'lemma', 'ner', 'parse', 'dcoref']
    cnlp.run_pipeline(annotators,
                      filelist,
                      tmpdir,
                      mem='2000m',
                      threads=3,
                      corenlp_dir='/home/chris/tools/nlp/stanford-corenlp-full-2013-06-20')

    for cat in cat2trees_dict.keys():
        for label, tree in cat2trees_dict[cat]:
            for n in tree.bfs_iter():
                for i, f in enumerate(n.items_meta):
                    fl = open(join(tmpdir, f))
                    cnlpstr = ''.join(fl.readlines())
                    fl.close()
                    n.items_meta[i] = cnlpstr

    for fname in filelist:
        remove(fname)
    shutil.rmtree(tmpdir)


class Revision:

    def __init__(self, rev_id, rev_datetime, rev_file):
        self.id = rev_id
        self.datetime = rev_datetime
        self.file = rev_file
        self.p_indices = []
        self.corenlp_string = None
        self.subsections = None

    def __str__(self): return 'WikiRevision {} - {}'.format(self.id, self.datetime)
    
    def tree(self):
        f = open(self.file, 'r') 
        tree = ept.make_tree_from_wiki(f, prune_wiki=True)
        f.close()
        return tree

    def add_document(self, doc):
        self.cnlp_doc = doc

    def add_paragraphs(self, grafs):
        self.paragraphs = grafs

class WikiEvent:
    def __init__(self, event_title, category):
        self.title = event_title
        self.revisions = []
        self._load_event(event_title, category)

    def __str__(self):
        return 'WikiEvent: {} ({} revision(s))'.format(self.title, len(self.revisions))
    
    def __getitem__(self, index):
        return self.revisions[index]    
       
    def __iter__(self):
        return iter(self.revisions)
        
    def _load_event(self, event_title, category):
        html_dir = get_wiki_html_dir(category)
        for html in listdir(html_dir):
            if html.endswith('{}.html'.format(event_title)):
                m = file_pattern.match(html)
                if m:
                    mints = [int(i) for i in m.groups()[:-1]]
                    rev_date = datetime(mints[0], mints[1], mints[2], mints[3], mints[4], mints[5])
                    rev_id = m.groups()[-2]
                    self.revisions.append(Revision(rev_id, rev_date, join(html_dir, html)))
        self.revisions.sort(key=lambda rev: rev.datetime)                            

    
def get_wiki_event_revisions(category):
    event_titles = set()
    for html in listdir(get_wiki_html_dir(category)):
        m = file_pattern.match(html)
        if m:
            title = m.groups()[-1]                
            event_titles.add(title)
    return [WikiEvent(title, category) for title in event_titles]


def preprocess_wikis(wiki_data, output_dir, verbose=False):

    tmp_dir = '/tmp/event_parses'
    if not exists(tmp_dir):
        makedirs(tmp_dir)
    
    graff_annots = _make_paragraph_annotations(wiki_data, tmp_dir, verbose)
    _pre_process_wiki_event(wiki_data, graff_annots, output_dir, tmp_dir, verbose)
   
    shutil.rmtree(tmp_dir) 


def _pre_process_wiki_event(wiki_data, graf_annots, output_dir, tmp_dir, verbose=False):
    wiki_files = {}
        
    if verbose:
        print 'EventParser.data: Generating full document parse and coref...'
    for wiki in wiki_data:
        for rev in wiki.revisions:
            rtree = rev.tree()
            hftree = rtree.header_free_tree()
            txt = hftree.document_string()
            txtfile = NamedTemporaryFile(delete=False, dir=tmp_dir)
            txtfile.write(txt)
            txtfile.flush()
            txtfile.close()
            wiki_files[rev.id] = txtfile.name
            
    if verbose:
        print 'EventParser.data: Writing corenlp file list...'
    filelist = _filelist(wiki_files.values())
    if verbose:
        print 'EventParser.data: Parsing documents...'
    shellcmd = _corenlp_cmd('tokenize,ssplit,pos,lemma,ner,parse,dcoref', filelist, tmp_dir)
    output = check_output(shellcmd, shell=True)
    print output


    proc_wiki_data = []

    pickle_dir = join(get_pickle_dir(), output_dir)
    if not exists(pickle_dir):
        makedirs(pickle_dir)
        
    for wiki in wiki_data:
        if verbose:
            print 'EventParser.data: Merging parse and paragraph annotations...'
        for rev in wiki.revisions:
            xml = '{}.xml'.format(wiki_files[rev.id])
            
            f = open(xml,'r')
            rev.corenlp_string = ''
            for line in f:
                rev.corenlp_string += line
            f.close()
            rev.p_indices = graf_annots[rev.id]

        fname = join(pickle_dir, wiki.title)
        if verbose:
            print 'EventParser.data: Writing pickle file to {}'.format(fname)
        f = open(fname, 'wb')
        pickle.dump(wiki, f, 2)
        f.close()
        


def _make_paragraph_annotations(wiki_data, tmp_dir, verbose=False):
    graf_files = {}
    
    if verbose:
        print 'EventParser.data: Generating paragraph alignments...'
    for wiki_inst in wiki_data:
        if verbose:
            print 'EventParser.data: \t{}'.format(wiki_inst.title)    
        for rev in wiki_inst.revisions:
            rtree = rev.tree()
            hftree = rtree.header_free_tree()
            grafs = hftree.document_string().split('\n\n')
            
            for i, p in enumerate(grafs, 1):
                pfile = NamedTemporaryFile(delete=False, dir=tmp_dir)
                pfile.write(p)
                pfile.flush()
                pfile.close()
                graf_files['{} {}'.format(rev.id, i)] = pfile.name
    if verbose:
        print 'EventParser.data: Writing corenlp file list...'
    filelist = _filelist(graf_files.values())
    if verbose:
        print 'EventParser.data: Annotating paragraphs...'
    output_dir = '/home/chris/Desktop/coreout'
    shellcmd = _corenlp_cmd('tokenize,ssplit', filelist, tmp_dir)
    output = check_output(shellcmd, shell=True)
    print output

    graf_annots = _get_paragraph_line_numbers(wiki_data, tmp_dir, graf_files)

    for f in graf_files.values():
        remove(f)
        #fname = split(f)[-1]
        xml_file = '{}.xml'.format(f)
        remove(xml_file)

    return graf_annots    
             
def _filelist(files):
    filelist = NamedTemporaryFile(delete=False)
    for f in files:
        filelist.write(f+'\n')
        filelist.flush()
    filelist.close()
    return filelist.name



def _corenlp_cmd(annotators, input_files, output_dir):
    java = 'java'
    jars = ['joda-time.jar', 'jollyday.jar', 'stanford-corenlp-3.2.0.jar',
           'stanford-corenlp-3.2.0-models.jar', 'xom.jar']
    corenlp_dir = '/home/chris/tools/nlp/stanford-corenlp-full-2013-06-20'
    classpath = ':'.join([join(corenlp_dir, jar) for jar in jars])           
    pipeline = 'edu.stanford.nlp.pipeline.StanfordCoreNLP'
    cmd = '{} -Xmx2500m -cp {} {} -annotators {} -filelist {} -outputDirectory {}'.format(java,
                                        classpath, 
                                       pipeline, 
                                       annotators,
                                       input_files,
                                       output_dir) 
    return cmd

def _get_paragraph_line_numbers(wiki_data, output_dir, tmp_file_map):
    graf_annots = {}
    for wiki_inst in wiki_data:
        for rev in wiki_inst.revisions:
            rtree = rev.tree()
            hftree = rtree.header_free_tree()
            grafs = hftree.document_string().split('\n\n')
            lcnt = 0
            graf_annot = []
            
            for i, p in enumerate(grafs, 1):
                lines = []
                fname = tmp_file_map['{} {}'.format(rev.id, i)]
                parsedfile = join(output_dir, '{}.xml'.format(split(fname)[1]))
                doc = corenlp_xml.Document(parsedfile)
                nsents = len(doc.sentences)
                ann = []  
                for i,s in enumerate(doc.sentences, lcnt):
                    ann.append(i)
                graf_annot.append(ann)
                lcnt += nsents
            graf_annots[rev.id] = graf_annot 
    return graf_annots
                
class Excerpt:
    def __init__(self, document, sindices):
        self.sentences = [document.sentences[i] for i in sindices]
        self._query_cache = {}
    
    def __iter__(self):
        return iter(self.sentences)

    def dep_query(self, query):
        if query in self._query_cache:
            return self._query_cache[query]
        else:
            f, selector = query
            results = []
            for s in self:
                for rel in s.get_dependency_graph().filter_iterator(f):
                    results.append(selector(rel))
            self._query_cache[query] = tuple(results)
            return self._query_cache[query]
