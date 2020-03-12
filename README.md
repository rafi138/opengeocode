Open GeoCoding
==============
HTTP API Fuzzy match address resolution to longitude, latitude coordinate

Based on open street map data, available at https://download.geofabrik.de/ indexed using trigrams extension of PostgreSQL.

Author: Sebastien Campion



Load data in memory 
--------------------
See load script for detail 

    curl --request POST   -F file=@monaco.csv http://localhost:5555/load


Query 
-----

    [0] % curl "http://localhost:5555/monaco?q=Moulins"
    {   
      "coord": [
        "7.4260295",
        "43.7407400"
      ],
      "query": "Moulins",
      "result": "('MC', '98000', 'Monte-Carlo', 'Boulevard des Moulins', '2')"
    }



