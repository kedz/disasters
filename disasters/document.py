import corenlp
from collections import defaultdict

class WCDocument(corenlp.Document):
    def __init__(self, fname):
        corenlp.Document.__init__(self, fname)
        self._wc_dict = None

    def wc_dict(self):
        if not self._wc_dict:
            wc = defaultdict(int)
            for s in self:
                for t in s:
                    wc[t.lem.lower()] += 1     
            self._wc_dict = wc
        return self._wc_dict

class DocFreqs:
    def __init__(self, flist):
        self.df = defaultdict(int)
        self._word_indices = {}
        self.vocab_size = 0
        self.ndocs = 0
        for f in flist:
            doc = WCDocument(f)
            for word in doc.wc_dict().keys():
                if word not in self._word_indices:
                    idx = self.vocab_size
                    self._word_indices[word] = idx
                    self.vocab_size += 1
                idx = self._word_indices[word]    
                self.df[word] += 1
            self.ndocs += 1


    def __getitem__(self, word):
        return self.df.get(word, 0)

    def words(self):
        return self.df.keys()
    
    def entries(self):
        return self.df.items()

    def word_index(self, word):
        if word in self._word_indices:
            return self._word_indices[word]
        else:
            return None

