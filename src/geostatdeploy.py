import geopandas
import argparse
from geodatasets import get_path
from geojson_rewind import rewind
import json
import os


htmlheader="""<html><head><title>{{title}}</title>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<script src="https://api.mapbox.com/mapbox.js/plugins/leaflet-fullscreen/v1.0.1/Leaflet.fullscreen.min.js"></script>
<script src="https://code.jquery.com/jquery-3.7.1.min.js" integrity="sha256-/JqT3SQfawRcv/BIHPThkBvs0OEvtFFmqPF/lYI/Cxo=" crossorigin="anonymous"></script>
<link rel="stylesheet" href="https://cdn.datatables.net/2.3.7/css/dataTables.dataTables.css" />
<script src="https://cdn.datatables.net/2.3.7/js/dataTables.js"></script>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"
     integrity="sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY="
     crossorigin=""/>
 <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"
     integrity="sha256-20nQCchB9co0qIjJZRGuk2/Z9VM+kNiyxNV1lvTlZBo="
     crossorigin=""></script>
<script src="index.js">
</script>
<style>
footer{
  list-style: none;
  background-color: #eee;
}
ul.breadcrumb {
  padding: 10px 16px;
  list-style: none;
  background-color: #eee;
}
ul.breadcrumb li {
  display: inline;
  font-size: 18px;
}
ul.breadcrumb li+li:before {
  padding: 8px;
  color: black;
  content: "/\00a0";
}
ul.breadcrumb li a {
  color: #0275d8;
  text-decoration: none;
}
ul.breadcrumb li a:hover {
  color: #01447e;
  text-decoration: underline;
}
</style>
</head>
<body>
<header>
<h3>{{title}}</h3>
{{breadcrumb}}
</header>
<div id="map" style="height:500px;z-index: 0;"></div>
"""

htmlfooter="""
<footer>This page as <a href="index.json">[JSON]</a> <a href="index.html">[HTML]</a>{{footercontent}}
</footer><script>
function generateLeafletPopup(feature, layer){
    var popup="<b>"
    if("name" in feature && feature.name!=""){
        popup+="<a href=\\""+feature.id+"\\" class=\\"footeruri\\" target=\\"_blank\\">"+feature.name+"</a></b><br/><ul>"
    }else{
        popup+="<a href=\\""+feature.id+"\\" class=\\"footeruri\\" target=\\"_blank\\">"+feature.id+"</a></b><br/><ul>"
    }
    for(prop in feature.properties){
        popup+="<li>"
        if(prop.startsWith("http")){
            popup+="<a href=\\""+prop+"\\" target=\\"_blank\\">"+prop.substring(prop.lastIndexOf('/')+1)+"</a>"
        }else{
            popup+=prop
        }
        popup+=" : "
        if(Array.isArray(feature.properties[prop]) && feature.properties[prop].length>1){
            popup+="<ul>"
            for(item of feature.properties[prop]){
                popup+="<li>"
                if((item+"").startsWith("http")){
                    popup+="<a href=\\""+item+"\\" target=\\"_blank\\">"+item.substring(item.lastIndexOf('/')+1)+"</a>"
                }else{
                    popup+=item
                }
                popup+="</li>"
            }
            popup+="</ul>"
        }else if(Array.isArray(feature.properties[prop]) && (feature.properties[prop][0]+"").startsWith("http")){
            popup+="<a href=\\""+feature.properties[prop][0]+"\\" target=\\"_blank\\">"+feature.properties[prop][0].substring(feature.properties[prop][0].lastIndexOf('/')+1)+"</a>"
        }else{
            popup+=feature.properties[prop]+""
        }
        popup+="</li>"
    }
    popup+="</ul>"
    return popup
}
if (document.getElementById("map")){
    const map = L.map('map').setView([51.505, -0.09], 13);
    const tiles = L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
    }).addTo(map);
    featLayer=L.geoJSON(features, {
        onEachFeature: function (feature, layer) {layer.bindPopup(generateLeafletPopup(feature, layer))}
    }).addTo(map);
    map.fitBounds(featLayer.getBounds());
}
if (document.getElementById("feattable")){
    $('#feattable').DataTable();
}
</script>
"""

