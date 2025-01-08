import geopandas
from geodatasets import get_path
import json
import os

outpath="public"
deploypath="https://situx.github.io/public/"

def createFolders(outpath):
    if not os.path.exists(outpath):
        os.makedirs(outpath)
    if not os.path.exists(outpath + "/api/"):
        os.makedirs(outpath + "/api/")
    if not os.path.exists(outpath + "/license/"):
        os.makedirs(outpath + "/license/")
    if not os.path.exists(outpath + "/collections/"):
        os.makedirs(outpath + "/collections/")
    if not os.path.exists(outpath + "/conformance/"):
        os.makedirs(outpath + "/conformance/")

collectionsjson = {"collections": [], "links": [
    {"href": outpath + "collections/index.json", "rel": "self", "type": "application/json",
     "title": "this document as JSON"},
    {"href": outpath + "collections/index.html", "rel": "self", "type": "text/html",
     "title": "this document as HTML"}]}
collectionshtml = "<html><head></head><body><header><h1>Collections of " + str(deploypath) + "</h1></head>{{collectiontable}}<footer><a href=\"index.json\">This page as JSON</a></footer></body></html>"
collectiontable = "<table><thead><th>Collection</th><th>Links</th></thead><tbody>"

landingpagejson = {"title": "Landing Page", "description": "Landing Page", "links": [{
    "href": str(deploypath) + "/index.json",
    "rel": "self",
    "type": "application/json",
    "title": "this document as JSON"
}, {
    "href": str(deploypath) + "/index.html",
    "rel": "alternate",
    "type": "text/html",
    "title": "this document as HTML"
}, {
    "href": str(deploypath) + "/collections/",
    "rel": "data",
    "type": "application/json",
    "title": "Supported Feature Collections as JSON"
}, {
    "href": str(deploypath) + "/collections/indexc.html",
    "rel": "data",
    "type": "text/html",
    "title": "Supported Feature Collections as HTML"
}, {"href": str(deploypath) + "/api/index.json", "rel": "service-desc",
    "type": "application/vnd.oai.openapi+json;version=3.0", "title": "API definition"},
    {"href": str(deploypath) + "/api", "rel": "service-desc", "type": "text/html",
     "title": "API definition as HTML"},
    {"href": str(deploypath) + "/conformance", "rel": "conformance", "type": "application/json",
     "title": "OGC API conformance classes as Json"},
    {"href": str(deploypath) + "/conformance", "rel": "conformance", "type": "text/html",
     "title": "OGC API conformance classes as HTML"}]}

conformancejson = {"conformsTo": ["http://www.opengis.net/spec/ogcapi-features-1/1.0/conf/core",
                                  "http://www.opengis.net/spec/ogcapi-features-1/1.0/conf/html",
                                  "http://www.opengis.net/spec/ogcapi-features-1/1.0/conf/oas30",
                                  "http://www.opengis.net/spec/ogcapi-features-1/1.0/conf/geojson"]}

featurecollections={}


createFolders(outpath)
rootdir="."
counter=1
for file in os.listdir(rootdir):
    print(file)
    if ".shp" in file or ".geojson" in file:
        gdf = geopandas.read_file(rootdir+"/"+file)
        gdfbbox=gdf.total_bounds
        print(gdfbbox)
        fileid=file[0:file.rfind(".")]
        if not os.path.exists(outpath+"/collections/"+fileid):
            os.makedirs(outpath+"/collections/"+fileid)
        curcoll={"id":fileid,"name":fileid,"links":[
        {"href":deploypath+"/collections/"+fileid+"/index.json","rel":"collection","type":"application/json","title":"Collection as JSON"},
        {"href":deploypath+"/collections/"+fileid+"/","rel":"collection","type":"text/html","title":"Collection as HTML"},
        {"href":deploypath+"/collections/"+fileid+"/index.ttl","rel":"collection","type":"text/ttl","title":"Collection as TTL"}
        ],"extent":{"spatial":{"bbox":[gdfbbox[0],gdfbbox[2],gdfbbox[1],gdfbbox[3]],"crs":str(gdf.crs)}}}
        collectionsjson["collections"].append(curcoll)
        with open(outpath+"/collections/"+fileid+"/index.json", 'w',encoding="utf-8") as f:
            json.dump(curcoll, f,indent=2)
        geodict=gdf.to_geo_dict()
        for row in gdf.itertuples():
            
            
            print(f"row with index {row.Index} has content <{row}>")
with open(outpath + "/collections/index.json", 'w',encoding="utf-8") as f:
    json.dump(collectionsjson, f,indent=2)


