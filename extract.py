"""
Address extraction from OSM file in pbf

A first pass, will extract :
- osm node with attributes longitude, latitude, city, postcode, street and optionally housenumber to csv.

and build:
- ways dict with key based on name and value : the first reference used to build it
- places dict with key composed by (postcode and name) and value : coordinate

This first extraction in not sufficient. Indeed, many address a located near ways, that's why we already extract them in
the first pass. In a second pass, we will search reference id used in ways values and find closed places to build a new
record : longitude, latitude, place, postcode, way name to csv.
"""
import sys
import csv
import operator
import time
import esy.osm.pbf

places = {}
ways = set()


def parse(filepath):
    osm = esy.osm.pbf.File(filepath)
    start = time.time()
    print("First pass")
    for i, e in enumerate(osm):

        if e.__class__.__name__ == 'Node' and \
                'addr:city' in e.tags and 'addr:postcode' in e.tags and 'addr:street' in e.tags:
            hnb = e.tags['addr:housenumber'] if 'addr:housenumber' in e.tags else 0
            yield [e.lonlat[0], e.lonlat[1], e.tags['addr:postcode'], e.tags['addr:city'], e.tags['addr:street'], hnb]

        if 'place' in e.tags and 'addr:postcode' in e.tags and 'name' in e.tags and e.tags['place'] in ['village', 'town', 'hamlet']:
            key = (e.tags['addr:postcode'].split(';')[0], e.tags['name'])
            if key not in places.keys() and hasattr(e, 'lonlat'):
                places[key] = e.lonlat

        if 'addr:city' in e.tags and 'addr:postcode' in e.tags:
            key = (e.tags['addr:postcode'].split(';')[0], e.tags['addr:city'])
            if key not in places.keys() and hasattr(e, 'lonlat'):
                places[key] = e.lonlat

        if e.__class__.__name__ == 'Way' and 'highway' in e.tags and 'name' in e.tags:
            ways.add((e.tags['name'], e.refs[0]))

        if i % 1000000 == 0:
            print("%10d millions of nodes | time: %3d secs" % (i / 1000000, (time.time() - start)))
    print("First pass done in %d secs" % (time.time() - start))

    start = time.time()
    print("Second pass")
    refs = set([r for n, r in ways])
    rll = {}
    for i, e in enumerate(osm):
        if e.id in refs:
            try:
                rll[e.id] = e.lonlat
            except:
                continue
        if i % 1000000 == 0:
            print("%10d millions of nodes | time: %3d secs" % (i / 1000000, (time.time() - start)))
    print("Second pass done in %d secs" % (time.time() - start))


    def get_postcode(lonlat):
        lon, lat = lonlat
        distances = {(postcode, place): (lon - lo)**2 + (lat - la)**2 for (postcode, place), (lo, la) in places.items()}
        return min(distances.items(), key=operator.itemgetter(1))[0]

    print("Resolving ways to coords")
    start = time.time()
    for i, (name, eid) in enumerate(ways):
        try:
            postcode, place = get_postcode(rll[eid])
            lon, lat = places[(postcode, place)]
            yield [lon, lat, postcode, place, name, 0]
        except Exception as e:
            print("Error %s" % str(e))
    print("Resolving ways to coords done in %d secs" % (time.time() - start))


if __name__ == '__main__':
    # @lon;@lat;addr:postcode;addr:city;addr:street;addr:housenumber
    with open(sys.argv[1] + '.csv', 'w') as csv_file:
        writer = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for values in parse(sys.argv[1]):
            writer.writerow(values)
