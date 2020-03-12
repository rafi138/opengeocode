
import codecs
import csv
import logging
import os
import pickle
import time

import ngram
from flask import Flask, request, jsonify, abort

data_dir = "data"

app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger('ogc')

ind = {}
inv = {}
for country in [f.replace('.p', '') for f in os.listdir(data_dir) if f.endswith('.p')]:
    fp = os.path.join(data_dir, '%s.p' % country)
    with open(fp, 'rb') as handle:
        i, j = pickle.load(handle)
        ind[country] = i
        inv[country] = j


@app.route('/ls')
def list():
   return ' '.join(ind.keys())


@app.route('/load', methods=['POST'])
def load():
    flask_file = request.files['file']
    if not flask_file:
        return 'Upload a CSV file'

    country = flask_file.filename.replace('.csv', '')
    ind[country] = ngram.NGram()
    inv[country] = {}

    stream = codecs.iterdecode(flask_file.stream, 'utf-8')
    s_csv = csv.reader(map(lambda line: line.lower(), stream), delimiter=';')
    next(s_csv)
    for row in s_csv:
        coord = tuple(row[0:2])
        address = tuple(row[2:])
        ind[country].add(' '.join(address))
        inv[country][' '.join(address)] = (coord, address)

    fp = os.path.join(data_dir, '%s.p' % country)
    with open(fp, 'wb') as f:
        pickle.dump((ind[country], inv[country]), f, protocol=pickle.HIGHEST_PROTOCOL)
    return jsonify(inv)


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
    app.run(host='0.0.0.0', port=5555, debug=True)
