"""
This is the script that will handle the request to the endpoint 
and that will use the JSON configuration file given.

Created:     13 November 2016 
Modified:    27 December 2016
"""
import requests

class Request(Thread):
    """
    The Request class will contain all the basic information useful to perform
    the HTTP request

    @param: config_dict, dictionary - dictionary with the correct configuration for request
    """
    def __init__(self, config_json):
        
        # calling superclass init method
        Thread._init__(self)

        # parameters initialization         
        self._method = config_dict['method']
        self._url = config_json['url']
        self._header = {
            "user-agent" : config_json['user-agent']
        } 
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

        # request performs
        r = s.send(req.prepare())

        # based on the preferences the response will be given
        if (self._response == "json"):
            try:
                return r.json()
            except ValueError:
                raise Exception("Error in JSON encoding / decoding preparing the request")
        
        if (self._response == "raw"):
            return r.raw()
        return r.text

    def run(self)
        """
        This method will perform the actual request, launching thread active behaviour
        """
        self.perform()