#!/usr/bin/env python
"""
Base class for api.cdek.ru
"""
import json
#import time
import logging
import os.path
#import sys
from datetime import datetime, timedelta

import log_app
import requests
from pdf2image import convert_from_path
from pg_app import PGapp
from psycopg2.extras import Json
from transliterate import translit

# from pdf2image import convert_from_bytes


#import re


#from psycopg2.extras import DictRow


DT_FORMAT = '"%d.%m.%Y %H:%M:%S"'
TS_FORMAT = '%Y%m%d_%H%M%S'

FIRM_LAT = {'АРКОМ': 'ARCOM',
            'КИПСПБ': 'KIPSPB',
            'ЭТК': 'ETK',
            'ТДЭС': 'TDES',
            'ЭТК24': 'ETK24',
            'ОСЗ': 'OSZ',
            'Авт': 'Avt',
            'api': 'API'
           }

dumps_utf8 = lambda x: json.dumps(x, ensure_ascii=False)

def _err_msg(err_list):
    """ Returns string with errors text """
    msg_list = []
    for err in err_list:
        msg_list.append(err['message'])
    ret_msg = '/'.join(msg_list)
    return ret_msg

class CdekAPI():
    """
    Base class for api.cdek.ru
    """
    #url_client_id = '%s/v2/oauth/token' % HOST
    #url_orders = '%s/v2/orders' % HOST
    _url_client_id = '%s/v2/oauth/token'
    _url_orders = '%s/v2/orders'
    _url_calc_tariff = '%s/v2/calculator/tariff'
    _url_webhooks = '%s/v2/webhooks'
    _url_print_barcodes = '%s/v2/print/barcodes'
    url_regions = '%s/v2/location/regions'
    _url_delivery_points = '%s/v2/deliverypoints'
    headers = {'Content-type': 'application/json'}

    #def __init__(self, client_id=None, client_secret=None, api_url=HOST):
    def __init__(self, config):
        logging.getLogger(__name__).addHandler(logging.NullHandler())
        self.access_token = config['CDEK']['token']
        self.token_created = datetime.strptime(config['CDEK']['created'],
                                               DT_FORMAT)

        self.api_url = config['CDEK']['api_url']
        # ??? self.payload = {}
        self.text = ''  # remove&
        self.status_code = 0
        self.err_msg = None

        #client_id = os.environ.get('CDEK_ACC')
        #client_secret = os.environ.get('CDEK_PWD')
        client_id = config['CDEK']['account']
        client_secret = config['CDEK']['password']

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
        else:
            self.status_code = -1
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
        self.status_code = -1
        if self.access_token:
            self.headers['Authorization'] = f'Bearer {self.access_token}'
            #logging.debug("type(payload)=%s, payload=%s", type(self.payload), self.payload)
        logging.debug('headers=%s', self.headers)
        try:
            resp = loc_method(_url % self.api_url,
                              params=payload,  # Ok for GET regions
                              json=payload,
                              headers=self.headers)
            resp.raise_for_status()
            # self.status_code = resp.status_code  # moved to finally:
            logging.debug("resp.url=%s", resp.url)
            self.err_msg = None
            #self.payload.clear()
            #resp.raise_for_status()
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
        #else:
        #    try:
        #        ret = resp.json()
        #    except requests.exceptions.JSONDecodeError:
        #        ret = resp  # ??? .text
        finally:
            self.status_code = resp.status_code
            logging.debug("self.status_code=%s", self.status_code)
            try:
                ret = resp.json()
            except requests.exceptions.JSONDecodeError:
                ret = resp  # ??? .text
            if self.err_msg:
                try:
                    logging.error('err_msg=%s', self.err_msg)
                except requests.exceptions.JSONDecodeError:
                    logging.debug('err_msg is not JSON, resp=%s', resp)
                #ret = {}
                if resp is not None:
                    logging.debug('resp.__dict__=%s', resp.__dict__)
                    logging.debug('resp.text=%s', resp.text)
                    resp_json = json.loads(resp.text)
                    logging.debug('resp_json=%s', resp_json)
                    logging.debug('type(resp_json)=%s', type(resp_json))
                    #ret = {}
                #elif status_code not in (200, 202):  # if not, than HTTPError
                    try:
                        #self.err_msg = self._err_msg(resp.text.get('errors'))
                        self.err_msg = self._err_msg(resp_json.get('errors'))
                    except AttributeError:
                        self.err_msg = resp.text

                logging.error("cdek_req %s failed, self.status_code=%s",
                              method,
                              self.status_code)
                logging.error("cdek_req failed, self.err_msg=%s", self.err_msg)

            if resp is not None:
                self.text = resp.text

        return ret

    #def cdek_create_order(self, **kwargs):
    def cdek_create_order(self, payload):
        """ Create an order
        """
        return self.cdek_req(self._url_orders, payload)

    def cdek_order_uuid(self, uuid):
        """ Order info
        """
        return self.cdek_req(f'{self._url_orders}/{uuid}', None, method='GET')

    def cdek_order_cdek_number(self, cdek_number):
        """ Order info by a cdek_number
        """
        return self.cdek_req(f'{self._url_orders}?cdek_number={cdek_number}', None, method='GET')

    def im_order_im_number(self, im_number):
        """ Order info by a im_number
        """
        return self.cdek_req(f'{self._url_orders}?im_number={im_number}', None, method='GET')

    def print_barcode(self, payload):
        """ Request to create barcode for the order with uuid
        Args:
            payload - должен быть сформирован в вызывающей процедуре,
            т.о. может содержать не один, а список заказов
        """
        return self.cdek_req(self._url_print_barcodes, payload)

    def get_barcode(self, uuid):
        """ Request to get url for downloading barcode by the order's uuid
        """
        return self.cdek_req(f'{self._url_print_barcodes}/{uuid}', None, method='GET')

    def dl_barcode(self, uuid):
        """ Download PDF from the url
        Args:
            uuid - barcode uuid, not the order uuid
        """
        return self.cdek_req(f'{self._url_print_barcodes}/{uuid}.pdf', None, method='GET')

    def calc_tariff(self, payload):
        """ Расчёт стоимости доставки
        """
        return self.cdek_req(self._url_calc_tariff, payload)

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
        return self.cdek_req(self._url_webhooks, '', 'GET')

    def delivery_points(self, payload):
        """ Метод предназначен для получения списка действующих офисов СДЭК
        """
        return self.cdek_req(self._url_delivery_points, payload, 'GET')

