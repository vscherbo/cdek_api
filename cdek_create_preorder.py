#!/usr/bin/env python3
""" Создание предзаказа СДЭК для shp_id
"""

import logging
import sys
import json
import cdek_api

def main():
    """
    Just main proc
    """
    cdek_api.log_app.PARSER.add_argument('--firm', type=str, required=True,
            help='our firm-sender')
    cdek_api.log_app.PARSER.add_argument('--shp', type=int, required=True,
            help='a shp_id to create an order')
    args = cdek_api.log_app.PARSER.parse_args()
    cdek = cdek_api.CDEKApp(args=args)
    cdek_res = cdek.cdek_shp(args.shp, args.firm)
    logging.debug('cdek_res=%s', json.dumps(cdek_res, ensure_ascii=False, indent=4))
    if cdek.ret_msg is not None:
        logging.error(cdek.ret_msg)
        print(cdek.ret_msg, file=sys.stderr, end='', flush=True)
    else:
        ent = cdek_res.get('entity')
        if ent is not None:
            uuid = ent.get('uuid')
            if uuid is not None:
                print(uuid, file=sys.stdout, end='', flush=True)
            else:
                print('No key "uuid" in CDEK entity', file=sys.stderr, end='', flush=True)
        else:
            print('No key "entity" in CDEK answer', file=sys.stderr, end='', flush=True)

if __name__ == '__main__':
    main()