parser=argparse.ArgumentParser()
parser.add_argument("-i","--input",nargs='*',help="the input directory to parse for geo files",action="store",required=False,default=".")
parser.add_argument("-o","--output",nargs='*',help="the output path(s)",action="store",required=False,default="result")
parser.add_argument("-dp","--deploypath",help="the deploypath where the documentation will be hosted",action="store",default="https://situx.github.io/geostatdeploy/")
parser.add_argument("-tp","--templatepath",help="the path of the HTML template",action="store",default="resources/html/")
parser.add_argument("-tn","--templatename",help="the name of the HTML template",action="store",default="default")
args, unknown=parser.parse_known_args()

print(args)
print("The following arguments were not recognized: "+str(unknown))

outpath = args.output
rootdir = args.input
deploypath = args.deploypath

if deploypath.endswith("/"):
    deploypath=deploypath[0:-1]

apihtml = "<!DOCTYPE html><html lang=\"en\"><head><meta charset=\"utf-8\" /><meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" /><metaname=\"description\" content=\"SwaggerUI\"/><title>SwaggerUI</title><link rel=\"stylesheet\" href=\"https://unpkg.com/swagger-ui-dist/swagger-ui.css\" /></head><body><div id=\"swagger-ui\"></div><script src=\"https://unpkg.com/swagger-ui-dist/swagger-ui-bundle.js\" crossorigin></script><script>const swaggerUrl = \"" + str(
            deploypath) + "/api/index.json\"; const apiUrl = \"" + str(
            deploypath) + "/\";  window.onload = () => {let swaggerJson = fetch(swaggerUrl).then(r => r.json().then(j => {j.servers[0].url = apiUrl; window.ui = SwaggerUIBundle({spec: j,dom_id: '#swagger-ui'});}));};</script></body></html>"

def formatCRS(crs):
    if "EPSG:" in crs:
        return "http://www.opengis.net/def/crs/EPSG/0/"+str(crs[crs.rfind(":")+1:])
    return crs

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



indexhtml="<html><head><title>Indexpage</title></head><body><h3>Static OGC API Features</h3>This is the landing page of this static OGC API features service.<ul><li><a href=\"api/api.html\">API as HTML</a></li><li><a href=\"collections/indexc.html\">Collections</li><li><a href=\"conformance/index.html\">Conformance</a></li></ul></body></html>"
collectionsjson = {"collections": [], "links": [
    {"href": deploypath + "/collections/index.json", "rel": "self", "type": "application/json",
     "title": "this document as JSON"},
    {"href": deploypath + "/collections/indexc.html", "rel": "alternate", "type": "text/html",
     "title": "this document as HTML"}]}
collectionshtml = htmlheader.replace("{{title}}","Collections of " + str(deploypath))+"{{collectiontable}}"+htmlfooter.replace("{{footercontent}}","").replace("id=\"map\"","id=\"nomap\"")+"</body></html>"
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
    {"href": str(deploypath) + "/conformance/index.json", "rel": "conformance", "type": "application/json",
     "title": "OGC API conformance classes as Json"},
    {"href": str(deploypath) + "/conformance", "rel": "conformance", "type": "text/html",
     "title": "OGC API conformance classes as HTML"}]}

apijson = {"openapi": "3.0.1", "info": {"title": f"{deploypath} Feature Collections",
                                        "description": f"Feature Collections of {deploypath}","version":"1.0"},
            "servers": [{"url": str(deploypath)}], "paths": {}}

apijson["paths"][f"{deploypath}/api"] = {
    "get": {"tags": ["Capabilities"], "summary": "api documentation", "description": "api documentation",
            "operationId": "openApi", "parameters": [], "responses": {
            "default": {"description": "default response","content": {"application/vnd.oai.openapi+json;version=3.0": {},"application/json": {}, "text/html": {"schema": {}}}}}}}
