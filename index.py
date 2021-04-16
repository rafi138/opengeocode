import json, string, logging, os, pickle, time
from typing import Optional

from annoy import AnnoyIndex
import random

from fastapi import FastAPI, Path, Query,  HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datasketch import MinHashLSHForest, MinHash

app = FastAPI()

origins = [
    "http://localhost:8888"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger('ogc')

N = 2
data_dir = "data"

ind = {}

for f in os.listdir(data_dir):
    if f.endswith(".ann"):
        name = f.split('.')[0]
        filepath = os.path.join(data_dir, f)
        t = AnnoyIndex(32, 'hamming')
        t.load(filepath)
        ind[name] = {"ann": t,
                     "coords": pickle.load(open(filepath.replace(".ann", ".p"), 'rb'))
                     }


def hash(s):
    s.lower().translate(str.maketrans('', '', string.punctuation))
    mh = MinHash(num_perm=32)
    for d in [s[i:i + N] for i in range(len(s) - N + 1)]:
        mh.update(d.encode('utf8'))
    return mh


def build(filepath):
    coords = []
    properties = ['city', 'number', 'postcode', 'region', 'street']
    t = AnnoyIndex(32, 'hamming')
    for i, line in enumerate(open(filepath, 'r')):
        d = json.loads(line)
        c = d['geometry']['coordinates']
        coords.append(c)
        s = ' '.join([d['properties'][p] for p in properties])
        t.add_item(i, hash(s).hashvalues)
        if i % 1000 == 0:
            print("%9d %s" % (i, s))
    t.build(10)
    t.save(os.path.join(data_dir, filepath + ".ann"))
    with open(os.path.join(data_dir, filepath + ".p"), 'wb') as f:
        pickle.dump(coords, f)


def search(ann, coords, s, n=5):
    for r in ann.get_nns_by_vector(hash(s).hashvalues, n, search_k=-1, include_distances=False):
        yield r, coords[r]


@app.get('/')
async def index():
    return list(ind.keys())


@app.get('/{country}')
async def query(country: str = Path(..., title="The name of the country indexed"),
                q: str = ""
                ):
    if country in ind.keys():
        s = time.time()
        res = list(search(ind[country]['ann'], ind[country]['coords'], q))
        e = time.time()
        return {'query': q,
                'result': res,
                'time': e - s
                }
    else:
        raise HTTPException(status_code=404, detail=f"Country {country} not indexed")


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--file", help="geojson file to index")
    parser.add_argument("-p", "--port", help="port", type=int, default=5555)
    args = parser.parse_args()
    if args.file:
        build(args.file)
    else:
        app.run(host='0.0.0.0', port=args.port, debug=True)
