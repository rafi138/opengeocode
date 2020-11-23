import numpy as np
import pandas as pd
import re
import pickle
import logging

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import MiniBatchKMeans
from numpy.random import RandomState

from annoy import AnnoyIndex

logging.basicConfig(level=logging.INFO)
rng = RandomState(0)


def ngrams(string, n=3):
    string = re.sub(r'[,-./]|\sBD', r'', string)
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


def vectorize(df, ofile=None):
    logging.info("Vectorize %d entry", df.size)
    vectorizer = TfidfVectorizer(analyzer=ngrams)
    tf_idf_matrix = vectorizer.fit_transform(df['address'])
    logging.info("tf_idf_matrix shape %s", tf_idf_matrix.shape)
    return tf_idf_matrix, vectorizer


def codebook(tf_idf_matrix, nb_of_clusters=1024):
    logging.info("MiniBatchKMeans")
    kmeans = MiniBatchKMeans(n_clusters=nb_of_clusters, random_state=rng, verbose=True)
    kmeans.fit(tf_idf_matrix)
    return kmeans.cluster_centers_


def index(tf_idf_matrix, cb, nb_trees=10):
    f = cb.shape[0]
    t = AnnoyIndex(f, 'angular')
    logging.info("Index loading ...")
    reduc = tf_idf_matrix.dot(cb.T)
    for i, v in enumerate(reduc):
        t.add_item(i, v)
    logging.info("Index building in progress with %d trees", nb_trees)
    t.build(nb_trees, n_jobs=-1)
    return t


def predict(q, cb, vectorizer, t, n=10, df=None):
    v = vectorizer.transform([q.lower()])[0].dot(cb.T)[0]
    for r in t.get_nns_by_vector(v, n):
        if df is not None:
            yield r, df.iloc[r]
        else:
            yield r


if __name__ == '__main__':
    # Load dataset
    df = getdf("france.csv")

    # TFIDF
    tf_idf_matrix, vectorizer = vectorize(df, None)
    with open("test.vec", 'wb') as fin:
        pickle.dump(vectorizer, fin)

    # Reduction
    cb = codebook(tf_idf_matrix)
    np.save("cb", cb)

    # Indexation
    t = index(tf_idf_matrix, cb)
    t.save("test.ann")

    # Search
    q = "rue de la porte 76270 Neufchatel-en-Bray"
    predict(q, cb, vectorizer, t, n=10, df=df)
