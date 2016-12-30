"""
This is the script that will handle the request to the endpoint 
and that will use the JSON configuration file given.

Created:     13 November 2016 
Modified:    30 December 2016
"""

from threading import Thread
import requests

class Request():
    """
    The Request class will contain all the basic information useful to perform
    the HTTP request

    @param: config_dict, dictionary - dictionary with the correct configuration for request
    """
    def __init__(self, config_dict):
        
        # calling superclass init method

        # parameters initialization         
        self._method = config_dict['method']
        self._url = config_dict['url']
        self._header = {
            "user-agent" : config_dict['user-agent']
        } 
        self._encoding = config_dict['encoding']
        self._payload = config_dict['payload']
        self._response = config_dict['response']
        self._responseheader = config_dict['response-header']



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

        # request performs
        r = s.send(req.prepare())

        # based on the preferences the response will be given
        if (self._response == "json"):
            try:
                return r.json()
            except ValueError:
                raise Exception("Error in JSON encoding / decoding preparing the request")
        
        if (self._response == "raw"):
            return r.raw
        return r.text
