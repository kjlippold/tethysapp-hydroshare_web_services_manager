import requests
import json
from .app import HydroshareWebServicesManager as app
from tethys_apps.models import TethysApp
import os


db_app = TethysApp.objects.get(package=app.package)
custom_settings = db_app.custom_settings


def get_layer_style(self, max_value, min_value, ndv_value, layer_id):
    
    # Sets default style for raster layers
    layer_style = """<?xml version="1.0" encoding="ISO-8859-1"?>
    <StyledLayerDescriptor version="1.0.0" xmlns="http://www.opengis.net/sld" xmlns:ogc="http://www.opengis.net/ogc"
      xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
      xsi:schemaLocation="http://www.opengis.net/sld http://schemas.opengis.net/sld/1.0.0/StyledLayerDescriptor.xsd">
      <NamedLayer>
        <Name>simpleraster</Name>
        <UserStyle>
          <Name>%s</Name>
          <Title>Simple raster style</Title>
          <Abstract>Simple raster style</Abstract>
          <FeatureTypeStyle>
            <Rule>
              <RasterSymbolizer>
                <Opacity>1.0</Opacity>
                <ColorMap>
                  <ColorMapEntry color="#000000" quantity="%s" label="nodata" opacity="0.0" />
                  <ColorMapEntry color="#000000" quantity="%s" label="values" />
                  <ColorMapEntry color="#FFFFFF" quantity="%s" label="values" />
                </ColorMap>
              </RasterSymbolizer>
            </Rule>
          </FeatureTypeStyle>
        </UserStyle>
      </NamedLayer>
    </StyledLayerDescriptor>""" % (layer_id, ndv_value, min_value, max_value)
    return layer_style


def remove_geoserver_workspace(workspace_id):
    geoserver_url = custom_settings.get(name='geoserver_url').value
    geoserver_user = custom_settings.get(name='geoserver_user').value
    geoserver_pass = custom_settings.get(name='geoserver_pass').value
    geoserver_auth = requests.auth.HTTPBasicAuth(
        geoserver_user, 
        geoserver_pass
    )
    headers = {
        "content-type": "application/json"
    }
    params = {
        "update": "overwrite", "recurse": True
    }
    rest_url = "/".join((geoserver_url, "workspaces", workspace_id))
    response = requests.delete(rest_url, params=params, auth=geoserver_auth, headers=headers)
    #print(response.status_code)


def add_geoserver_workspace(res_id):
    geoserver_url = custom_settings.get(name='geoserver_url').value
    geoserver_user = custom_settings.get(name='geoserver_user').value
    geoserver_pass = custom_settings.get(name='geoserver_pass').value
    geoserver_auth = requests.auth.HTTPBasicAuth(
        geoserver_user, 
        geoserver_pass
    )
    headers = {"content-type": "application/json"}
    workspace_id = "HS-" + str(res_id)
    remove_geoserver_workspace(workspace_id)
    data = json.dumps({"workspace": {"name": workspace_id}})
    rest_url = "/".join((geoserver_url, "workspaces"))
    response = requests.post(rest_url, headers=headers, data=data, auth=geoserver_auth)
    #print(response)
    return workspace_id


