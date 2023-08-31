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
        return os.path.exists("/var/lib/linuxmuster-cachingserver/actions.json")
    
    @get(r'/api/lmn/cachingserver/getserver')
    #@authorize('lmn_cachingserver:show')
    @endpoint(api=True)
    def handle_api_lmn_cachingserver_getserver(self, http_context):
        with open("/var/lib/linuxmuster-cachingserver/servers.json") as f:
            original = json.load(f)
            result = {}
            for key in sorted(original.keys()):
                result[key] = original[key]
            return result
        
    @get(r'/api/lmn/cachingserver/getserverfilehashed')
    #@authorize('lmn_cachingserver:show')
    @endpoint(api=True)
    def handle_api_lmn_cachingserver_getserverfilehashed(self, http_context):
        with open("/var/lib/linuxmuster-cachingserver/cached_filehashes.json") as f:
            return json.load(f)
    
    @get(r'/api/lmn/cachingserver/getimages')
    #@authorize('lmn_cachingserver:show')
    @endpoint(api=True)
    def handle_api_lmn_cachingserver_getimages(self, http_context):
        result = []
        for path in glob("/srv/linbo/images/*/*.qcow2", recursive = True):
            result.append({"path": path, "filename": os.path.basename(path)})
        return {"status": True, "data": result}
        
    @post(r'/api/lmn/cachingserver/server-status')
    #@authorize('lmn_cachingserver:show')
    @endpoint(api=True)
    def handle_api_lmn_cachingserver_server_status(self, http_context):
        server = http_context.json_body()['server']
        try:
            request = requests.get("http://" + server + ":8000/status")
            return request.json()
        except Exception:
            return {"status": False, "data": ""}
        
    @post(r'/api/lmn/cachingserver/file-status')
    #@authorize('lmn_cachingserver:show')
    @endpoint(api=True)
    def handle_api_lmn_cachingserver_file_status(self, http_context):
        server = http_context.json_body()['server']
        try:
            request = requests.get("http://" + server + ":8000/files/hashes/get")
            hashes_on_cachingserver =  request.json()
        except Exception:
            return {"status": False, "data": ""}
        try:
            with open("/var/lib/linuxmuster-cachingserver/cached_filehashes.json") as f:
                hashes_on_server = json.load(f)
        except Exception:
            return {"status": False, "data": ""}
        
        result = {}
        summary = {} # action: True = latest, False = old
        for filename in hashes_on_server:
            result[filename] = hashes_on_server[filename]
            if result[filename]["action"] not in summary:
                summary[result[filename]["action"]] = True
            if filename in hashes_on_cachingserver:
                result[filename]["hash_on_cache"] = hashes_on_cachingserver[filename]["hash"]
                result[filename]["exist"] = True
                if hashes_on_server[filename]["hash"] == hashes_on_cachingserver[filename]["hash"]:
                    result[filename]["latest"] = True
                else:
                    result[filename]["latest"] = False
                    summary[result[filename]["action"]] = True
            else:
                result[filename]["hash_on_cache"] = "-"
                result[filename]["exist"] = False
                result[filename]["latest"] = False
                summary[result[filename]["action"]] = True

        return {"status": True, "data": {"summary": summary, "result": result}}
        
    
    @post(r'/api/lmn/cachingserver/syncserver')
    #@authorize('lmn_cachingserver:show')
    @endpoint(api=True)
    def handle_api_lmn_cachingserver_syncserver(self, http_context):
        servername = http_context.json_body()['servername']
        syncitem = http_context.json_body()['syncitem']
        command = ['sudo', '/usr/bin/linuxmuster-cachingserver', '--json', 'sync', '-n', servername, '-i', syncitem]
        output = subprocess.check_output(command, shell=False)
        return json.loads(output.decode())