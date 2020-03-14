#!/usr/bin/env python3
import codecs
import csv
import logging
import os
import pickle
import time

import ngram
from flask import Flask, request, jsonify, abort
from werkzeug.datastructures import FileStorage

data_dir = "data"

app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger('ogc')

ind = {}
inv = {}


def save(filename, stream):
    country = filename.replace('.csv', '')
    ind[country] = ngram.NGram()
    inv[country] = {}
    s_csv = csv.reader(stream, delimiter=';')
    next(s_csv)
    for row in s_csv:
        coord = tuple(map(float, row[0:2]))
        address = row[2:]
        ad = ' '.join(address).lower()
        ind[country].add(ad)
        inv[country][ad] = (coord, address)
    dest = os.path.join(data_dir, '%s.p' % country)
    with open(dest, 'wb') as f:
        log.info("Saving %s : %s entries", country, len(ind[country]))
        pickle.dump((ind[country], inv[country]), f, protocol=pickle.HIGHEST_PROTOCOL)
    return len(ind[country])


@app.before_first_request
def load():
    for country in [f.replace('.p', '') for f in os.listdir(data_dir) if f.endswith('.p')]:
        fp = os.path.join(data_dir, '%s.p' % country)
        with open(fp, 'rb') as handle:
            i, j = pickle.load(handle)
            ind[country] = i
            inv[country] = j


@app.route('/ls')
def ls():
    return ' '.join(ind.keys())


@app.route('/load', methods=['POST'])
def httpload():
    flask_file = request.files['file']
    if not flask_file:
        return 'Upload a CSV file'

    stream = codecs.iterdecode(flask_file.stream, 'utf-8')
    nbentries = save(flask_file.filename, stream)
    return jsonify({'nb_of_insertions': nbentries})


@app.route('/<string:country>')
def index(country):
    if country in ind.keys():
        q = request.args.get('q')
        s = time.time()
        res = ind[country].find(q)
        e = time.time()
        return jsonify({'query': q,
                        'result': inv[country][str(res)],
                        'time': e - s
                        })
    else:
        abort(404, description="Country %s not indexed" % country)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("-w", "--web", help="start the web server")
    parser.add_argument("-l", "--load", dest="filepath", nargs='?', action="append", const=str,
                        help="load CSV file in memory and cache")
    args = parser.parse_args()
    for fp in args.filepath:
        with open(fp, encoding='utf-8') as s:
            save(fp, s)
    if args.web:
        app.run(host='0.0.0.0', port=5555, debug=True)