##################################################################

UPD_SENT_SQL = 'UPDATE shp.cdek_preorder_params \
SET sts_code=%s, ret_code=%s, cdek_uuid=%s, ret_msg=%s WHERE shp_id = %s \
AND cdek_uuid IS NULL;'

UPD_SQL = 'UPDATE shp.cdek_preorder_params \
SET sts_code=%s, ret_code=%s, cdek_uuid=%s, cdek_number=%s, our_number=%s, ret_msg=%s \
WHERE cdek_uuid = %s;'
#SET sts_code=%s, cdek_number=%s, cdek_uuid=%s, our_number=%s WHERE shp_id = %s;'

ERR_REASON = {}
ERR_REASON['tarfiff_code'] = 'Код тарифа'
ERR_REASON['from_address'] = 'Адрес отправителя'
ERR_REASON['delivery_point'] = 'ПВЗ назначения'
ERR_REASON['to_address'] = 'Адрес назначения'
ERR_REASON['calc_address'] = 'Адрес назначения для расчёта'
ERR_REASON['recipient_name'] = 'Имя получателя'
ERR_REASON['recipient_phone'] = 'Телефон получателя'

def make_msg(params):
    """
    returns error message for user
    """
    return 'Отсутствуют обязательные значения: ' + '/'.join(params)

