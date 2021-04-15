import json, string

properties = ['city', 'number', 'postcode', 'region', 'street']

coords = []

from datasketch import MinHashLSHForest, MinHash

forest = MinHashLSHForest(num_perm=32)
N = 2

def hash(s):
    s.lower().translate(str.maketrans('', '', string.punctuation))
    mh = MinHash(num_perm=32)
    for d in [s[i:i+N] for i in range(len(s)-N+1)]:
        mh.update(d.encode('utf8'))
    return mh

def gen_str_address(N=2):
    for i, line in enumerate(open('fr_countrywide-addresses-country.geojson', 'r')):
        d = json.loads(line)
        c = d['geometry']['coordinates']
        coords.append(c)
        s  = ' '.join([d['properties'][p] for p in properties])
        print(i, s)
        mh = hash(s)
        forest.add(i, mh)
        if i >= 1000:
            break
    forest.index()



def query(s, k=3):
    for r in forest.query(hash(s), k):
        yield r, coords[r]

if __name__ == "__main__":
    gen_str_address()
