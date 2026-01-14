#!/usr/bin/env python
""" Загрузка PDF со ШК для заказа СДЭК по uuid-ШК
"""

import logging
import sys
# import json
import cdek_api

def main():
    """
    Just main proc
    """
    cdek_api.log_app.PARSER.add_argument('--uuid', type=str, required=True,
            help='a barcode uuid to download')
    cdek_api.log_app.PARSER.add_argument('--outpdf', type=str, required=True,
            help='a barcode uuid to download')
    args = cdek_api.log_app.PARSER.parse_args()
    cdek = cdek_api.CDEKApp(args=args)
    cdek.download_barcode(args.uuid, args.outpdf)
    # cdek_res = cdek.download_barcode(args.uuid, args.outpdf)
    # try:
    #     logging.debug('cdek_res=%s', json.dumps(cdek_res, ensure_ascii=False, indent=4))
    # except TypeError:
    #     logging.debug('cdek_res=%s', cdek_res.__dict__)

    if cdek.ret_msg is not None and cdek.ret_msg != '':
        logging.error('cdek.ret_msg=%s', cdek.ret_msg)
        print(cdek.ret_msg, file=sys.stderr, end='', flush=True)

if __name__ == '__main__':
    main()