def verify_required(payload, mode='preorder'):
    """ Проверяет, что обязательные поля заполнены
    payload['tariff_code']
    payload['from_location']['address']
    if payload['tariff_code'] in (136, 138):  # to SKLAD
        payload['delivery_point'] = req_to[0]
    elif payload['tariff_code'] in (137, 139):  # to DVER`
        payload['to_location'] = {"address": req_to[0]}
    payload['recipient']['name']
    payload['recipient']['phones'][0]['number']
    payload['packages']
    """
    err_params = []
    if payload['tariff_code'] is None:
        err_params.append(ERR_REASON['tariff_code'])
    if payload['from_location']['address'] is None:
        err_params.append(ERR_REASON['from_address'])

    if mode == 'calc_tariff':
        if payload['to_location']['address'] is None:
            err_params.append(ERR_REASON['calc_address'])

    if mode == 'preorder':  # для calc_tariff не нужно проверять
        # to SKLAD
        if payload['tariff_code'] in (136, 138) and payload.get('delivery_point') is None:
            err_params.append(ERR_REASON['delivery_point'])
        # to DVER`
        if payload['tariff_code'] in (137, 139) and payload.get('to_location') is None:
            err_params.append(ERR_REASON['to_address'])
        if payload['recipient']['name'] is None:
            err_params.append(ERR_REASON['recipient_name'])
        if len(payload['recipient']['phones']) == 0\
           or payload['recipient']['phones'][0]['number'] is None:
            err_params.append(ERR_REASON['recipient_phone'])

    return err_params