def get_database_list(res_id):

    db_list = {
        "geoserver": [],
        "wof": []
    }

    hydroshare_url = custom_settings.get(name='hydroshare_url').value
    rest_url = "/".join((hydroshare_url, "resource", res_id, "file_list"))
    print(rest_url)
    response = requests.get(rest_url)
    print(response)
    print(response.content)
    if response.status_code != 200:
        return "Invalid"

    file_list = json.loads(response.content.decode('utf-8'))["results"]

    for result in file_list:
        if (result["logical_file_type"] == "GeoRasterLogicalFile" and result["content_type"] == "image/tiff") or (result["logical_file_type"] == "GeoFeatureLogicalFile" and result["content_type"] == "application/x-qgis"):
            layer_id = "L-" + str(result["id"])
            layer_path = "/".join(result["url"].split("/")[4:])
            layer_title = ".".join(result["url"].split("/")[-1].split(".")[:-1])
            layer_ext = result["url"].split("/")[-1].split(".")[-1]
            layer_type = result["content_type"]
            if result["content_type"] == "image/tiff" and layer_ext == "tif":
                db_list["geoserver"].append(
                    {
                        "layer_id": layer_id,
                        "layer_type": "GeographicRaster",
                        "file_type": "geotiff",
                        "hs_path": layer_path,
                        "layer_title": layer_title,
                        "store_type": "coveragestores",
                        "layer_group": "coverages",
                        "verification": "coverage"
                    }
                )
            if result["content_type"] == "application/x-qgis" and layer_ext == "shp":
                db_list["geoserver"].append(
                    {
                        "layer_id": layer_id,
                        "layer_type": "GeographicFeature",
                        "file_type": "shp",
                        "hs_path": layer_path,
                        "layer_title": layer_title,
                        "store_type": "datastores",
                        "layer_group": "featuretypes",
                        "verification": "featureType"
                    }
                )
        if (result["logical_file_type"] == "TimeSeriesLogicalFile" and result["url"].split("/")[-1].split(".")[-1] == "sqlite"):
            db_list["wof"].append(
                {
                    "layer_id": "L-" + str(result["id"]),
                    "hs_path": "/".join(result["url"].split("/")[4:]),
                    "layer_title": ".".join(result["url"].split("/")[-1].split(".")[:-1])
                }
            )

    return db_list


def register_geoserver_databases(workspace_id, db_list):
    geoserver_url = custom_settings.get(name='geoserver_url').value
    geoserver_user = custom_settings.get(name='geoserver_user').value
    geoserver_directory = custom_settings.get(name='geoserver_resource_directory').value
    geoserver_pass = custom_settings.get(name='geoserver_pass').value
    geoserver_auth = requests.auth.HTTPBasicAuth(
        geoserver_user, 
        geoserver_pass
    )
    for layer in db_list:
        rest_url = "/".join((geoserver_url, "workspaces", workspace_id, layer["store_type"], layer["layer_id"], ".".join(("external", layer["file_type"]))))
        dir_path = [geoserver_directory, layer["hs_path"]]
        data = "file://" + os.path.join(*dir_path)
        response = requests.put(rest_url, data=data, auth=geoserver_auth)
        headers = {"content-type": "application/json"}
        rest_url = "/".join((geoserver_url, "workspaces", workspace_id, layer["store_type"], layer["layer_id"], layer["layer_group"], ".".join((layer["layer_title"], "json"))))
        response = requests.get(rest_url, headers=headers, auth=geoserver_auth)

        #print(response.content.decode('utf-8'))

        if json.loads(response.content.decode('utf-8'))[layer["verification"]]["enabled"] is False:
            headers = {"content-type": "application/json"}
            params = {"update": "overwrite", "recurse": True}
            rest_url = "/".join((geoserver_url, "workspaces", workspace_id, layer["store_type"], layer["layer_id"]))
            response = requests.delete(rest_url, params=params, auth=geoserver_auth, headers=headers)
            print(response)

        data = response.content.decode('utf-8').replace('"name":"' + layer["layer_title"] + '"', '"name":"' + layer["layer_id"] + '"')
        response = requests.put(rest_url, headers=headers, auth=geoserver_auth, data=data)
        if response.status_code != 200:
            headers = {"content-type": "application/json"}
            params = {"update": "overwrite", "recurse": True}
            rest_url = "/".join((self.geoserver_url, "workspaces", workspace_id, layer["store_type"], layer["layer_id"]))
            response = requests.delete(rest_url, params=params, auth=geoserver_auth, headers=headers)
            #print(response)
            continue
        
        if layer["layer_type"] == "GeographicRaster":
            try:
                layer_vrt = "https://www.hydroshare.org/resource/" + ".".join(layer["hs_path"].split(".")[:-1]) + ".vrt"
                response = requests.get(layer_vrt)
                vrt = etree.fromstring(response.content.decode('utf-8'))
                layer_max = None
                layer_min = None
                layer_ndv = None
                for element in vrt.iterfind(".//MDI"):
                    if element.get("key") == "STATISTICS_MAXIMUM":
                        layer_max = element.text
                    if element.get("key") == "STATISTICS_MINIMUM":
                        layer_min = element.text
                if layer_max == None or layer_min == None:
                    raise Exception
                try:
                    layer_ndv = vrt.find(".//NoDataValue").text
                except:
                    raise Exception
                if layer_ndv == None:
                    raise Exception
                layer_style = get_layer_style(layer_max, layer_min, layer_ndv, layer["layer_id"])
                rest_url = geoserver_url + "/workspaces/" + workspace_id + "/styles"
                headers = {"content-type": "application/vnd.ogc.sld+xml"}
                response = requests.post(rest_url, data=layer_style, auth=geoserver_auth, headers=headers)

                rest_url = geoserver_url + "/layers/" + layer["layer_id"]
                headers = {"content-type": "application/json"}
                body = '{"layer": {"defaultStyle": {"name": "' + layer["layer_id"] + '", "href":"https:\/\/geoserver.hydroshare.org\/geoserver\/rest\/styles\/' + layer["layer_id"] + '.json"}}}'
                response = requests.put(rest_url, data=body, auth=geoserver_auth, headers=headers)
            except:
                pass


