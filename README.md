# geostatdeploy
Static OGC API Features deployment generator


GeoStatDeploy converts your geodata to a static OGC API Features representation which can be deployed to a webspace such as on Github pages.
The result can be viewed in any OGC API Features compatible client such as QGIS.

As a test you may try to incorporate the test dataset represented in this repository into QGIS using the following URL:

https://situx.github.io/geostatdeploy/index.json

## Why and when to use geostatdeploy 

* You are unable to host an OGC API Features service but you have access to a webspace
* You want to give access to a specific dataset you created to people in a GIS environment using a simple URL
* You want to present your data using the OGC API Features paradigm for a longer period of time without worrying about server maintenance

## Capabilities

Geostatdeploy currently understand the following input data formats:

* SHP
* GeoJSON

More dataformats will follow and GeoStatDeploy will limit itself by the range of dataformats that GeoPandas is capable of.

## How does it work?

GeoStatDeploy creates a Static API representation of OGC API Features data.
A static API is a collection of pre-generated JSON documents and data files which mimic the results of an actual API.

In particular, GeoStatDeploy generates OGC API Features compatible answer documents in JSON for the following requests:

- LandingPage Request
- Conformance Request
- OpenAPI specification Request
- Collections Request
- Feature Request

This allows clients such a QGIS to list statically hosted collections, access their metadata and download these collections as layers into QGIS.

The static API does NOT support HTTP parameters attached to HTTP requests:
- CQL requests
- Parameters such as limit or offset

These parameters are simply ignored because there is no actual web service implementation that could interpret them.
Hence, no matter which parameters are appended, the whole feature collection or metadata description will be returned.

A full deployment can be seen in the gh-pages branch of this repository as data and on the Github page of this repository.
 
