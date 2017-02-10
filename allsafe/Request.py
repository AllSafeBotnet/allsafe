"""
This is the script that will handle the request to the endpoint 
and that will use the JSON configuration file given.

Created:     13 November 2016 
Modified:    30 December 2016
"""

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
        self._method        = config_dict['method']
        self._url           = config_dict['url']
        self._resources     = config_dict['resources']
        self._header        = {
                                "user-agent" : config_dict['user-agent']
                              } 
        self._encoding       = config_dict['encoding']
        self._payload        = config_dict['payload']
        self._response       = config_dict['response']
        self._responseheader = config_dict['response-header']
        self._proxies        = config_dict['proxy_server']



    def perform(self):
        """
        This method will perform the actual request based on 
        the paramaters initliazed by the json configuration file
        """

        # a new session is created
        s = requests.Session()

        #TODO maybe it could be written in a better way
        # check for any proxy
        proxies = dict()
        for protocol in self._proxies:
            if (protocol == 'http' or protocol == 'https') and (len(self._proxies[protocol]) != 0):
                proxies[protocol] = self._proxies[protocol]
        # updating proxies after validation
        self._proxies = proxies

        # polishing url
        if '://' not in self._url:
            self._url = 'http://' + self._url
        if self._url[len(self._url)-1] == '/':
            self._url = self._url[:len(self._url)-1]

        # updating the session if necessary
        if self._proxies:
            s.proxies.update(self._proxies)
        # iterating over resources to perform sequential requests
        # toward different resources from a unique session
        for resource in self._resources:
            if resource[0] != '/':
                resource = '/' + resource

            # creation of the request container
            req = requests.Request()
            
            # parameters setting
            req.method = self._method
            req.url = self._url + resource
            req.data = self._payload  #TODO write because data and params use payload
            req.params = self._payload
            req.headers = self._header

            # request performs
            r = s.send(req.prepare(),timeout=0.5)

            # based on the preferences the response will be given
            #if (self._response == "json"):
            #    try:
            #        return r.json()
            #    except ValueError:
            #        raise Exception("Error in JSON encoding / decoding preparing the request")
            #
            #if (self._response == "raw"):
            #    return r.raw
            #return r.text
