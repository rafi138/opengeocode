import pickle, re
from annoy import AnnoyIndex
import codebook

def ngrams(string, n=3):
    string = re.sub(r'[,-./]|\sBD',r'', string)
    ngrams = zip(*[string[i:] for i in range(n)])
    return [''.join(ngram) for ngram in ngrams]

with open('vectorizer.pk', 'rb') as fin:
    vectorizer = pickle.load(fin)


f = 1000
t = AnnoyIndex(f, 'angular')# Length of item vector that will be indexed
t.load("test.ann")

q = "rue de la porte 76270 Neufchatel-en-Bray".lower()
v = vectorizer.transform([q]).toarray()[0]
df = codebook.getdf("france.csv")
for r in t.get_nns_by_vector(v, 3):
    print(df.iloc[r])