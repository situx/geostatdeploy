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
collectiontabletemp = "<table><thead><th>Collection</th><th>Links</th></thead><tbody>"

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
with open(outpath + "/conformance/index.json", 'w',encoding="utf-8") as f:
    json.dump(conformancejson, f,indent=2)
    
with open(outpath + "/index.json", 'w',encoding="utf-8") as f:
    json.dump(landingpagejson, f,indent=2)

createFolders(outpath)
rootdir="."
counter=1
for file in os.listdir(rootdir):
    print(file)
    if ".shp" in file or ".geojson" in file:
        gdf = geopandas.read_file(rootdir+"/"+file,encoding="utf-8")
        gdfbbox=gdf.total_bounds
        print(gdfbbox)
        fileid=file[0:file.rfind(".")]
        curcoll={"id":fileid,"name":fileid,"links":[
        {"href":deploypath+"/collections/"+fileid+"/index.json","rel":"collection","type":"application/json","title":"Collection as JSON"},
        {"href":deploypath+"/collections/"+fileid+"/","rel":"collection","type":"text/html","title":"Collection as HTML"},
        {"href":deploypath+"/collections/"+fileid+"/index.ttl","rel":"collection","type":"text/ttl","title":"Collection as TTL"}
        ],"extent":{"spatial":{"bbox":[gdfbbox[0],gdfbbox[2],gdfbbox[1],gdfbbox[3]],"crs":str(gdf.crs)}}}
        collectionsjson["collections"].append(curcoll)
        if not os.path.exists(outpath+"/collections/"+fileid):
            os.makedirs(outpath+"/collections/"+fileid)
        with open(outpath+"/collections/"+fileid+"/index.json", 'w',encoding="utf-8") as f:
            json.dump(curcoll, f,indent=2)
        curcolhtml=collectiontabletemp+"<tr><td><a href=\""+fileid+"\">"+fileid+"</a></td><td><a href=\""+fileid+"/index.html\">[Collection as HTML]</a>&nbsp;<a href=\""+fileid+"/index.json/\">[Collection as JSON]</a></td></tr>"
        with open(outpath+"/collections/"+fileid+"/index.html", 'w',encoding="utf-8") as f:
            f.write(collectionshtml.replace("{{collectiontable}}", curcolhtml))
        geodict=gdf.to_geo_dict()
        collectiontable+="<tr><td><a href=\""+fileid+"\">"+fileid+"</a></td><td><a href=\""+fileid+"/index.html\">[Collection as HTML]</a>&nbsp;<a href=\""+fileid+"/index.json/\">[Collection as JSON]</a></td></tr>"
        if not os.path.exists(outpath + "/collections/"+fileid+"/items/"):
            os.makedirs(outpath + "/collections/"+fileid+"/items/")
        with open(outpath + "/collections/"+fileid+"/items/index.json", 'w',encoding="utf-8") as f:
            json.dump(geodict, f,indent=2)
        i=0
        for row in gdf.itertuples():
            fid=gdf.iloc[[i]].to_geo_dict()["features"][0]["id"]
            if not os.path.exists(outpath + "/collections/"+fileid+"/items/"+str(fid)+"/"):
                os.makedirs(outpath + "/collections/"+fileid+"/items/"+str(fid)+"/")
            with open(outpath + "/collections/"+fileid+"/items/"+str(fid)+"/index.json", 'w',encoding="utf-8") as f:
                json.dump(gdf.iloc[[i]].to_geo_dict()["features"][0], f,indent=2)  
            with open(outpath + "/collections/"+fileid+"/items/"+str(fid)+"/index.html", 'w',encoding="utf-8") as f:
                f.write(gdf.iloc[[i]].to_html())  
            i+=1                
collectiontable+="</tbody></table>"
with open(outpath + "/collections/index.json", 'w',encoding="utf-8") as f:
    json.dump(collectionsjson, f,indent=2)

with open(outpath + "/collections/index.html", 'w',encoding="utf-8") as f:
    f.write(collectionshtml.replace("{{collectiontable}}",collectiontable))
    



