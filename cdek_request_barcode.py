#!/usr/bin/env python3
""" Запрос ШК для заказа СДЭК по uuid
"""

import logging
import sys
import json
import cdek_api

def main():
    """
    Just main proc
    """
    cdek_api.log_app.PARSER.add_argument('--uuid', type=str, required=True,
            help='an order uuid to request form barcode PDF')
    args = cdek_api.log_app.PARSER.parse_args()
    cdek = cdek_api.CDEKApp(args=args)
    cdek_res = cdek.request_barcode(args.uuid)
    logging.debug('cdek_res=%s', json.dumps(cdek_res, ensure_ascii=False, indent=4))
    if cdek.ret_msg is not None and cdek.ret_msg != '':
        logging.error(cdek.ret_msg)
        print(cdek.ret_msg, file=sys.stderr, end='', flush=True)
    else:
        logging.debug('getting entity')
        ent = cdek_res.get('entity')
        logging.debug('got entity=%s', json.dumps(ent, ensure_ascii=False, indent=4))
        if ent is not None:
            uuid = ent.get('uuid')
            if uuid is None:
                print('No key "uuid" in CDEK entity', file=sys.stderr, end='', flush=True)
        else:
            print('No key "entity" in CDEK answer', file=sys.stderr, end='', flush=True)

if __name__ == '__main__':
    main()