apijson["paths"][f"{deploypath}/license/dataset"] = {}
apijson["components"] = {"schemas": {"Conformance": {"type": "object", "properties": {
    "conformsTo": {"type": "array", "items": {"type": "string"}}}, "xml": {"name": "ConformsTo","namespace": "http://www.opengis.net/ogcapi-features-1/1.0"}},
                                        "Collection": {"type": "object", "properties": {
                                            "id": {"type": "string", "xml": {"name": "Id","namespace": "http://www.opengis.net/ogcapi-features-1/1.0"}},
                                            "title": {"type": "string", "xml": {"name": "Title","namespace": "http://www.opengis.net/ogcapi-features-1/1.0"}},
                                            "description": {"type": "string", "xml": {"name": "Description","namespace": "http://www.opengis.net/ogcapi-features-1/1.0"}},
                                            "links": {"type": "array", "xml": {"name": "link","namespace": "http://www.w3.org/2005/Atom"},"items": {"$ref": "#/components/schemas/Link"}},
                                            "extent": {"$ref": "#/components/schemas/Extent"},
                                            "itemType": {"type": "string"},
                                            "crs": {"type": "array", "items": {"type": "string"}},
                                            "storageCrs": {"type": "string"}}, "xml": {"name": "Collection","namespace": "http://www.opengis.net/ogcapi-features-1/1.0"}},
                                        "Collections": {"type": "object", "properties": {
                                            "links": {"type": "array", "xml": {"name": "link","namespace": "http://www.w3.org/2005/Atom"},"items": {"$ref": "#/components/schemas/Link"}},
                                            "collections": {"type": "array", "xml": {"name": "Collection","namespace": "http://www.opengis.net/ogcapi-features-1/1.0"},
                                                        "items": {"$ref": "#/components/schemas/Collection"}}},
                                                        "xml": {"name": "Collections","namespace": "http://www.opengis.net/ogcapi-features-1/1.0"}},
                                        "Extent": {"type": "object", "properties": {
                                            "spatial": {"$ref": "#/components/schemas/Spatial"},
                                            "temporal": {"$ref": "#/components/schemas/Temporal"}},
                                            "xml": {"name": "Extent","namespace": "http://www.opengis.net/ogcapi-features-1/1.0"}},
                                        "Link": {"type": "object", "properties": {
                                            "href": {"type": "string", "xml": {"attribute": True}},
                                            "rel": {"type": "string", "xml": {"attribute": True}},
                                            "type": {"type": "string", "xml": {"attribute": True}},
                                            "title": {"type": "string", "xml": {"attribute": True}}},
                                            "xml": {"name": "link","namespace": "http://www.w3.org/2005/Atom"}},
                                        "Spatial": {"type": "object", "properties": {"bbox": {"type": "array",
                                                    "items": {"type": "array","items": {"type": "number","format": "double"}}},
                                                    "crs": {"type": "string","xml": {"attribute": True}}},
                                                    "xml": {"name": "SpatialExtent","namespace": "http://www.opengis.net/ogcapi-features-1/1.0"}},
                                        "Temporal": {"type": "object", "properties": {
                                            "interval": {"type": "array","items": {"type": "string", "format": "date-time"}},
                                            "trs": {"type": "string", "xml": {"attribute": True}}},"xml": {"name": "TemporalExtent","namespace": "http://www.opengis.net/ogcapi-features-1/1.0"}},
                                        "LandingPage": {"type": "object"}}}
