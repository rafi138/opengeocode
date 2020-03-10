import logging
import os

from flask import Flask, request, jsonify, g
from psycopg2 import pool

app = Flask(__name__)
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


@app.route('/resolve', methods=['POST'])
def resolve():
    db = get_db()
    cur = db.cursor()
    q = request.get_json()
    return jsonify({'request': q, 'response': {}})
    #
    # cur.execute("SELECT tablename, tableowner FROM pg_tables WHERE schemaname='public';")
    # tables = list(cur.fetchall())
    # for n, o in tables:
    #     cur.execute("SELECT pg_size_pretty(pg_total_relation_size(%s));", (n,))
    #     yield n, o, cur.fetchone()[0]


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