class CDEKApp(PGapp, log_app.LogApp):
    """ An CDEK app
    """
    def __init__(self, args):
        log_app.LogApp.__init__(self, args=args)
        #script_name = os.path.splitext(os.path.basename(__file__))[0]
        #config_filename = f'{script_name}.conf'
        config_filename = args.conf
        self.get_config(config_filename)
        super().__init__(self.config['PG']['pg_host'],
                                      self.config['PG']['pg_user'])
        if self.pg_connect():
            self.set_session(autocommit=True)
            self.api = CdekAPI(self.config)
            if self.api:
                with open(config_filename, 'w', encoding='utf-8') as cfgfile:
                    self.config.write(cfgfile)
            self.total_sum = 0
            self.total_weight = 0
            self.ret_msg = ''
        else:
            logging.error('No connect to PG')
            #raise f"Failed to login to {self.config['PG']['pg_host']}"

    def cdek_regions(self, page=0, size=10):
        """ Метод предназначен для получения детальной информации о регионах
        """
        payload = {}
        if page > 0:
            payload['country_codes'] = 'RU'
            payload['page'] = page
            payload['size'] = size
        return self.api.cdek_req(self.api.url_regions, payload, 'GET')

    def _save_params(self, shp_id, payload, firm):
        """ Save preorder params to PG
        """
        json_payload = Json(payload, dumps=dumps_utf8)
        ret_msg = None
        err_params = verify_required(payload)
        if len(err_params) == 0:
            ret_msg = None
        else:
            ret_msg = make_msg(err_params)
        logging.debug('ret_msg=%s', ret_msg)

        # add ON CONFLICT
        params_ins = self.curs.mogrify(
                'INSERT INTO shp.cdek_preorder_params(shp_id, ret_msg, payload, our_firm)\
VALUES (%s, %s, %s, %s)', (shp_id, ret_msg, json_payload, firm))
        # ???UIDX on shp_id, ON CONFLICT DO NOTHING???
        logging.debug('params_ins=%s', params_ins)
        if not self.do_query(params_ins):
            ret_msg = f'FAILED INSERT INTO shp.cdek_preorder_params, shp_id={shp_id}'
            logging.error(ret_msg)

        return ret_msg

    def _parse_answer(self, shp_id, res):
        """ Parse API answer
            and write errors message into DB
        """
        self.ret_msg = None
        sts_code = 0
        uuid = None
        # parse answer for state
        for req in res['requests']:
            if req['type'] == 'CREATE' and req['state'] != 'ACCEPTED':
                sts_code = 90
                logging.warning('CREATE request is not ACCEPTED')
                msg_list = []
                err_list = req.get('errors')
                for err in err_list:
                    msg_list.append(err['message'])
                self.ret_msg = '/'.join(msg_list)
            if req['type'] == 'CREATE' and req['state'] == 'ACCEPTED':
                sts_code = 10
                logging.debug('ACCEPTED')
                uuid = res['entity']['uuid']

        # update shp.cdek_preorder_params if got status
        if sts_code != 0:
            upd_sent_sql = self.curs.mogrify(UPD_SENT_SQL, (sts_code, self.api.status_code,
                                            uuid, self.ret_msg, shp_id))
            logging.debug('upd_sent_sql=%s', upd_sent_sql)
            if not self.do_query(upd_sent_sql):
                logging.error('FAILED upd_sent_sql=%s', upd_sent_sql)

    def _comment(self, shp_id):
        """ Bills list to comment
        """
        bills_select = self.curs_dict.mogrify(
                'SELECT bill::varchar FROM shp.ship_bills WHERE shp_id = %s',
                (shp_id,)
                )
        logging.debug('bills_select=%s', bills_select)
        if self.run_query(bills_select, dict_mode=True) == 0:
            req_bills = self.curs_dict.fetchall()
            logging.debug('req_bills=%s', req_bills)
            ret_comment = ', '.join([','.join(bill) for bill in req_bills])
        else:
            ret_comment = f'отправка {shp_id}'
        return ret_comment

    def _from(self, shp_id, tariff_code):
        """ Returns 'from' field for preorder
        """
        ret_from = None
        self.curs_dict.callproc('shp.cdek_from', [shp_id])
        req_from = self.curs_dict.fetchone()
        if tariff_code in (136, 137):  # from SKLAD
            # -- ret_from = {'code': 137} # Санкт-Петербург
            #payload['shipment_point'] = 'SPB9' # req_from[0]
            ret_from = {
                    'city': "Санкт-Петербург",
                    'address': req_from[0]}
            #        'address': "Мурино, Ясная 11"}
        elif tariff_code in (138, 139):  # from DVER`
            ret_from = {"address": req_from[0]}
        return ret_from

    def _sender(self, shp_id):
        # sender
        self.curs_dict.callproc('shp.cdek_sender', [shp_id])
        req_sender = self.curs_dict.fetchone()
        ret_sender = {
                'company': req_sender['company'],
                'name': req_sender['name'],
                'email': req_sender['email'],
                'phones': {}
                }
        # sender phones
        self.curs_dict.callproc('shp.cdek_sender_phones', [shp_id])
        req_phones = self.curs_dict.fetchall()
        #ret_sender['phones'] = []
        phones = []
        for rec in req_phones:
            d_rec = dict(rec)
            phones.append(d_rec)
            #ret_sender['phones'].append(d_rec)
        ret_sender['phones'] = phones

        return ret_sender

    def _recipient(self, shp_id):
        # recipient
        self.curs_dict.callproc('shp.cdek_recipient', [shp_id])
        req_recipient = self.curs_dict.fetchone()
        ret_recipient = {
                'company': req_recipient['company'],
                'name': req_recipient['name'],
                'email': req_recipient['email'],
                'passport_series': req_recipient['passport_series'],
                'passport_number': req_recipient['passport_number'],
                # right format of date "passport_date_of_issue": "2019-03-12",
                # but currently format is wrong.
                # Commented because is not mandatory attribute
                ### 'passport_date_of_issue': req_recipient['passport_date_of_issue'],
                'passport_organization': req_recipient['passport_organization'],
                'inn': req_recipient['inn'],
                'phones': {}
                }
        # recipient phones
        self.curs_dict.callproc('shp.cdek_recipient_phones', [shp_id])
        req_phones = self.curs_dict.fetchall()
        phones = []
        for rec in req_phones:
            d_rec = dict(rec)
            phones.append(d_rec)
        ret_recipient['phones'] = phones
        logging.debug('ret_recipient=%s', ret_recipient)
        return ret_recipient


    def cdek_shp(self, shp_id, firm):
        """ Создаёт заказ для отправки с shp_id
        """
        payload = {}
        payload['type'] = 1  # интернет-магазин (ИМ)
        #payload['number'] = f'{shp_id}_{FIRM_LAT[firm]}'  # Номер заказа в ИС Клиента
        # Номер заказа в ИС Клиента
        payload['number'] = f'{shp_id}_{translit(firm, "ru", reversed=True)}'
        payload['comment'] = self._comment(shp_id)

        # tarif
        self.curs_dict.callproc('shp.cdek_route', [shp_id])
        tariff = self.curs_dict.fetchone()
        payload['tariff_code'] = tariff[0]

        # from
        payload['from_location'] = self._from(shp_id, payload['tariff_code'])

        # sender
        payload['sender'] = self._sender(shp_id)

        # to
        self.curs_dict.callproc('shp.cdek_to', [shp_id])
        req_to = self.curs_dict.fetchone()
        if payload['tariff_code'] in (136, 138):  # to SKLAD
            payload['delivery_point'] = req_to[0]
        elif payload['tariff_code'] in (137, 139):  # to DVER`
            payload['to_location'] = {"address": req_to[0]}

        # recipient
        payload['recipient'] = self._recipient(shp_id)

        payload['packages'] = self._packages(shp_id)
        payload['delivery_recipient_cost'] = self._delivery_cost(shp_id)

        ret_msg = None
        if payload['delivery_recipient_cost'] is None: # Оплата Мы
            loc_res = self._cre_order(shp_id, payload, firm)
        else:
            ret_msg = payload['delivery_recipient_cost'].get('ret_msg')
            if ret_msg is None:
                loc_res = self._cre_order(shp_id, payload, firm)
                ####### loc_res["ret_msg"]
            else:
                loc_res = {'ret_msg': ret_msg}

        if "ret_msg" in loc_res:
            ret_msg = loc_res["ret_msg"]
        #else:
        #    ret_msg = None
        self.ret_msg = ret_msg
        return loc_res

    def _cre_order(self, shp_id, payload, firm):
        """ Save params and call API to create an order
        """

        logging.debug('payload=%s', json.dumps(payload, ensure_ascii=False, indent=4))
        # INSERT INTO shp.cdek_preorder_params
        ret_msg = self._save_params(shp_id, payload, firm)
        logging.debug('ret_msg=%s', ret_msg)
        if ret_msg is None:
            # UPDATE будет в триггере на cdek_order_status только для CREATED
            loc_res = self.api.cdek_create_order(payload)
            #logging.debug('type(loc_res)=%s', type(loc_res))
            #logging.debug('loc_res=%s', loc_res)
            if "requests" in loc_res.keys():
                logging.debug('key "requests" found in the answer')
                self._parse_answer(shp_id, loc_res)
            elif "errors" in loc_res.keys():
                logging.debug('ERRORS: loc_res=%s', loc_res)
            else:
                logging.debug('ELSE keys found in the answer=%s', loc_res.keys())
        else:
            loc_res = {'ret_msg': ret_msg}
            self.ret_msg = ret_msg
        return loc_res

    def calc_tariff(self, shp_id):
        """ Метод используется для расчета стоимости и сроков доставки по коду тарифа
        """
        payload = {}
        payload['type'] = 1
        # tarif
        self.curs_dict.callproc('shp.cdek_route', [shp_id])
        tariff = self.curs_dict.fetchone()
        payload['tariff_code'] = tariff[0]
        # DEBUG payload['tariff_code'] = 136
        # from
        self.curs_dict.callproc('shp.cdek_from', [shp_id])
        req_from = self.curs_dict.fetchone()
        payload['from_location'] = {'code': 137, # Санкт-Петербург
                "address": req_from[0]}
        # to
        self.curs_dict.callproc('shp.cdek_to', [shp_id])
        req_to = self.curs_dict.fetchone()
        if payload['tariff_code'] in (136, 138):  # до Склада
            #self.curs_dict.callproc('shp.cdek_pvz_addr', [req_to[0]])
            self.curs_dict.callproc('shp.cdek_pvz_calc_addr', [req_to[0]])
            req_pvz = self.curs_dict.fetchone()
            if req_pvz[0] is not None and req_pvz[0] != 'не определен':
                payload['to_location'] = {"address": req_pvz[0],
                        "postal_code": req_pvz[0].split(',')[0]}
            else:
                payload['to_location'] = {"address": None}
        else:
            payload['to_location'] = {"address": req_to[0]}

        # packages
        payload['packages'] = self._packages(shp_id, 'calc')

        loc_serv = [{'code': 'INSURANCE', 'parameter': str(self.total_sum)}]
        payload['services'] = loc_serv
        logging.debug('payload=%s', json.dumps(payload, ensure_ascii=False,
                                               sort_keys=True,
                                               indent=4))

        err_params = verify_required(payload, 'calc_tariff')
        if len(err_params) == 0:
            ret_msg = None
        else:
            ret_msg = make_msg(err_params)
        if ret_msg is None:
            loc_res = self.api.calc_tariff(payload)
            try:
                logging.info(loc_res["delivery_sum"])
            except KeyError:
                loc_res = {'ret_msg': self.api.err_msg}
        else:
            loc_res = {'ret_msg': ret_msg}

        return loc_res

    def _delivery_cost(self, shp_id):
        """ Returns values for payload['delivery_recipient_cost']
        """
        res = None
        wepay_select = self.curs.mogrify(
                'SELECT wepay FROM shp.ship_bills WHERE shp_id = %s',
                (shp_id,)
                )
        logging.debug('wepay_select=%s', wepay_select)
        if self.do_query(wepay_select, reconnect=True):
            req_wepay = self.curs.fetchone()
            logging.debug('req_wepay=%s', req_wepay)
            if not req_wepay[0]:  # ОтгрузкаОплата не Мы
                logging.debug('ОтгрузкаОплата = Они, рассчитываем стоимость')
                loc_cost = self.calc_tariff(shp_id)
                logging.debug('loc_cost=%s', loc_cost)
                ret_msg = loc_cost.get('ret_msg')
                if ret_msg is None:
                    res = {
                        'value': loc_cost.get("total_sum"),
                        #'vat_sum': 0,  !!!T0DO
                        #'vat_rate': None
                    }
                else:
                    res = {'ret_msg': ret_msg}
        else:
            logging.warning('req_wepay NOT FOUND for shp_id=%s', shp_id)
        return res

    def test_packages(self, shp_id, mode='order'):
        """ non protected
        """
        return self._packages(shp_id, mode)

    def _packages(self, shp_id, mode='order'):
        """ Returens list of packages
        """
        # boxes = packages
        self.curs_dict.callproc('shp.cdek_packages', [shp_id])
        req_packages = self.curs_dict.fetchall()
        logging.debug('len(req_packages)=%s', len(req_packages))
        logging.debug('req_packages=%s', req_packages)
        boxes = len(req_packages)

        loc_packages = []
        self.total_sum = 0
        self.total_weight = 0

        # get full list of items
        self.curs_dict.callproc('shp.cdek_package_items', [shp_id])
        req_items = self.curs_dict.fetchall()
        for item in req_items:
            self.total_sum += item['cost']*item['amount']
            if item['ware_key'] is None:
                item['ware_key'] = -1
            if item['weight'] is None:
                item['weight'] = 200
            # WRONG! Must be a weight of boxes
            # self.total_weight += item['weight']*item['amount']

        for idx, rec in enumerate(req_packages):
            #self.total_weight += rec['weight']
            d_rec = dict(rec)
            logging.debug('type(rec)=%s, d_rec=%s', type(rec), d_rec)
            d_rec.update({'items': []})

            if boxes > 1:  # для неск коробок виртуальные приборы
                self.curs_dict.callproc('shp.cdek_package_items_virt', [shp_id,
                    idx+1, boxes, self.total_sum, rec['weight']])
                req_items = self.curs_dict.fetchall()
                logging.debug('boxes > 1: req_items=%s', req_items)

            if mode == 'order':
                for item in req_items:
                    d_item = dict(item)
                    logging.debug('d_item=%s', d_item)
                    # in cdek_package_items()
                    # d_item['name'] = d_item['name'].replace('"','\"')
                    d_item['weight'] = rec['weight']
                    d_item['cost'] = float(d_item['cost'])
                    d_item['payment'] = {"value": 0}
                    d_rec['items'].append(d_item)
            elif mode == 'calc':
                d_rec.pop('items')
                d_rec.pop('number')
            loc_packages.append(d_rec)

        logging.debug('Calculated self.total_sum=%s, self.total_weight=%s',
                self.total_sum, self.total_weight)

        return loc_packages

    def uuid_barcode(self, uuid, prn_format = 'A7'):
        """ Метод используется для формирования ШК места в формате pdf к заказу
        /заказам (TOD0)
        """
        payload = {}
        loc_order = {'order_uuid': uuid}
        loc_orders_list = []
        loc_orders_list.append(loc_order)
        logging.debug('loc_orders_list=%s', loc_orders_list)
        #payload = {"orders": [loc_order], "format": prn_format}
        #payload = {"orders": loc_orders_list, "format": prn_format}
        payload["orders"] = loc_orders_list
        payload["format"] = prn_format
        logging.debug('payload=%s', json.dumps(payload, ensure_ascii=False, indent=4))
        return self.api.print_barcode(payload)

    def cdek_num_barcode(self, cdek_num, prn_format = 'A7'):
        """ Метод используется для формирования ШК места в формате pdf к заказу
        /заказам (TOD0)
        """
        payload = {}
        loc_order = {'cdek_number': cdek_num}
        loc_orders_list = []
        loc_orders_list.append(loc_order)
        logging.debug('loc_orders_list=%s', loc_orders_list)
        #payload = {"orders": [loc_order], "format": prn_format}
        #payload = {"orders": loc_orders_list, "format": prn_format}
        payload["orders"] = loc_orders_list
        payload["format"] = prn_format
        logging.debug('payload=%s', json.dumps(payload, ensure_ascii=False, indent=4))
        return self.api.print_barcode(payload)

    def request_barcode(self, uuid):
        """ Запрашивает формирование ШК
        и записывает полученный uuid ШК в PG cdek_preorder_params
        Далее скачать можно по получении webhook в таблице cdek_print_form
        """
        #??? resp = self.api.get_barcode(uuid)
        resp = self.uuid_barcode(uuid)
        barcode_upd = self.curs.mogrify('UPDATE cdek_preorder_params SET barcode_uuid = %s \
WHERE cdek_uuid = %s', (resp['entity']['uuid'], uuid))
        logging.debug('barcode_upd=%s', barcode_upd)
        if self.do_query(barcode_upd, reconnect=True):
            #pass
            self.conn.commit()
            logging.debug('commited! barcode_upd=%s', barcode_upd)
        else:
            logging.error('Error with update cdek_preorder_params.barcode_uuid')
        return resp


    def download_barcode(self, uuid, filename=None):
        """ Метод используется для формирования ШК места в формате pdf к заказу
        /заказам (TOD0)
        Args:
            uuid - barcode uuid
        """
        #loc_res = True
        #resp = self.api.get_barcode(uuid)
        #time.sleep(3)
        resp = self.api.dl_barcode(uuid)
        if filename is None:
            filename = f'{uuid}.pdf'
        with open(filename, "wb") as barcode_output:
            try:
                barcode_output.write(resp.content)
            except AttributeError:
                #logging.error('resp=%s', resp)
                #logging.error('err=%s', self.api.err_msg)
                self.ret_msg = self.api.err_msg
            else:
                jpg_file, _ = os.path.splitext(filename)
                # jpg_path, _ = os.path.split(filename)
                logging.debug('filename=%s, jpg_file=%s', filename, jpg_file)
        pages = convert_from_path(filename, dpi=300, size=(874, 1240))
        logging.debug('pages=%s', pages)
        if len(pages) == 0:
            self.ret_msg = 'convert from pdf failed, pages[] is empty'
            logging.error(self.ret_msg)
        else:
            for count, page in enumerate(pages):
                ind = count + 1
                page.save(f'{jpg_file}_{ind}.jpg', dpi=(300, 300))

        #return loc_res
        return resp

    def delivery_points(self, city_code):
        """ Метод предназначен для получения списка действующих офисов СДЭК
        """
        payload = {'city_code': city_code}
        return self.api.delivery_points(payload)

    def order_info(self, uuid):
        """ Get order info via API
            parse and write info into shp.cdek_preorder_params
        """
        info = self.api.cdek_order_uuid(uuid)
        sts_code = 0
        cdek_number = None
        our_number = None
        self.ret_msg = None
        for req in info['requests']:
            logging.debug('req=%s', req)
            if req['type'] == 'CREATE' and req['state'] == 'SUCCESSFUL':
                sts_code = 20
                cdek_number = info["entity"]["cdek_number"]
                our_number = info["entity"]["number"]
            if req['type'] == 'CREATE' and req['state'] == 'INVALID':
                sts_code = 91
                msg_list = []
                err_list = req.get('errors')
                for err in err_list:
                    msg_list.append(err['message'])
                self.ret_msg = '/'.join(msg_list)

        if sts_code != 0:
            # update shp.cdek_preorder_params
            upd_sql = self.curs.mogrify(UPD_SQL, (sts_code, self.api.status_code,
                                                uuid,
                                                cdek_number,
                                                our_number,
                                                self.ret_msg,
                                                uuid)
                                                )
            logging.debug('upd_sql=%s', upd_sql)
            if not self.do_query(upd_sql):
                logging.error('FAILED upd_sql=%s', upd_sql)
        return info

