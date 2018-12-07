#!/usr/bin/env python
# -*- coding:utf-8 -*-

import json
import logging
from libs.error_message import err


logger = logging.getLogger("corgi_log")
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())


def response_json(err_code,
                  err_msg=None,
                  err_msg_en=None,
                  data=None):
    """
    method for standard response json
    """

    try:
        if err_code in err:
            err_msg_list = err[err_code]
        else:
            raise KeyError

        response = {
            "err_code": err_code,
            "err_msg": err_msg_list[0] if err_msg is None else err_msg,
            "err_msg_en": err_msg_list[1] if err_msg_en is None else err_msg_en,
            "data": dict()
        }
        if data is not None:
            response.update({"data": data})
        response_data = json.dumps(response)

    except (TypeError, AttributeError):
        logger.exception("response 内容格式非法")
    except KeyError:
        logger.exception("不存在的 err_code")
    else:
        return response_data
