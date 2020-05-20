import csv
import sys
from collections import defaultdict, Counter
import operator

import esy.osm.pbf


def parse():
    osm = esy.osm.pbf.File(sys.argv[1])
    refs = {}
    postcodes = defaultdict(list)
    ways = {}

    def get_postcode(lon, lat):
        distances = {l: abs(lon - lo) + abs(lat - la) for l, (lo, la) in postcodes_coord.items()}
        return min(distances.items(), key=operator.itemgetter(1))[0]

    for e in osm:
        if e.__class__.__name__ == 'Node':
            print(e.tags)
            refs[e.id] = e.lonlat
            if 'addr:postcode' in e.tags:
                city = e.tags['addr:city'] if 'addr:city' in e.tags else ''
                postcodes[e.tags['addr:postcode']].append((e.lonlat, city))
            if 'addr:city' in e.tags and 'addr:postcode' in e.tags and 'addr:street' in e.tags and 'addr:housenumber' in e.tags:
                yield [e.lonlat[0], e.lonlat[1], e.tags['addr:postcode'], e.tags['addr:city'], e.tags['addr:street'], e.tags['addr:housenumber']]
            elif 'addr:city' in e.tags and 'addr:postcode' in e.tags and 'addr:street' in e.tags:
                yield [e.lonlat[0], e.lonlat[1], e.tags['addr:postcode'], e.tags['addr:city'], e.tags['addr:street'], 0]

        if e.__class__.__name__ == 'Way' and 'highway' in e.tags and 'name' in e.tags:
            ways[e.id] = (e.tags['name'], e.refs)

    # compute means of postcode
    postcodes_coord = {}
    postcodes_city = {}
    for postcode, v in postcodes.items():
        mlon = sum([lon for (lon, lat), city in v]) / len(v)
        mlat = sum([lat for (lon, lat), city in v]) / len(v)
        postcodes_coord[postcode] = (mlon, mlat)
        cities = Counter()
        for (lon, lat), city in v:
            cities[city] += 1
        postcodes_city[postcode] = max(cities.items(), key=operator.itemgetter(1))[0]

    for w, (name, rf) in ways.items():
        print([r for r in rf])
        coords = [refs[r] for r in rf if r in refs.keys()]
        mlon = sum([lon for (lon, lat) in coords]) / len(coords)
        mlat = sum([lat for (lon, lat) in coords]) / len(coords)
        p = get_postcode(mlon, mlat)
        print(postcodes_city[p], p, name, (mlon, mlat))
        yield [mlon, mlat, p, postcodes_city[p], name]


if __name__ == '__main__':
    # @lon;@lat;addr:postcode;addr:city;addr:street;addr:housenumber
    with open(sys.argv[1] + '.csv', 'w') as csv_file:
        writer = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for values in parse():
            print(values)
            writer.writerow(values)