if __name__ == '__main__':
    log_app.PARSER.add_argument('--uuid', type=str, help='an order uuid to check status')
    log_app.PARSER.add_argument('--uuid_barcode', type=str, help=\
'an order uuid to print a barcode')
    log_app.PARSER.add_argument('--req_barcode', type=str, help=\
'an order uuid to request a barcode')
    log_app.PARSER.add_argument('--cdek_num_barcode', type=int, help=\
'an order cdek_number to print a barcode')
    log_app.PARSER.add_argument('--get_barcode', type=str, help=\
'get url of the barcode by the uuid')
    log_app.PARSER.add_argument('--dl_barcode', type=str, help=\
"download PDF with barcode by its uuid (not order uuid)")
    log_app.PARSER.add_argument('--cdek_number', type=str, help=\
'an order cdek_number to check status')
    log_app.PARSER.add_argument('--im_number', type=str, help='an order im_number to check status')
    log_app.PARSER.add_argument('--demoshp', type=str, help='a shp_id to create an order')

    log_app.PARSER.add_argument('--shp', type=int, help='a shp_id to create an order')
    log_app.PARSER.add_argument('--firm', type=str, help='our firm-sender')

    log_app.PARSER.add_argument('--calc', type=int, help='a shp_id to calculate a shipment cost')
    log_app.PARSER.add_argument('--hooks', type=int, help='webhooks list')
    log_app.PARSER.add_argument('--wh_type', type=str, help='a webhook type to register')
    log_app.PARSER.add_argument('--city_code', type=str,
            help='List of delivery points in city_code')
    log_app.PARSER.add_argument('--pck', type=int)
    ARGS = log_app.PARSER.parse_args()
    CDEK = CDEKApp(args=ARGS)
    if CDEK:
        logging.debug('CDEK.text=%s', CDEK.api.text)

        # an order info
        if ARGS.uuid:
            #CDEK_RES = CDEK.api.cdek_order_uuid(ARGS.uuid)
            CDEK_RES = CDEK.order_info(ARGS.uuid)
        if ARGS.cdek_number:
            CDEK_RES = CDEK.api.cdek_order_cdek_number(ARGS.cdek_number)
        if ARGS.im_number:
            CDEK_RES = CDEK.api.im_order_im_number(ARGS.im_number)

        #if ARGS.demoshp:
        #    DEMO_PAYLOAD['number'] = ARGS.demoshp
        #    CDEK_RES = CDEK.api.cdek_create_order(payload=DEMO_PAYLOAD)

        if ARGS.shp:
            CDEK_RES = CDEK.cdek_shp(ARGS.shp, ARGS.firm)
            try:
                print(CDEK_RES['entity']['uuid'])
            except KeyError:
                print('Обращения к СДЭК API не было')

        if ARGS.calc:
            CDEK_RES = CDEK.calc_tariff(ARGS.calc)
            """
            order_payload['delivery_recipient_cost'] = {
                value: CDEK_RES["delivery_sum"],
                vat_sum:
                vat_rate:
            }
            """

        if ARGS.hooks:
            CDEK_RES = CDEK.api.cdek_webhook_list()

        if ARGS.req_barcode:
            CDEK_RES = CDEK.request_barcode(ARGS.req_barcode)

        if ARGS.uuid_barcode:
            CDEK_RES = CDEK.uuid_barcode(ARGS.uuid_barcode, prn_format='A4')

        if ARGS.cdek_num_barcode:
            CDEK_RES = CDEK.cdek_num_barcode(ARGS.cdek_num_barcode)

        if ARGS.get_barcode:
            CDEK_RES = CDEK.api.get_barcode(ARGS.get_barcode)

        if ARGS.dl_barcode:
            CDEK_RES = CDEK.download_barcode(ARGS.dl_barcode)

        if ARGS.wh_type:
            CDEK_RES = CDEK.api.cdek_webhook_reg('http://dru.kipspb.ru:8123', ARGS.wh_type)
            #CDEK_RES = CDEK.api.cdek_webhook_reg('http://ttk-az.kipspb.ru:8123', ARGS.wh_type)

        if ARGS.city_code:
            CDEK_RES = CDEK.delivery_points(ARGS.city_code)

        if ARGS.pck:
            CDEK_RES = CDEK.test_packages(ARGS.pck, 'calc')

        logging.debug('CDEK_RES=%s', json.dumps(CDEK_RES, ensure_ascii=False, indent=4))
