import numpy as np
import pandas as pd
import re, time
import pickle
import logging

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import NearestNeighbors

logging.basicConfig(level=logging.INFO)


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


def vectorize(df, max_df=0.01, min_df=0.001):
    logging.info("Vectorize %d entry", df.size)
    vectorizer = TfidfVectorizer(analyzer=ngrams, max_df=max_df, min_df=min_df)
    tf_idf_matrix = vectorizer.fit_transform(df['address'].to_numpy())
    logging.info("tf_idf_matrix shape %s", tf_idf_matrix.shape)
    return tf_idf_matrix, vectorizer


if __name__ == '__main__':
    df = getdf("france.csv")
    X, vectorizer = vectorize(df, None)
    with open("TfidfVectorizer.p", 'wb') as fin:
        pickle.dump(vectorizer, fin)
    #del df['address']  # free memory
    nbrs = NearestNeighbors(n_neighbors=X.shape[-1], algorithm='brute').fit(X)

    q = "rue de la porte 76270 Neufchatel-en-Bray"
    start = time.time()
    vq = vectorizer.transform([q.lower()])
    results = nbrs.kneighbors(vq.toarray(), 10)[1][0]
    print("Time : %0.6f sec" % (time.time() - start))
    for k in results:
        print(df.iloc[k])
