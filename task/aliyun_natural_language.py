#! -*- coding:utf-8 -*-
import json
import uuid
import hmac
import base64
import hashlib
import requests
from datetime import datetime
from urllib.parse import urlparse

GMT_FORMAT = '%a, %d %b %Y %H:%M:%S GMT'


class AliyunNaturalLanguage(object):
    def __init__(self, url: str):
        self.method = "POST"
        self.accept = "application/json"
        self.content_type = "application/json;chrset=utf-8"
        self.date = datetime.utcnow().strftime(GMT_FORMAT)
        self.url = url
        self.path = urlparse(url).path

        self.host = url.replace(self.path, "").replace("http://", "")

    @staticmethod
    def md5_base64(string: str):
        if string.__len__() == 0:
            return ""
        m = hashlib.md5()
        m.update(string.encode("utf-8"))
        md5str = m.digest()
        encode_str = base64.b64encode(md5str)
        return encode_str.decode()

    @staticmethod
    def hmac_sha1(string: str, key: str):
        h = hmac.new(key.encode(encoding="utf-8"), string.encode(encoding="utf-8"), hashlib.sha1).digest()
        return base64.b64encode(h).decode("utf-8")

    def send_post(self, post_body, access_key_id, access_key_secret):
        # 对body做MD5 + BASE64加密
        body_md5 = self.md5_base64(json.dumps(post_body))
        uuid_str = str(uuid.uuid1())
        string_to_sign = (self.method + "\n" + self.accept + "\n" + body_md5 + "\n" + self.content_type + "\n" +
                          self.date + "\n" + "x-acs-signature-method:HMAC-SHA1\n" + "x-acs-signature-nonce:" +
                          uuid_str + "\n" + self.path)
        # 计算HMAC - SHA1
        signature = self.hmac_sha1(string_to_sign, access_key_secret)
        auth_header = "acs " + access_key_id + ":" + signature
        headers = {"Accept": self.accept, "Content-Type": self.content_type, "Content-MD5": body_md5,
                   "Date": self.date, "Host": self.host, "Authorization": auth_header,
                   "x-acs-signature-nonce": uuid_str,
                   "x-acs-signature-method": "HMAC-SHA1"}

        response = requests.post(url=self.url,
                                 headers=headers,
                                 data=json.dumps(post_body))
        return json.loads(response.content.decode())


if __name__ == "__main__":
    data1 = {"text": "白色炫酷吊炸天来自北欧的沙发上有只狗", "lang": "ZH"}
    data2 = {"text": "白色炫酷吊炸天来自北欧的沙发上有只狗"}
    service_url1 = "http://nlp.cn-shanghai.aliyuncs.com/nlp/api/wordsegment/general"
    service_url2 = "http://nlp.cn-shanghai.aliyuncs.com/nlp/api/wordpos/general"
    access_key = ""
    access_secret = ""
    obj = AliyunNaturalLanguage(url=service_url1)
    result = obj.send_post(post_body=data1, access_key_id=access_key, access_key_secret=access_secret)
    print(result)
    print(len(result["data"]))
