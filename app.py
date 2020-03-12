import logging
import os
import time

from flask import Flask, request, jsonify, g
from psycopg2 import pool, sql


app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger('ogc')
app.config['pool'] = pool.SimpleConnectionPool(1, 20, user=os.getenv('DATABASE_DB'),
                                               password=os.getenv('DATABASE_PASSWORD'),
                                               host=os.getenv('DATABASE_HOST'),
                                               database=os.getenv('DATABASE_DB'))


def get_db():
    if 'db' not in g:
        g.db = app.config['pool'].getconn()
        g.db.autocommit = True
    return g.db


@app.route('/<string:country>/<string:city>/')
@app.route('/<string:country>/<string:city>/<string:postcode>')
@app.route('/<string:country>/<string:city>/<string:postcode>/<string:street>')
@app.route('/<string:country>/<string:city>/<string:postcode>/<string:street>/<string:housenumber>')
def index(country, city='', postcode='', street='', housenumber=''):
    db = get_db()
    cur = db.cursor()
    q = request.get_json()
    cur.execute("SELECT set_limit(0.2);")

    s = "SELECT *,  " \
        "similarity(city, %s) + similarity(postcode, %s) + similarity(street, %s) + similarity(housenumber, %s) AS similarity " \
        "FROM {} WHERE city %% %s OR postcode %% %s OR street %% %s OR housenumber %% %s " \
        "ORDER BY similarity DESC NULLS LAST LIMIT 1;"

    query = sql.SQL(s).format(sql.Identifier(country))
    params = (city, postcode, street, housenumber, city, postcode, street, housenumber)
    start = time.time()
    cur.execute(query, params)
    end = time.time()
    results = [r for r in cur.fetchall()]
    return jsonify({'request': (city, postcode, street, housenumber), 'response': results, 'time': 1000 * (end - start)})


@app.route('/json', methods=['POST'])
def json():
    q = request.get_json()
    index(q['country'], q['city'], q['postcode'], q['street'], q['housenumber'] )


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