apijson["paths"][f"{deploypath}/"] = {"get": {"tags": ["Capabilities"], "summary": "landing page",
        "description": "Landing page of this dataset","operationId": "landingPage", "parameters": [], "responses": {
        "default": {"description": "default response", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/LandingPage"}},"text/html": {"schema": {}}}}}}}
apijson["paths"][f"{deploypath}/conformance"] = {
    "get": {"tags": ["Capabilities"], "summary": "supported conformance classes",
            "description": "Retrieves the supported conformance classes", "operationId": "conformance",
            "parameters": [], "responses": {"default": {"description": "default response", "content": {
            "application/json": {"schema": {"$ref": "#/components/schemas/Conformance"}},"text/ttl": {"schema": {}}, "text/html": {"schema": {}}}}}}}
apijson["paths"][f"{deploypath}/collections"] = {"get": {"tags": ["Collections"], "summary": "describes collections",
                                            "description": "Describes all collections provided by this service",
                                            "operationId": "collections", "parameters": [], "responses": {
        "default": {"description": "default response", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Collections"}},
            "text/ttl": {"schema": {}}, "text/html": {"schema": {}}}}}}}

conformancejson = {"conformsTo": ["http://www.opengis.net/spec/ogcapi-features-1/1.0/conf/core",
                                  "http://www.opengis.net/spec/ogcapi-features-1/1.0/conf/html",
                                  "http://www.opengis.net/spec/ogcapi-features-1/1.0/conf/oas30",
                                  "http://www.opengis.net/spec/ogcapi-features-1/1.0/conf/geojson"]}

featurecollections = {}
createFolders(outpath)
with open(outpath + "/conformance/index.json", 'w', encoding="utf-8") as f:
    json.dump(conformancejson, f, indent=2)

with open(outpath + "/conformance/index.html", 'w', encoding="utf-8") as f:
    json.dump(conformancejson, f, indent=2)

with open(outpath + "/index.json", 'w', encoding="utf-8") as f:
    json.dump(landingpagejson, f, indent=2)


counter = 1
for file in os.listdir(rootdir):
    print(file)
    if ".shp" in file or ".geojson" in file:
        gdf = geopandas.read_file(rootdir + "/" + file, encoding="utf-8")
        gdfbbox = gdf.total_bounds
        print(gdfbbox)
        dtypes=gdf.dtypes
        tomodify=[]
        for i, tp in dtypes.items():
            #print(str(i)+" - "+str(tp))
            if "datetime" in str(tp):
                gdf[i]=gdf[i].astype("string")
        print(gdf.dtypes)
        fileid = file[0:file.rfind(".")]
        coll=fileid
        cname=str(coll).replace(outpath, "").replace("index.geojson", "").replace(".geojson", "").rstrip("/")
        apijson["paths"][deploypath[0:-1]+f"{deploypath[-1:]}/collections/" + cname] = {
            "get": {"tags": ["Collections"], "summary": "describes collection " + cname, "description": "Describes the collection with the id " + cname, "operationId": "collection-" + str(
                coll).replace(outpath, "").replace("index.geojson", "").replace(".geojson", ""),
                    "parameters": [], "responses": {"default": {"description": "default response", "content": {
                    "application/json": {"schema": {"$ref": "#/components/schemas/Collections"},"example": None}}}}}}
        apijson["paths"][deploypath[0:-1]+f'{deploypath[-1:]}/collections/{cname}/items/index.json'.replace("//", "/")] = {"get": {"tags": ["Data"],"summary": "retrieves features of collection " + cname.rstrip("/"),
                "description": "Retrieves features of collection  " + cname,"operationId": "features-" + cname,"parameters": [], "responses": {
        "default": {"description": "default response","content": {"application/geo+json": {"example": None}},"text/ttl": {"schema": {"example": None}, "example": None},"text/html": {"schema": {"example": None}, "example": None}}}}}
        apijson["paths"][deploypath[0:-1]+f"{deploypath[-1:]}/collections/{cname}/items/{{featureId}}/index.json".replace("//", "/")] = {"get": {"tags": ["Data"],
                                                                                    "summary": "retrieves feature of collection " + cname.rstrip("/"),
                                                                                    "description": "Retrieves one single feature of the collection with the id " + cname,
                                                                                    "operationId": "feature-" + cname, "parameters": [
                {"name": "featureId", "in": "path", "required": True, "schema": {"type": "string"}}],"responses": {"default": {"description": "default response",
                                                                                            "content": {"application/geo+json": {"example": None}},
                                                                                            "text/ttl": {"schema": {"example": None},"example": None},
                                                                                            "text/html": {"schema": {"example": None},"example": None}}}}}
        curcoll = {"id": fileid, "title": fileid,  "links": [
            {"href": deploypath + "/collections/" + fileid + "/items/index.json", "rel": "items","type": "application/json", "title": "Collection as JSON"},
            {"href": deploypath + "/collections/" + fileid+"/items/indexc.html" , "rel": "items", "type": "text/html","title": "Collection as HTML"},
            {"href": deploypath + "/collections/" + fileid + "/items/index.ttl", "rel": "items", "type": "text/ttl","title": "Collection as TTL"}
        ], "itemType": "feature", "extent": {"spatial": {"bbox": [gdfbbox[0], gdfbbox[2], gdfbbox[1], gdfbbox[3]], "crs":formatCRS(str(gdf.crs))}},"crs":[formatCRS(str(gdf.crs))]}
        collectionsjson["collections"].append({"id": fileid,"title": fileid, "links": [{"href": deploypath + "/collections/" + fileid + "/index.json", "rel": "collection",
             "type": "application/json", "title": "Collection as JSON"},
            {"href": deploypath + "/collections/" + fileid+"/indexc.html" , "rel": "collection", "type": "text/html","title": "Collection as HTML"},
            {"href": deploypath + "/collections/" + fileid + "/index.ttl", "rel": "collection", "type": "text/ttl","title": "Collection as TTL"}],
            "extent": {"spatial": {"bbox": [gdfbbox[0], gdfbbox[2], gdfbbox[1], gdfbbox[3]], "crs":formatCRS(str(gdf.crs))}},"crs":[formatCRS(str(gdf.crs))]})
        if not os.path.exists(outpath + "/collections/" + fileid):
            os.makedirs(outpath + "/collections/" + fileid)
        with open(outpath + "/collections/" + fileid + "/index.json", 'w', encoding="utf-8") as f:
            json.dump(curcoll, f, indent=2)
        with open(outpath + "/collections/" + fileid + "/index.html", 'w', encoding="utf-8") as f:
            json.dump(curcoll, f, indent=2)
        with open(outpath + "/collections/" + fileid + "/index.js", 'w', encoding="utf-8") as f:
            thegjson={"type":"Feature","name":str(fileid)+" BBOX","properties":{},"geometry":{"type":"Polygon","coordinates":[[[curcoll["extent"]["spatial"]["bbox"][0],curcoll["extent"]["spatial"]["bbox"][1]], [curcoll["extent"]["spatial"]["bbox"][3],curcoll["extent"]["spatial"]["bbox"][1]], [curcoll["extent"]["spatial"]["bbox"][3],curcoll["extent"]["spatial"]["bbox"][2]], [curcoll["extent"]["spatial"]["bbox"][1],curcoll["extent"]["spatial"]["bbox"][3]], [curcoll["extent"]["spatial"]["bbox"][0],curcoll["extent"]["spatial"]["bbox"][1]] ]]}}
            f.write("var features="+json.dumps(thegjson,indent=2))
        curcolhtml = collectiontabletemp + "<tr><td><a href=\"" + fileid + "\">" + fileid + "</a></td><td><a href=\"items/indexc.html\">[Collection as HTML]</a>&nbsp;<a href=\"items/index.json/\">[Collection as JSON]</a></td></tr>"
        with open(outpath + "/collections/" + fileid + "/indexc.html", 'w', encoding="utf-8") as f:
            breadcrumb="<ul class=\"breadcrumb\"><li><a href=\"../../../\">Home</a></li><li><a href=\"../indexc.html\">Collections</a></li><li>"+fileid+"</li></ul>"""
            f.write(htmlheader.replace("{{title}}","Collection: "+str(fileid)).replace("{{breadcrumb}}",breadcrumb))
            f.write("<ul><li><a href=\"items/indexc.html\">Details</a></li></ul>")
            f.write(htmlfooter.replace("{{footercontent}}",""))
        geodict = gdf.to_geo_dict()
        collectiontable += "<tr><td><a href=\"" + fileid + "/indexc.html\">" + fileid + "</a></td><td><a href=\"" + fileid + "/index.json/\">[Collection as JSON]</a></td></tr>"
        if not os.path.exists(outpath + "/collections/" + fileid + "/items/"):
            os.makedirs(outpath + "/collections/" + fileid + "/items/")
        res=json.loads(gdf.to_json())
        flen=len(res["features"])
        res["numberMatched"]=flen
        res["numberReturned"]=flen
        res["crs"]=[formatCRS(str(gdf.crs))]
        with open(outpath + "/collections/" + fileid + "/items/index.json", 'w', encoding="utf-8") as f:
            json.dump(rewind(res),f, indent=2)
        with open(outpath + "/collections/" + fileid + "/items/index.js", 'w', encoding="utf-8") as f:
            f.write("var features="+json.dumps(rewind(res), indent=2))
        with open(outpath + "/collections/" + fileid + "/items/index.html", 'w', encoding="utf-8") as f:
            json.dump(rewind(res),f, indent=2)
        with open(outpath + "/collections/" + fileid + "/items/indexc.html", 'w', encoding="utf-8") as f:
            breadcrumb="<ul class=\"breadcrumb\"><li><a href=\"../../../\">Home</a></li><li><a href=\"../../indexc.html\">Collections</a></li><li><a href=\"../indexc.html\">"+fileid+"</a></li><li>Items</li></ul>"""
            f.write(htmlheader.replace("{{title}}",str(fileid)+" Features").replace("{{breadcrumb}}",breadcrumb))
            f.write(gdf.to_html().replace("<table ","<table id=\"feattable\" "))
            f.write(htmlfooter.replace("{{footercontent}}",""))
            f.write("</body></html>")
        i = 0
        outdict={"type":"Collection","features":[]}
        for row in gdf.itertuples():
            fid = gdf.iloc[[i]].to_geo_dict()["features"][0]["id"]
            if not os.path.exists(outpath + "/collections/" + fileid + "/items/" + str(fid) + "/"):
                os.makedirs(outpath + "/collections/" + fileid + "/items/" + str(fid) + "/")
            res=json.loads(gdf.iloc[[i]].to_json())["features"][0]
            res["numberMatched"]=1
            res["numberReturned"]=1
            res["crs"]=[formatCRS(str(gdf.crs))]
            res["links"]=[{
                "href": deploypath+"/collections/" + fileid + "/items/" + str(fid),
                "rel": "self",
                "type": "application/json",
                "title": "this document as JSON"
            }]
            with open(outpath + "/collections/" + fileid + "/items/" + str(fid) + "/index.json", 'w',encoding="utf-8") as f:
                json.dump(rewind(res),f, indent=2)
            with open(outpath + "/collections/" + fileid + "/items/" + str(fid) + "/index.js", 'w',encoding="utf-8") as f:
                res["links"]=[{
                    "href": deploypath+"/collections/" + fileid + "/items/" + str(fid),
                    "rel": "self",
                    "type": "application/json",
                    "title": "this document as JS"
                }]
                f.write("var features="+json.dumps(rewind(res), indent=2))
            with open(outpath + "/collections/" + fileid + "/items/" + str(fid) + "/index.html", 'w',encoding="utf-8") as f:
                res["links"]=[{
                    "href": deploypath+"/collections/" + fileid + "/items/" + str(fid),
                    "rel": "self",
                    "type": "application/json",
                    "title": "this document as JSON"
                }]
                json.dump(rewind(res),f, indent=2)
            with open(outpath + "/collections/" + fileid + "/items/" + str(fid) + "/indexc.html", 'w',encoding="utf-8") as f:
                breadcrumb="<ul class=\"breadcrumb\"><li><a href=\"../../../../\">Home</a></li><li><a href=\"../../../indexc.html\">Collections</a></li><li><a href=\"../../indexc.html\">"+fileid+"</a></li><li><a href=\"../indexc.html\">Items</a></li><li>"+str(fid)+"</li></ul>"""
                f.write(htmlheader.replace("{{title}}",fid).replace("{{breadcrumb}}",breadcrumb))
                f.write(gdf.iloc[[i]].to_html().replace("<table ","<table id=\"feattable\" "))
                f.write(htmlfooter.replace("{{footercontent}}",""))
                f.write("</body></html>")
            i += 1
collectiontable += "</tbody></table>"
with open(outpath + "/collections/index.json", 'w', encoding="utf-8") as f:
    json.dump(collectionsjson, f, indent=2)

with open(outpath + "/collections/index.html", 'w', encoding="utf-8") as f:
    json.dump(collectionsjson, f, indent=2)

with open(outpath + "/index.html", 'w', encoding="utf-8") as f:
    f.write(indexhtml)

with open(outpath + "/collections/indexc.html", 'w', encoding="utf-8") as f:
    f.write(collectionshtml.replace("{{collectiontable}}", collectiontable))

with open(f"{outpath}/api/index.json", "w", encoding="utf-8") as f:
    json.dump(apijson,f)
with open(f"{outpath}/api/index.html", "w", encoding="utf-8") as f:
    json.dump(apijson,f)
with open(f"{outpath}/api/api.html", "w", encoding="utf-8") as f:
    f.write(apihtml)
