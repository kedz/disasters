from BeautifulSoup import BeautifulSoup
import nltk
import re

class ClusterTree:
    def __init__(self, label, items=None, urls=None, children=None):
        self.label = label
        self.items = items if items else []
        self.children = children if children else [] 
        self.items_meta = None
        self.urls = urls if urls else []
        # Tree stats that are cached after first calculation:
        self._height = None
        self._n_nodes = None
        self._avg_bf = None
        self._n_int_nodes = None
        self._n_leaf_nodes = None

    def print_toc(self, indent=''):
        print indent + self.label
        for c in self.children:
            c.print_toc(indent+'\t') 

    def leaves(self):
        if len(self.children) == 0:
            return [self]        
        else:
            leaves = []
            for c in self.children:
                leaves.extend(c.leaves())
            return leaves                

    def height(self, depth=0):
        if self._height:
            return self._height
        else:
            if len(self.children) == 0:
                self._height = depth
                return depth
            else:
                self._height = max([c.height(depth=(depth+1)) for c in self.children])
                return self._height


    def n_nodes(self):
        if self._n_nodes == None:
            self._n_nodes = 1 + sum([c.n_nodes() for c in self.children])
        return self._n_nodes



    def n_int_nodes(self):
        if self._n_int_nodes == None:
            self._n_int_nodes = self.n_nodes() - self.n_leaf_nodes()
        return self._n_int_nodes

    def n_leaf_nodes(self):
        if self._n_leaf_nodes == None:
            self._n_leaf_nodes = len(self.leaves())
        return self._n_leaf_nodes
    
    def avg_bf(self):
       
        if self._avg_bf == None:
            
            branches = 0
            Q = [self]
            nodes = 0

            while len(Q) > 0:
                n = Q.pop()
                nodes += 1
                branches += len(n.children)
                Q.extend(n.children)
            
            self._avg_bf = float(branches) / float(nodes)

        return self._avg_bf        

    def bfs_iter(self):
        Q = [self]

        while len(Q) > 0:
            n = Q.pop()
            yield n
            Q.extend(n.children)
            

    def to_ipython(self):
        import pygraphviz as pgv
        G = pgv.AGraph()
        Q = [self]

        G.add_node(self.label)
        while len(Q) > 0:
            n = Q.pop()
            for c in n.children:
                G.add_edge(n.label, c.label)
            Q.extend(n.children)
            
        G.layout(prog='dot')
        G.draw('/tmp/toctree.png')
        from IPython.display import Image
        return Image(filename='/tmp/toctree.png')


def from_wiki(f):
    """
    Creates an event cluster tree from Wikipedia page html fragment.

    Parameters
    ----------
    f - a file handle to the html fragment
    """
    
    pagetext = f.read()
    f.close()
     
    parsed_html = BeautifulSoup(pagetext)

    toctablediv = parsed_html.find('div', attrs={'id':'toc'})
    grafs, urls = _recover_section_text(parsed_html)
    r = ClusterTree('Abstract', items=grafs, urls=urls)    

    if toctablediv:
        toctable = toctablediv.find('ul')
        _recover_wiki_tree(toctable, parsed_html, r)

    return r

def _recover_wiki_tree(el, soup, root, indent=''):
    if not el:
        return

    for li in el.findAll('li', recursive=False):
        toctext = li.a.get('href')[1:]
        if toctext not in ['See_also', 'References', 'External_links', 'Notes']:
       
            sublist = li.find('ul')
            safe_text = toctext.replace(' ', '_')
            grafs, urls = _recover_section_text(soup, safe_text)
            node = ClusterTree(toctext, items=grafs, urls=urls)
            _recover_wiki_tree(sublist, soup, node, indent+'\t')
            root.children.append(node)
  


def _recover_section_text(soup, section=None):
    
    grafs = []
    urls = []
    if section:
        tag = soup.find('span', attrs={'id':section}).parent
    else:
        tag = soup.find('p', recursive=False)
        clean_text = _extract_clean_text(tag, soup)
        grafs.append(clean_text)
    while True:
        if not tag:
            break
        tag = tag.nextSibling
        if tag == None:
            break
        if hasattr(tag, 'name'):
            if tag.name in ['h1', 'h2', 'h3', 'h4', 'h5']:
                break
            if tag.name == 'p':
                clean_text, links = _extract_clean_text(tag, soup)
                grafs.append(clean_text)
                urls.append(links)

    return (grafs, urls)

def _extract_clean_text(tag, soup):
    if not tag:
        return ''
    #for s in tag.find_all('a'):
    links = [] 
    footnotes = [s.extract() for s in tag('sup')]
    for ref in footnotes:
        if len(ref('a')) > 0:
            id = ref('a')[0]['href'][1:]
            found_id = soup.find(id=id)
            if found_id:
                for atag in found_id.findAll('a', {'class':'external text'}):
                    links.append(atag['href'])
        #else:
        #    print ref('a')
    clean_text = nltk.clean_html(repr(tag))
    clean_text = clean_text.replace('&#160;',' ')
    clean_text = clean_text.replace('\s', ' ')
    clean_text = re.sub('\[\d+\]', '', clean_text)
    clean_text = clean_text.strip()
    return (clean_text, links)

def num_subtrees_with_label(root, label):
    num = 0
    for c in root.children:
        num += num_subtrees_with_label(c, label) 
    if label == root.label: num += 1
    return num

def subtrees_with_label(root, label):
    if root.label == label:
        return [root]
    else:
        matches = []
        for c in root.children:
            match = subtrees_with_label(c, label)
            matches.extend(match)
        return matches

def num_subtrees_with_label_re(root, regex):
    num = 0
    for c in root.children:
        num += num_subtrees_with_label_re(c, regex) 
    if regex.search(root.label):
        num += 1
    return num

def subtrees_with_label_re(root, regex):
    if regex.search(root.label):
        return [root]
    else:
        matches = []
        for c in root.children:
            match = subtrees_with_label_re(c, regex)
            matches.extend(match)
        return matches






