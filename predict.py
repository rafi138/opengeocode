import numpy as np
import pickle, re, sys
from annoy import AnnoyIndex
import codebook

def ngrams(string, n=3):
    string = re.sub(r'[,-./]|\sBD',r'', string)
    ngrams = zip(*[string[i:] for i in range(n)])
    return [''.join(ngram) for ngram in ngrams]

with open('vectorizer.pk', 'rb') as fin:
    vectorizer = pickle.load(fin)


f =  int(sys.argv[1])
t = AnnoyIndex(f, 'angular')# Length of item vector that will be indexed
t.load("test.ann")


q = " ".join(sys.argv[2:]).lower()
print(q)
print("#"*80)
tfidfthreshord = 0
print(q)
print(ngrams(q))
print("#"*80)
v = vectorizer.transform([q])
print(v)
a = v.toarray()[0]

#a[a > tfidfthreshord] = 1
#a[a <= tfidfthreshord] = 0
print(a)
print(np.count_nonzero(a))
df = codebook.getdf("france.csv")
for r in t.get_nns_by_vector(a, 3):
    print(df.iloc[r])

# features = vectorizer.get_feature_names()
# indices = np.argsort(vectorizer.idf_)[::-1]
# features = vectorizer.get_feature_names()
# top_n = 2
# top_features = [features[i] for i in indices[:top_n]]
# print top_features

