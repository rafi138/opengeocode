import numpy as np
import pandas as pd
import re
import pickle
import logging

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import MiniBatchKMeans

from annoy import AnnoyIndex

logging.basicConfig(level=logging.INFO)
from numpy.random import RandomState
rng = RandomState(0)

def ngrams(string, n=3):
    string = re.sub(r'[,-./]|\sBD',r'', string)
    ngrams = zip(*[string[i:] for i in range(n)])
    return [''.join(ngram) for ngram in ngrams]


def getdf(csv_filepath):
    logging.info("Load file %s", csv_filepath)
    df = pd.read_csv(csv_filepath)
    df.fillna('', inplace=True)
    for c in ['number', 'street', 'postalcode', 'city']:
        df[c].astype(object).replace(np.nan, 'None')
    df['address'] = (df['number'] + " " + df['street'] + " " + df['postalcode'] + " " + df['city']).str.lower()
    for c in ['number', 'street', 'postalcode', 'city', 'Unnamed: 0']:
        del df[c]
    df.head()
    return df


def vectorize(df, f=None, ofile=None):
    logging.info("Vectorize %d entry with %s max features", df.size, f)
    vectorizer = TfidfVectorizer(analyzer=ngrams)
    tf_idf_matrix = vectorizer.fit_transform(df['address'])
    logging.info("tf_idf_matrix shape %s", tf_idf_matrix.shape)
    if ofile:
        with open(ofile, 'wb') as fin:
            pickle.dump(vectorizer, fin)
    return tf_idf_matrix, vectorizer


def minikm(tf_idf_matrix):
    kmeans = MiniBatchKMeans(n_clusters=128, random_state=rng, verbose=True)
    kmeans.fit(tf_idf_matrix)
    return kmeans


def sparce_pca(tf_idf_matrix):
    n_components = tf_idf_matrix.shape[-1]
    estimator = MiniBatchSparsePCA(n_components=n_components, alpha=0.8, n_iter=100, batch_size=3, random_state=rng, n_jobs=-1)
    estimator.fit(tf_idf_matrix.toarray())
    components_ = estimator.components_
    return components_

def index(tf_idf_matrix, nb_trees=10,  ofile=None):
    t = AnnoyIndex(f, 'angular')
    logging.info("Index loading ...")
    for i, v in enumerate(tf_idf_matrix):
        a = v.toarray()[0]
        a[a > tfidfthreshord] = 1
        a[a <= tfidfthreshord] = 0
        t.add_item(i, a)
    logging.info("Index building in progress with %d trees", nb_trees)
    t.build(nb_trees, n_jobs=-1)
    if ofile:
        annoyindex.save(ofile)



def predict(q, f, vectorizer, annoyt):
    q = q.lower()
    v = vectorizer.transform([q]).toarray()[0]
    n = 10
    t.get_nns_by_vector(v, n)


if __name__ == '__main__':
    df = getdf("france.csv")
    vectorizer, annoyindex = learn(df, 5000)
    # Save vectorizer and index
