Open GeoCoding
--------------
HTTP API Fuzzy match address resolution to longitude, latitude coordinate


Based on open street map data, available at https://download.geofabrik.de/

Example
_______

HTTP post on endpoint /resolve with header Content-Type: application/json : 

```json
{
  "country":"belgium",
  "postcode":"3630",
  "city": "Maasmechelen",
  "street": "Rijksweg",
  "housenumber": "431"
}
```

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
______________

This step download osm data, convert it in csv, create table in postgres and load it.

Here a toy example :

    docker-compose run ogc /app/ogc_import europe monaco

/!\ params are used to build the following osm url : **https://download.geofabrik.de/$CONTINENT/$COUNTRY-latest.osm.pbf**


Lauch on port 5000
__________________

    docker-compose up 


You can use the script resolve to the it 

    ./resolve tests/debug.json