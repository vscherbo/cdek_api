#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Base class for api.cdek.ru
"""
import os
import sys
from datetime import datetime
from datetime import timedelta
import logging
import json
#import re

import requests

from pg_app import PGapp
import log_app

DT_FORMAT = '"%d.%m.%Y %H:%M:%S"'
TS_FORMAT = '%Y%m%d_%H%M%S'

#HOST = "https://api.cdek.ru"

class CdekAPI():
    """
    Base class for api.cdek.ru
    """
    #url_client_id = '%s/v2/oauth/token' % HOST
    #url_orders = '%s/v2/orders' % HOST
    _url_client_id = '%s/v2/oauth/token'
    _url_orders = '%s/v2/orders'
    _url_webhooks = '%s/v2/webhooks'
    url_regions = '%s/v2/location/regions'
    headers = {'Content-type': 'application/json'}

    #def __init__(self, client_id=None, client_secret=None, api_url=HOST):
    def __init__(self, config):
        logging.getLogger(__name__).addHandler(logging.NullHandler())
        self.access_token = config['CDEK']['token']
        self.token_created = datetime.strptime(config['CDEK']['created'],
                                               DT_FORMAT)

        self.api_url = config['CDEK']['api_url']
        #self.payload = {}
        self.text = ''
        #self.status_code = 200
        self.err_msg = None

        client_id = os.environ.get('CDEK_ACC')
        client_secret = os.environ.get('CDEK_PWD')

        if self.need_login():
            #if client_id and client_secret:
            assert isinstance(client_id, str)
            assert isinstance(client_secret, str)
            if self.auth(client_id, client_secret):
                config['CDEK']['token'] = self.access_token
                config['CDEK']['created'] = datetime.now().strftime(DT_FORMAT)
        else:
            logging.info('Do NOT need login. Using saved access_token.')
            self.headers['Token'] = self.access_token

    def auth(self, client_id, client_secret):
        """ Authentication
        """

        payload = {'grant_type': 'client_credentials',
                   'client_id': client_id,
                   'client_secret': client_secret}
        logging.debug('payload=%s', payload)
        #self.headers = {'Content-type': 'x-www-form-urlencoded'}
        resp = requests.post(self._url_client_id % self.api_url,
                             params=payload,
                             headers={"Content-type": "x-www-form-urlencoded"})
        ret = resp.json()
        loc_res = False
        if resp is not None:
            self.text = resp.text
        if ret and 'access_token' in ret.keys():
            self.access_token = ret['access_token']
            logging.debug('auth ret=%s', ret)
            self.headers = {'Content-type': 'application/json'}
            loc_res = True
        #else:
        #    self.status_code = -1
        return loc_res

    def need_login(self):
        """ Returns True if toeken is expired """
        loc_res = False
        if not self.access_token:
            loc_res = True
            logging.info('Access_token is empty. Need login')
        elif (datetime.now() - self.token_created) > \
            timedelta(minutes=59, seconds=59):
            loc_res = True
            logging.info('Access_token expired. Need login')
        return loc_res

    @staticmethod
    def __exception_fmt__(tag, exception):
        return f'{tag} msg={str(exception)}'
        #return 'f{tag} msg=f{str(exception).encode("utf-8")}'

    def cdek_req(self, _url, payload, method='POST'):
        """ DO an request to api.cdek.ru
            Args:
                _url - URL on api.cdek.ru
                method - 'GET' or default 'POST'
        """
        # pylint: disable=too-many-branches
        if method == 'GET':
            loc_method = requests.get
        elif method == 'POST':
            loc_method = requests.post
        else:
            raise f'Wrong value {method} for an argument "method"'

        ret = {}
        resp = None
        status_code = -1
        if self.access_token:
            self.headers['Authorization'] = f'Bearer {self.access_token}'
            #logging.debug("type(payload)=%s, payload=%s", type(self.payload), self.payload)
        logging.debug('headers=%s', self.headers)
        try:
            resp = loc_method(_url % self.api_url,
                              params=payload,
                              headers=self.headers)
            status_code = resp.status_code
            logging.debug("resp.url=%s", resp.url)
            self.err_msg = None
            logging.debug("status_code=%s", resp.status_code)
            #self.payload.clear()
            resp.raise_for_status()
        except requests.exceptions.Timeout as exc:
            # Maybe set up for a retry, or continue in a retry loop
            self.err_msg = self.__exception_fmt__('Timeout', exc)
        except requests.exceptions.TooManyRedirects as exc:
            # Tell the user their URL was bad and try a different one
            self.err_msg = self.__exception_fmt__('TooManyRedirects', exc)
        except requests.exceptions.HTTPError as exc:
            self.err_msg = self.__exception_fmt__('HTTPError', exc)
        except requests.exceptions.RequestException as exc:
            # catastrophic error. bail.
            self.err_msg = self.__exception_fmt__('RequestException', exc)
        else:
            ret = resp.json()
            # logging.debug("r.text=%s", r.text)
        finally:
            if self.err_msg:
                logging.error(self.err_msg)
                ret = {}
                if resp is not None:
                    logging.debug(resp.json())
                    ret = resp.json()

                ret["answer"] = {'state': 'exception', 'err_msg': self.err_msg}
            elif status_code not in (200, 202):
                logging.error("cdek_req %s failed, status_code=%s",
                              method,
                              status_code)

            if resp is not None:
                self.text = resp.text

        return ret

    def cdek_create_order(self, **kwargs):
        """ Create an order
        """
        payload = {"docIds": kwargs}
        return self.cdek_req(self._url_orders, payload)

    def cdek_order(self, uuid):
        """ Order info
        """
        #return self.cdek_get('{}/{}'.format(self._url_orders, uuid))
        return self.cdek_req(f'{self._url_orders}/{uuid}', 'GET')

    def cdek_webhook_reg(self, arg_url, arg_type):
        """ Webhook subscription
        """
        payload = {}
        payload['url'] = arg_url
        payload['type'] = arg_type
        return self.cdek_req(self._url_webhooks, payload)

    def cdek_webhook_list(self):
        """ Webhook subscription info
        """
        return self.cdek_req(self._url_webhooks, 'GET')


class CDEKApp(PGapp, log_app.LogApp):
    """ An CDEK app
    """
    def __init__(self, args):
        log_app.LogApp.__init__(self, args=args)
        script_name = os.path.splitext(os.path.basename(__file__))[0]
        config_filename = f'{script_name}.conf'
        self.get_config(config_filename)
        super().__init__(self.config['PG']['pg_host'],
                                      self.config['PG']['pg_user'])
        if self.pg_connect():
            self.set_session(autocommit=True)
        self.api = CdekAPI(self.config)
        if self.api:
            with open(config_filename, 'w', encoding='utf-8') as cfgfile:
                self.config.write(cfgfile)

    def cdek_regions(self, page=0, size=10):
        """ Метод предназначен для получения детальной информации о регионах
        """
        payload = {}
        if page > 0:
            payload['country_codes'] = 'ES'
            payload['page'] = page
            payload['size'] = size

        return self.api.cdek_req(self.api.url_regions, payload, 'GET')

if __name__ == '__main__':
    LOG_FORMAT = '[%(filename)-21s:%(lineno)4s - %(funcName)20s()] \
            %(levelname)-7s | %(asctime)-15s | %(message)s'
    logging.basicConfig(stream=sys.stdout, format=LOG_FORMAT, level=logging.DEBUG)
    logging.info('Start')
    ARGS = log_app.PARSER.parse_args()
    CDEK = CDEKApp(args=ARGS)
    if CDEK:
        logging.debug('CDEK.text=%s', CDEK.api.text)
        #CDEK_RES = CDEK.cdek_webhook_reg('http://dru.kipspb.ru:8123', 'ORDER_STATUS')
        # Webhooks info
        #CDEK_RES = CDEK.api.cdek_webhook_list()

        # an order info
        # CDEK_RES = CDEK.cdek_order('72753034-6edc-41d1-8abf-ab03d80fb89b')

        # regions
        CDEK_RES = CDEK.cdek_regions(page=2, size=3)

        logging.debug('CDEK_RES=%s', json.dumps(CDEK_RES, ensure_ascii=False, indent=4))


        #logging.debug('CDEK.text=%s', CDEK.text)
