import numpy as np
import pandas as pd
import re
import pickle
import logging

from sklearn.feature_extraction.text import TfidfVectorizer

from annoy import AnnoyIndex

logging.basicConfig(level=logging.DEBUG)


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


def learn(df, f, tfidfthreshord=0.5, nb_trees=10):
    logging.info("Vectorize %d entry with %d features", df.size, f)
    vectorizer = TfidfVectorizer(min_df=1, analyzer=ngrams, max_features=f)
    tf_idf_matrix = vectorizer.fit_transform(df['address'])

    t = AnnoyIndex(f, 'angular')
    logging.info("Index loading ...")
    for i, v in enumerate(tf_idf_matrix):
        a = v.toarray()[0]
        a[a >= tfidfthreshord] = 1
        a[a < tfidfthreshord] = 0
        t.add_item(i, a)

    logging.info("Index building in progress with %d trees", nb_trees)
    t.build(nb_trees, n_jobs=-1)
    return vectorizer, t


def predict(q, f, vectorizer, annoyt):
    q = q.lower()
    v = vectorizer.transform([q]).toarray()[0]
    n = 10
    t.get_nns_by_vector(v, n)


if __name__ == '__main__':
    df = getdf("france.csv")
    vectorizer, annoyindex = learn(df, 1000)
    # Save vectorizer and index
    annoyindex.save('test.ann')
    with open('vectorizer.pk', 'wb') as fin:
        pickle.dump(vectorizer, fin)
