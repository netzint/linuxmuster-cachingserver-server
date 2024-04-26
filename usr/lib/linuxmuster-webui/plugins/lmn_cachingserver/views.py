from jadi import component

from aj.api.http import get, post, HttpPlugin
from aj.auth import authorize
from aj.api.endpoint import endpoint, EndpointError

import os.path
import json
import subprocess
import requests

from glob import glob

@component(HttpPlugin)
class Handler(HttpPlugin):
    def __init__(self, context):
        self.context = context

    @get(r'/api/lmn/cachingserver/isinstalled')
    #@authorize('lmn_cachingserver:show')
    @endpoint(api=True)
    def handle_api_lmn_cachingserver_isinstalled(self, http_context):
        return os.path.exists("/var/lib/linuxmuster-cachingserver/servers.json")
    
    @get(r'/api/lmn/cachingserver/getserver')
    #@authorize('lmn_cachingserver:show')
    @endpoint(api=True)
    def handle_api_lmn_cachingserver_getserver(self, http_context):
        with open("/var/lib/linuxmuster-cachingserver/servers.json") as f:
            original = json.load(f)
            result = {}
            for key in sorted(original.keys()):
                result[key] = original[key]
            result2 = []
            for res in result:
                result2.append(result[res])
            return result2
    
    @get(r'/api/lmn/cachingserver/getimages')
    #@authorize('lmn_cachingserver:show')
    @endpoint(api=True)
    def handle_api_lmn_cachingserver_getimages(self, http_context):
        result = []
        for path in glob("/srv/linbo/images/*/*.qcow2", recursive = True):
            result.append({"path": path, "filename": os.path.basename(path), "imagename": os.path.basename(path).replace(".qcow2", "")})
        return {"status": True, "data": result}
    
    @post(r'/api/lmn/cachingserver/addimagetoserver')
    #@authorize('lmn_cachingserver:show')
    @endpoint(api=True)
    def handle_api_lmn_cachingserver_add_Image_to_server(self, http_context):
        server = http_context.json_body()['server']
        imagename = http_context.json_body()['imagename']
        with open("/var/lib/linuxmuster-cachingserver/servers.json", "r") as f:
            serverfile = json.load(f)
        if imagename in serverfile[server]["images"]:
            return {"status": True, "data": "Image already selected!"}
        else:
            serverfile[server]["images"].append(imagename)
            with open("/var/lib/linuxmuster-cachingserver/servers.json", "w") as f:
                json.dump(serverfile, f, indent=4)

    @post(r'/api/lmn/cachingserver/removeimagefromserver')
    #@authorize('lmn_cachingserver:show')
    @endpoint(api=True)
    def handle_api_lmn_cachingserver_remove_Image_from_server(self, http_context):
        server = http_context.json_body()['server']
        imagename = http_context.json_body()['imagename']
        with open("/var/lib/linuxmuster-cachingserver/servers.json", "r") as f:
            serverfile = json.load(f)
        if imagename not in serverfile[server]["images"]:
            return {"status": True, "data": "Image was already removed!"}
        else:
            serverfile[server]["images"].remove(imagename)
            with open("/var/lib/linuxmuster-cachingserver/servers.json", "w") as f:
                json.dump(serverfile, f, indent=4)
        
    @post(r'/api/lmn/cachingserver/server-status')
    #@authorize('lmn_cachingserver:show')
    @endpoint(api=True)
    def handle_api_lmn_cachingserver_server_status(self, http_context):
        server = http_context.json_body()['server']
        try:
            request = requests.get("http://" + server + ":4457/v1/status")
            return request.json()
        except Exception:
            return {"status": False, "data": ""}
        
    @post(r'/api/lmn/cachingserver/configuration-status')
    #@authorize('lmn_cachingserver:show')
    @endpoint(api=True)
    def handle_api_lmn_cachingserver_configuration_status(self, http_context):
        server = http_context.json_body()['server']
        try:
            request = requests.get("http://" + server + ":4457/v1/configuration/check")
            return {"status": True, "data": request.json()} 
        except Exception:
            return {"status": False, "data": ""}
        
    
    @post(r'/api/lmn/cachingserver/configuration-sync')
    #@authorize('lmn_cachingserver:show')
    @endpoint(api=True)
    def handle_api_lmn_cachingserver_configuration_sync(self, http_context):
        server = http_context.json_body()['server']
        try:
            request = requests.get("http://" + server + ":4457/v1/configuration/sync")
            return {"status": True, "data": request.json()} 
        except Exception:
            return {"status": False, "data": ""}
        
    @post(r'/api/lmn/cachingserver/images-status')
    #@authorize('lmn_cachingserver:show')
    @endpoint(api=True)
    def handle_api_lmn_cachingserver_images_status(self, http_context):
        server = http_context.json_body()['server']
        try:
            request = requests.get("http://" + server + ":4457/v1/images/check")
            return {"status": True, "data": request.json()} 
        except Exception:
            return {"status": False, "data": ""}
        
    
    @post(r'/api/lmn/cachingserver/images-sync')
    #@authorize('lmn_cachingserver:show')
    @endpoint(api=True)
    def handle_api_lmn_cachingserver_images_sync(self, http_context):
        server = http_context.json_body()['server']
        try:
            request = requests.get("http://" + server + ":4457/v1/images/sync")
            return {"status": True, "data": request.json()} 
        except Exception:
            return {"status": False, "data": ""}
        
    @post(r'/api/lmn/cachingserver/logs')
    #@authorize('lmn_cachingserver:show')
    @endpoint(api=True)
    def handle_api_lmn_cachingserver_logs(self, http_context):
        server = http_context.json_body()['server']
        try:
            request = requests.get("http://" + server + ":4457/v1/logs")
            return {"status": True, "data": request.json()} 
        except Exception:
            return {"status": False, "data": ""}