def unregister_geoserver_databases(res_id):
    workspace_id = "HS-" + str(res_id)
    remove_geoserver_workspace(workspace_id)


def register_wof_databases(res_id, db_list):
    wof_user = custom_settings.get(name='wof_user').value
    wof_pass = custom_settings.get(name='wof_pass').value
    wof_auth = requests.auth.HTTPBasicAuth(
        wof_user, 
        wof_pass
    )
    wof_url = custom_settings.get(name='wof_url').value
    wof_directory = custom_settings.get(name='wof_resource_directory').value
    network_id = "HS-" + str(res_id)
    for db in db_list:
        rest_url = wof_url + "/rest/network/" + network_id + "/databases/"
        print(rest_url)
        db_path = wof_directory + db["hs_path"]
        data = {
            "network_id": str(network_id),
            "database_id": str(db["layer_id"]),
            "database_name": str(db["layer_title"]),
            "database_path": str(db_path),
            "database_type": "odm2"
        }
        print(data)
        response = requests.post(rest_url, data=data, auth=wof_auth)
        print(response)
        print(response.content)
        return response


def unregister_wof_databases(res_id):
    wof_user = custom_settings.get(name='wof_user').value
    wof_pass = custom_settings.get(name='wof_pass').value
    wof_auth = requests.auth.HTTPBasicAuth(
        wof_user, 
        wof_pass
    )
    wof_url = custom_settings.get(name='wof_url').value
    network_id = "HS-" + str(res_id)
    rest_url = wof_url + "/rest/network/" + network_id + "/"
    response = requests.delete(rest_url, auth=wof_auth)
    print(response)
    return response


def add_wof_resource(res_id):
    wof_user = custom_settings.get(name='wof_user').value
    wof_pass = custom_settings.get(name='wof_pass').value
    wof_auth = requests.auth.HTTPBasicAuth(
        wof_user, 
        wof_pass
    )
    wof_url = custom_settings.get(name='wof_url').value
    network_id = "HS-" + str(res_id) 
    rest_url = wof_url + "/rest/networks/"
    data = {"network_id": network_id}
    print(data)
    response = requests.post(rest_url, data=data, auth=wof_auth)
    print(response)
    print(response.content)
    return response
