import pygraphviz as pgv
import argparse
from collections import defaultdict
import os
import corenlp
import cPickle as pickle

nominals = ['NN', 'NNP', 'NNS', 'NPS', 'PRP']

def make_graph(doc, pmis, ofile):

    G=pgv.AGraph(strict=False, directed=True)
    key_idx = 0
    
    last_verb = {}
    entcounts = defaultdict(int)
    
    for s in doc:
        
        for rel in s.deps:
            if 'VB' in rel.gov.pos and rel.dep.pos in nominals:
         
                if rel.dep.ne in ['O', 'PERSON', 'ORGANIZATION']:
                    token = rel.dep
                    mc = doc.mention_chain(token)
                    if mc is not None:
                        ent = mc.rep_head.lem.lower()
                    else:
                        ent = token.lem.lower()
                else: ent = rel.dep.ne
    
                v1 = rel.gov.lem.lower()
                
                if ent not in last_verb:                    
                    entcounts[ent] += 1
                    last_verb[ent] = [v1]
                    
                
                else:
                    entcounts[ent] += 1
                    
                    if entcounts[ent] == 2:
                        G.add_node(u'e:{}'.format(unicode(ent)),
                                   shape='rectangle')
                        if 'obj' in rel.type:
                            G.add_edge(v1, u'e:{}'.format(unicode(ent)),
                                       label=rel.type, color='red')
                        elif 'subj' in rel.type:    
                            G.add_edge(u'e:{}'.format(unicode(ent)), v1,
                                       label=rel.type, color='red')
                        else:
                            G.add_edge(v1, u'e:{}'.format(unicode(ent)),
                                       label=rel.type, color='red', dir='none')
                        key_idx += 1
        
                    v2 = rel.gov.lem.lower()
                    for v1 in last_verb[ent]:
                        #score = pmicounts.pmi(ent, v1, v2)    
                        #if score is not None:
                            #if score > 2:
                        
                        pmi = pmis.pmi(v1, v2, ent)
                        G.add_edge(v1, v2, color='green', label=ent)
                        key_idx += 1
                                
                            #    if (v1, v2) in edges:
                            #        if pmicounts.pmi(edges[(v1, v2)], v1, v2) < score:
                    
                             #           edges[(v1, v2)] = ent
                              #  else: edges[(v1, v2)] = ent
                            
                    
                    #last_verb[ent].append(v2)
                    last_verb[ent] = [v2]
                    
                    
                        #print ent, v1, v2, score
                    
    
                        
                        #key_idx += 1
                #    verb_co_occurrence = (v1, v2) 
                                          
                #    co_occur[ent][verb_co_occurrence] += 1
                #    
                #    verb_count[ent][v2] += 1
    
    #for edge in edges.keys():
    #    G.add_edge(edge[0], edge[1], color='green', label=edges[edge], key='e{}'.format(key_idx))
    #    key_idx += 1
    G.layout(prog='dot')
    G.draw(ofile)

parser = argparse.ArgumentParser()
parser.add_argument('-if', '--inputfile', help='input corenlp xml file',
                    type=unicode, required=True)
parser.add_argument('-of', '--outputfile', help='output png file',
                    type=unicode, required=True)

parser.add_argument('-pf', '--pmi-file',
                    help='pmi counts pickle file',
                    type=unicode, required=True)

args = parser.parse_args()

ifile = args.inputfile
ofile = args.outputfile
odir = os.path.split(ofile)[0]
pfile = args.pmi_file

if not os.path.exists(ifile):
    import sys
    sys.stderr.write(u'Input file {} does not exist!\n'.format(ifile))
    sys.stderr.flush()
    sys.exit()


if not os.path.exists(pfile):
    import sys
    sys.stderr.write(u'Pmi counts file {} does not exist!\n'.format(pfile))
    sys.stderr.flush()
    sys.exit()

with open(pfile, 'rb') as f:
    pmis = pickle.load(f)

if odir != '' and not os.path.exists(odir):
    os.makedirs(odir)

if not ofile.endswith(u'.png'):
    ofile = u'{}.png'.format(ofile)


G=pgv.AGraph(strict=False, directed=True)
key_idx = 0
 
import itertools
doc = corenlp.Document(ifile)
for ent, verbs in pmis.aggregate(doc).iteritems():
    if len(verbs) > 1:
        for v1, v2 in itertools.izip(verbs[0:-1], verbs[1:]):
            score = pmis.pmi(v1, v2, ent)
            G.add_edge(v1, v2, label=u'e:{} {:2.2f}'.format(unicode(ent), score),
                       color='green', dir='none', key=key_idx)
            key_idx += 1

G.layout(prog='dot')
G.draw(ofile)




#make_graph(doc, pmis, ofile) 
