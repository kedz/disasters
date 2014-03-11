from os import getenv, listdir, remove, makedirs
from os.path import join, split, exists, basename
import re
from datetime import datetime
from collections import namedtuple, defaultdict
import os

_data_dir = os.getenv('DISASTERS_DATA', '.')
_pickle_dir = os.path.join(_data_dir, 'preprocessed')
_wiki_disaster_dir = os.path.join(_data_dir, 'disasters')
_wiki_html_dir = os.path.join(_data_dir, 'html')
_wiki_impact_links_dir = os.path.join(_data_dir, 'linked_pages')

file_pattern = re.compile(r'(\d\d\d\d)_(\d\d)_(\d\d)_(\d\d)_(\d\d)_(\d\d)_(\d+)_(.*?)\.html')

_disaster_categories = ('hurricanes', 'typhoons',
                        'cyclones', 'tropicalstorms')

def get_cats():
    return _disaster_categories

    #c = clustertree.from_wiki(open(html, 'r'))
    #itrees = clustertree.subtrees_with_label_re(c, re.compile(r'impact', re.I))
    #return [(cat, (html.split('/')[-1], it)) for it in itrees]

def get_disasters(disaster_type):
    disasters = []
    dfile = open(os.path.join(_wiki_disaster_dir, '{}.txt'.format(disaster_type)), 'r')
    for line in dfile:
        title, date_str = line.strip().split('\t')
        date = datetime.strptime(date_str, "%m/%d/%y")
        disasters.append((title, date))
    dfile.close()
    return disasters

def get_wiki_html_dir(disaster):
    return join(_wiki_html_dir, disaster)

def get_linked_page_dir(category):
    d = join(_wiki_impact_links_dir, category)
    if not exists(d):
        makedirs(d)
    return d

def set_data_dir(directory):
    _data_dir = directory

def get_html(category, num_revs=1, latest_first=False):
    d = os.path.join(_wiki_html_dir, category)
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

            articles[m.group(8)].append((rdate, os.path.join(d, fname)))

    pages = []
    for key in articles.keys():
        revs = articles[key]
        revs.sort(key=lambda x: x[0], reverse=latest_first)
        pages.append([rev[1] for rev in revs[0:num_revs]])
    return pages

