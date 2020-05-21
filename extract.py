import csv
import sys
import operator

import esy.osm.pbf


def parse():
    osm = esy.osm.pbf.File(sys.argv[1])
    refs = {}
    pc_coord = {}
    pc_city = {}
    ways_names = {}
    ways_ref = {}

    def get_postcode(lon, lat):
        distances = {l: abs(lon - lo) + abs(lat - la) for l, (lo, la) in pc_coord.items()}
        return min(distances.items(), key=operator.itemgetter(1))[0]

    print("First pass")
    for e in osm:
        if e.__class__.__name__ == 'Node':
            # store the mapping between postcode and longlat and postcode and city
            if 'addr:postcode' in e.tags and e.tags['addr:postcode'] not in pc_coord.keys() and 'addr:city' in e.tags:
                pc_coord[e.tags['addr:postcode']] = e.lonlat
                pc_city[e.tags['addr:postcode']] = e.tags['addr:city']

            if 'addr:city' in e.tags and 'addr:postcode' in e.tags and 'addr:street' in e.tags and 'addr:housenumber' in e.tags:
                yield [e.lonlat[0], e.lonlat[1], e.tags['addr:postcode'], e.tags['addr:city'], e.tags['addr:street'], e.tags['addr:housenumber']]
            elif 'addr:city' in e.tags and 'addr:postcode' in e.tags and 'addr:street' in e.tags:
                yield [e.lonlat[0], e.lonlat[1], e.tags['addr:postcode'], e.tags['addr:city'], e.tags['addr:street'], 0]

        if e.__class__.__name__ == 'Way' and 'highway' in e.tags and 'name' in e.tags:
            try:
                ways_names[e.id] = e.tags['name']
                ways_ref[e.id] = e.refs[0]
            except Exception as e:
                print("Error with %s" % str(e))

    print("Nuber of refs to resolve : %s" % len(ways_ref))
    print("Second pass")
    for e in osm:
        if e.id in ways_ref.values() and e.lonlat:
            wid = list(ways_ref.keys())[list(ways_ref.values()).index(e.id)]
            name = ways_names[wid]
            lon, lat = e.lonlat
            p = get_postcode(lon, lat)
            print("New address ", pc_city[p], p, name, (lon, lat))
            yield [lon, lat, p, pc_city[p], name]


if __name__ == '__main__':
    # @lon;@lat;addr:postcode;addr:city;addr:street;addr:housenumber
    with open(sys.argv[1] + '.csv', 'w') as csv_file:
        writer = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for values in parse():
            print(values)
            writer.writerow(values)
