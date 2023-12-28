#!/usr/bin/env python3
""" Запрос статуса предзаказа СДЭК по uuid
"""

import logging
import sys
import json
import cdek_api

def main():
    """
    Just main proc
    """
    #cdek_api.log_app.PARSER.add_argument('--conf', type=str, required=True, help='conf file')
    #??? cdek_api.log_app.PARSER.set_required('--conf', type=str, required=True, help='conf file')
    cdek_api.log_app.PARSER.add_argument('--uuid', type=str, required=True,
            help='an order uuid to check status')
    args = cdek_api.log_app.PARSER.parse_args()
    cdek = cdek_api.CDEKApp(args=args)
    cdek_res = cdek.order_info(args.uuid)
    logging.debug('cdek_res=%s', json.dumps(cdek_res, ensure_ascii=False, indent=4))
    if cdek.ret_msg is not None:
        logging.error(cdek.ret_msg)
        print(cdek.ret_msg, file=sys.stderr, end='', flush=True)
    """ check 'state' in a list of requests
    else:
        reqs = cdek_res.get('requests')
        if reqs is not None:
            for req in reqs:
                ... CHECK
                print(uuid, file=sys.stdout, end='', flush=True)
                print('No key "uuid" in CDEK entity', file=sys.stderr, end='', flush=True)
        else:
            print('No key "requests" in CDEK answer', file=sys.stderr, end='', flush=True)
    """

if __name__ == '__main__':
    main()
