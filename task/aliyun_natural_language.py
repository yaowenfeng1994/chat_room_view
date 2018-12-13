#! -*- coding:utf-8 -*-

import json
import uuid
import hmac
import base64
import hashlib
import requests
from datetime import datetime

GMT_FORMAT = '%a, %d %b %Y %H:%M:%S GMT'


class AliyunNaturalLanguage(object):
    def __init__(self):
        self.method = "POST"
        self.accept = "application/json"
        self.content_type = "application/json;chrset=utf-8"
        self.path = "/nlp/api/wordsegment/general"
        self.date = datetime.utcnow().strftime(GMT_FORMAT)
        self.host = "nlp.cn-shanghai.aliyuncs.com"

    @staticmethod
    def md5_base64(string: str):
        if string.__len__() == 0:
            return ""
        m = hashlib.md5()
        m.update(string.encode())
        md5str = m.digest()
        encode_str = base64.b64encode(md5str)
        return encode_str.decode()

    @staticmethod
    def hmac_sha1(string: str, key: str):
        h = hmac.new(key.encode(), string.encode(), "sha1").hexdigest()
        encode_str = base64.b64encode(h.encode("utf-8"))
        return encode_str.decode()

    def send_post(self, post_body, access_key_id, access_key_secret):
        # 对body做MD5 + BASE64加密
        body_md5 = self.md5_base64(json.dumps(post_body))

        uuid_str = str(uuid.uuid1())
        string_to_sign = (self.method + "\n" + self.accept + "\n" + body_md5 + "\n" + self.content_type + "\n" +
                          self.date + "\n" + "x-acs-signature-method:HMAC-SHA1\n" + "x-acs-signature-nonce:" +
                          uuid_str + "\n" + self.path)
        # 计算HMAC - SHA1
        signature = self.hmac_sha1(string_to_sign, access_key_secret)

        print(111, signature)
        auth_header = "acs " + access_key_id + ":" + signature
        # print(auth_header)
        headers = {"Accept-Type": self.accept, "Content-Type": self.content_type, "Content-MD5": body_md5,
                   "Date": self.date, "Host": self.host, "Authorization": auth_header,
                   "x-acs-signature-nonce": uuid_str,
                   "x-acs-signature-method": "HMAC-SHA1"}
        print(headers)
        # def aliyun_natural_language(self):
        # data = '{"postBody": {"text": "白色的沙发", "lang": "ZH"}}'
        response = requests.post(url="http://nlp.cn-shanghai.aliyuncs.com/nlp/api/wordsegment/general", headers=headers,
                                 data=json.dumps(post_body))

        print(response)
        print(response.content.decode())


if __name__ == '__main__':
    # aliyun_natural_language()
    s = "91e800d1-2675-4645-b777-ccdaafec40ca"  # str object
    a = AliyunNaturalLanguage()
    data = {"text": "yaowenfeng", "lang": "ZH"}
    accessKey = "LTAIDIinsEwJhX7u"
    accessSecret = "k3YdCJcUztozDZr1q7I3hEyNCx1LZB"
    a.send_post(data, accessKey, accessSecret)
