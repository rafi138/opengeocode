Open GeoCoding
==============

![Logo](images/ogc.svg)


**Ultra fast fuzzy match address geocode resolution HTTP API.**

This software provides an HTTP Rest API to resolve an address in a string format (even malformed)  into longitude & latitude coordinates. 
It can use to replace commercial APIs like [Microsoft Bing](https://www.bing.com/api/maps/sdkrelease/mapcontrol/isdk/searchbyaddress) or [Google Maps](https://developers.google.com/maps/documentation/geocoding/intro)


Based on [open street map data](https://download.geofabrik.de), an in-memory index is built on the fly using ngrams. Deploy on-premise, it offers an efficient way to solve large scale geocode compute with a high throughput and a low latency.

Author: Sebastien Campion

![Screenshot](images/screenshot.png)


Load data  
---------

In memory and in a persistance way using data directory.

Using command line : 

    ./ogc -l monaco.csv -l belgium.csv 
    
Using HTTP, see load script for osm conversion : 

    curl --request POST   -F file=@monaco.csv http://localhost:5555/load

Run 
----

	./ogc -w
	

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



