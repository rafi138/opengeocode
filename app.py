import codecs
import csv
import logging
import ngram

from flask import Flask, request, jsonify, abort

app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger('ogc')

ind = {}
inv = {}


@app.route('/load', methods=['POST'])
def load():
    flask_file = request.files['file']
    if not flask_file:
        return 'Upload a CSV file'

    country = flask_file.filename.replace('.csv', '')
    ind[country] = ngram.NGram(key=lambda x: (" ".join(x)).lower())
    inv[country] = {}

    stream = codecs.iterdecode(flask_file.stream, 'utf-8')
    s_csv = csv.reader(stream, delimiter=';')
    next(s_csv)
    for row in s_csv:
        coord = tuple(row[0:2])
        address = tuple(row[2:])
        log.debug((coord, address))
        ind[country].add(address)
        inv[country][str(address)] = coord
    return jsonify(inv)


@app.route('/<string:country>')
def index(country):
    if country in ind.keys():
        q = request.args.get('q')
        s = time.time()
        res = ind[country].find(q)
        e = time.time()
        return jsonify({'query': q,
                        'result': str(res),
                        'coord': inv[country][str(res)],
                        'time': e - s
                        })
    else:
        abort(404, description="Country %s not indexed" % country)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5555, debug=True)
