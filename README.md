[![SWH](https://archive.softwareheritage.org/badge/origin/https://github.com/scampion/opengeocode/)](https://archive.softwareheritage.org/browse/origin/?origin_url=https://github.com/scampion/opengeocode)

[![SWH](https://archive.softwareheritage.org/badge/swh:1:rev:7d0916ac7a43b0d811e4e66c23b69720139068e6/)](https://archive.softwareheritage.org/swh:1:rev:7d0916ac7a43b0d811e4e66c23b69720139068e6;origin=https://github.com/scampion/opengeocode;visit=swh:1:snp:48d8937d82bd177e3ce4654705d358e06a8f2895/)

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.4273721.svg)](https://doi.org/10.5281/zenodo.4273721)


Open GeoCoding
==============

![Logo](images/ogc.svg)


**Ultra fast fuzzy match address geocode resolution HTTP API Server based on Open Street Map.**

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


Cite
----

```
@software {
  title = {OpenGeocode},
  author = {Campion Sebastien},
  date = {2020},
  license = {AGPL},
  url = {https://www.scamp.fr/opengeocode},
  abstract = {Fast fuzzy match address geocode resolution HTTP API Server based on Open Street Map.},
  repository= {https://github.com/scampion/opengeocode},
  swhid = {swh:1:rev:7d0916ac7a43b0d811e4e66c23b69720139068e6;origin=https://github.com/scampion/opengeocode;visit=swh:1:snp:48d8937d82bd177e3ce4654705d358e06a8f2895},
}
```


