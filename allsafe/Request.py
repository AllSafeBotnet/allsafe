"""
This is the script that will handle the request to the endpoint 
and that will use the JSON configuration file given.

Created:     13 November 2016 
Modified:    13 November 2016
"""
import requests
import json
import os

class Request():
    """
    The Request class will contain all the basic information useful to perform
    the HTTP request

    @param: config_path, filename = path to file containing the configuration
    """
    def __init__(self, config_path):

        # performing file opening and reading
        script_dir = os.path.dirname(__file__) 
        abs_file_path = os.path.join(script_dir, config_path)
        file = open(abs_file_path,'r')
        config = file.read()
        file.close()
        
        # the read json will be loaded in order to be accessed in an easy way
        config_json = json.loads(config)

        # parameters initialization         
        self._method = config_json['method']
        self._url = config_json['url']
        self._header = {
            "user-agent" : config_json['user-agent']
        } 
        self._credentials = config_json['auth-credentials']
        self._encoding = config_json['encoding']
        self._payload = config_json['payload']
        self._timeout = config_json['timeout']
        self._response = config_json['response']
        self._responseheader = config_json['response-header']



    def perform(self):
        """
        This method will perform the actual request based on 
        the paramaters initliazed by the json configuration file
        """

        # creation of the request container
        req = requests.Request()

        # parameters setting
        req.method = self._method
        req.url = self._url
        req.data = self._payload
        req.params = self._payload
        req.headers = self._header

        # a new session is created
        s = requests.Session()
        # Credential for authentication need to be in the right format 
        if (self._credentials != "{}"):
            s.auth = (self._credentials["username"] , self._credentials["password"])

        # request performs
        r = s.send(req.prepare())

        # based on the preferences the response will be given
        if (self._response == "json"):
            try:
                return r.json()
            except ValueError:
                print("Error in json") #TODO to improve
        
        if (self._response == "raw"):
            return r.raw()
        return r.text