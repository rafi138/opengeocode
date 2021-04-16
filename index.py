import json, string, logging, os, pickle, time

from annoy import AnnoyIndex
import random

from flask import Flask, request, jsonify, abort, render_template_string
from datasketch import MinHashLSHForest, MinHash


app = Flask(__name__)
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
    t.build(10)
    t.save(os.path.join(data_dir, filepath + ".ann"))
    with open(os.path.join(data_dir, filepath + ".p"), 'wb') as f:
        pickle.dump(coords, f)


def search(ann, coords, s, n=5):
    for r in ann.get_nns_by_vector(hash(s).hashvalues, n, search_k=-1, include_distances=False):
        yield r, coords[r]


@app.route('/<string:country>')
def query(country):
    if country in ind.keys():
        q = request.args.get('q')
        s = time.time()
        res = list(search(ind[country]['ann'], ind[country]['coords'], q))
        e = time.time()
        return jsonify({'query': q,
                        'result': res,
                        'time': e - s
                        })
    else:
        abort(404, description="Country %s not indexed" % country)


@app.route('/')
def index():
    t = """
        <html>
        <head></head>
        <body style="font-family: sans-serif">
        <div style="text-align: center">
            {{ svg | safe }}
        <h1>Open GeoCoding</h1>
        <select id="country">
            {% for country in countries %}
                  <option value="{{country}}">{{country}}</option>
            {% endfor %}
        </select>
        <input type="text" id="query"><hr>
        <span id="result"></span><br>
        <span id="time"></span>
        <hr>
         <a href="https://github.com/scampion/opengeocode">github</a>
        </div>

        <script type="text/javascript">
            (function() {
                document.querySelector("#query").onkeyup = function (e) {
                    console.log();
                  let xhr = new XMLHttpRequest();
                  xhr.open('GET', './' + document.querySelector("#country").value + '?q=' + e.target.value);
                  xhr.send();
                    xhr.onload = function() {
                      if (xhr.status != 200) { 
                        console.log(`Error ${xhr.status}: ${xhr.statusText}`); 
                      } else { 
                        var jsonResponse = JSON.parse(xhr.response);
                        document.querySelector("#result").innerHTML = "";
                        jsonResponse.result.forEach(function(value){                            
                            document.querySelector("#result").innerHTML += "<a  href='https://maps.google.com/?q=" + value[1][1] + "," + value[1][0] + "'>" + value + "</a><br>";
                            console.log(value);
                        });                        
                        document.querySelector("#time").innerHTML = 'time : ' + Math.round(Number(jsonResponse.time) * 1000) + ' ms';
                      }
                    }
                }
        })();
        </script>
        </body>
        </html> 
        """
    return render_template_string(t, svg=open(os.path.join('images', 'ogc.svg')).read(), countries=ind.keys())


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
