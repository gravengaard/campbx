#import urllib2
import requests
#import base64
#import simplejson as json
import logging
from functools import partial
from decimal import Decimal
import unittest

class EndPointPartial(partial):
    def __new__(cls, func, conf, _repr):
        cls._repr = _repr
        return super(EndPointPartial, cls).__new__(cls, func, conf)

    def __repr__(self):
        return unicode('<API endpoint %s>' % self._repr)


class CampBX(object):
    """Camp BX API Class"""
    username = None
    password = None
    api_url = 'https://campbx.com/api/'
    log = None

    # API endpoints
    # { python_call : (url_php_call, requires_auth) }
    endpoints = {
        'xdepth': ('xdepth', False),
        'xticker': ('xticker', False),
        'my_funds': ('myfunds', True),
        'my_orders': ('myorders', True),
        'my_margins': ('mymargins', True),
        'get_btc_address': ('getbtcaddr', True),
        'send_instant': ('sendinstant', True),
        'send_btc': ('sendbtc', True),
        'trade_cancel': ('tradecancel', True),
        'trade_enter': ('tradeenter', True),
        'trade_advanced': ('tradeadv', True),
    }

    def __init__(self, username=None, password=None, log_level=logging.INFO):
        self.username = username
        self.password = password
        
        self.session = requests.Session()
        self.session.headers['User-agent'] = 'Mozilla/5.0'

        # setup logging
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(log_level)

        # append all the enpoints to the class dictionary
        self._create_endpoints()

    def debug_mode(self, toggle):
        """
        Toggle debug mode for more detailed output
          obj.debug_mode(True) - Turn debug mode on
          obj.debug_mode(False) - Turn debug mode off
        """
        if toggle:
            self.log.setLevel(logging.DEBUG)
        else:
            self.log.setLevel(logging.ERROR)

    def _make_request(self, conf, post_params={}):
        """Make a request to the API and return data in a pythonic object"""
        endpoint, requires_auth = conf

        # setup the url and the request objects
        url = '%s%s.php' % (self.api_url, endpoint)
        self.log.debug('Setting url to %s' % url)
        #request = urllib2.Request(url)

        # tack on authentication if needed
        self.log.debug('Post params: %s' % post_params)
        if requires_auth:
            post_params.update({
                'user': self.username,
                'pass': self.password
            })

        try:
            self.log.debug('Requesting data from %s' % url)
            response = self.session.post(url, data=post_params)
            return response.json(parse_float=Decimal)
        except:
            self.log.exception("Error making request")
            return None

    def _create_endpoints(self):
        """Create all api endpoints using self.endpoint and partial from functools"""
        for k, v in self.endpoints.items():
            _repr = '%s.%s' % (self.__class__.__name__, k)
            self.__dict__[k] = EndPointPartial(self._make_request, v, _repr)

class Test_CampBX(unittest.TestCase):
    cbx = CampBX('test', 'fake')
    
    def test_xdepth(self):
        xdepth = self.cbx.xdepth()
        
        self.assertIn('Bids', xdepth)
        self.assertIn('Asks', xdepth)
        self.assertIsInstance(xdepth['Bids'], list)
        self.assertIsInstance(xdepth['Asks'], list)
    
    def test_xticker(self):
        xticker = self.cbx.xticker()
        
        self.assertIn('Last Trade', xticker)
        self.assertIn('Best Ask', xticker)
        self.assertIn('Best Bid', xticker)


if __name__=='__main__':
    unittest.main()