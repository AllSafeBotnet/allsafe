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
        self.__method = config_json['method']
        self.__url = config_json['url']
        self.__header = {
            "user-agent" : config_json['user-agent']
        } 
        self.__credentials = config_json['auth-credentials']
        self.__encoding = config_json['encoding']
        self.__payload = config_json['payload']
        self.__timeout = config_json['timeout']
        self.__response = config_json['response']
        self.__responseheader = config_json['response-header']



    def perform(self):
        """
        This method will perform the actual request based on 
        the paramaters initliazed by the json configuration file
        """

        # creation of the request container
        req = requests.Request()

        # parameters setting
        req.method = self.__method
        req.url = self.__url
        req.data = self.__payload
        req.params = self.__payload
        req.headers = self.__header

        # a new session is created
        s = requests.Session()
        # Credential for authentication need to be in the right format 
        if (self.__credentials != "{}"):
            s.auth = (self.__credentials["username"] , self.__credentials["password"])

        # request performs
        r = s.send(req.prepare())

        # based on the preferences the response will be given
        if (self.__response == "json"):
            try:
                return r.json()
            except ValueError:
                print("Error in json") #TODO to improve
        
        if (self.__response == "raw"):
            return r.raw()
        return r.text