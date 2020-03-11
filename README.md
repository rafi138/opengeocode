Open GeoCoding
==============
HTTP API Fuzzy match address resolution to longitude, latitude coordinate

Based on open street map data, available at https://download.geofabrik.de/ indexed using trigrams extension of PostgreSQL.

Run it 
-------

Lauch on port 5000

    docker-compose up 


HTTP GET API :
--------------
    http://localhost:5000/country/city
    http://localhost:5000/country/city/postcode
    http://localhost:5000/country/city/postcode/street
    http://localhost:5000/country/city/postcode/street/housenumber


Example :
_________


    curl http://localhost:5000/belgium/Maasmechelen/3630/Rijksweg/431

Response:

```json
{
  "request": null,
  "response": [
    [
      5.6952999,
      50.9601391,
      "BE",
      "3630",
      "Maasmechelen",
      "Rijksweg",
      "431",
      4.0
    ]
  ],
  "time": 142.05574989318848
}

```

HTTP POST API :
---------------

HTTP post on endpoint /json with header Content-Type: application/json.

In you file myquery.json:
```json
{
  "country":"belgium",
  "postcode":"Rijksweg",
  "city": "Maasmechelen",
  "street": "Rijksweg",
  "housenumber": "431"
}
```

Post it using the following command :

    curl --header "Content-Type: application/json"  --request POST  --data @myquery.json  http://localhost:5000/resolve

Result:


```json
{
  "request": {
    "city": "Maasmechelen",
    "country": "belgium",
    "housenumber": "431",
    "postcode": "3630",
    "street": "Rijksweg"
  },
  "response": [
    [
      5.6952999,
      50.9601391,
      "BE",
      "3630",
      "Maasmechelen",
      "Rijksweg",
      "431",
      4.0
    ]
  ],
  "time": 143.88608932495117
}
```


Provisioning :
--------------

This step download osm data, convert it in csv, create table in postgres and load it.

Here a toy example :

    docker-compose run ogc /app/ogc_import europe monaco

/!\ params are used to build the following osm url : **https://download.geofabrik.de/$CONTINENT/$COUNTRY-latest.osm.pbf**


