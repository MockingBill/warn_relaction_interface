import requests
import re
import uuid, hashlib
import pandas as pd
import os
import logging

logger = logging.getLogger('log')


class download_unit:
    def __init__(self):
        self._result = False
        self.work_id = None
        self.length=None

    def get_result(self):
        return self._result
    def get_len(self):
        return self.length

    def download_file(self, url, file_pname, work_id, chunk_size=1024 * 4):
        try:
            self.work_id = work_id
            # 第二种
            with requests.get(url, stream=True) as req:
                if req.status_code == 200:
                    with open(file_pname, 'wb') as f:
                        for chunk in req.iter_content(chunk_size=chunk_size):
                            if chunk:
                                f.write(chunk)
                    self.is_good_file(file_pname)
                else:
                    self._result = False
        except Exception as e:
            logger.error("[" + self.work_id + "] "+str(e))
            self._result = False

    def is_good_file(self, url):
        suffix = str(url).split('.')[-1]
        try:
            if suffix == 'csv':
                d = pd.read_csv(url, encoding='utf-8')
                d.columns = ['TIME_OF_ALARM', 'MAJOR', 'MANUFACTURER', 'NETWORK_ELEMENT_NAME', 'TITLE']
                sh=d.shape
                if d.shape[1] == 5:
                    self.length=d.shape[0]
                    pd.to_datetime(pd.to_datetime(d['TIME_OF_ALARM']), unit='ms')
                    logger.info("[" + self.work_id + "]:shape"+str(sh)+"csv列数量正确")
                    self._result = True
                else:
                    logger.error("[" + self.work_id + "]:shape"+str(sh)+"csv列数量错误")
                    os.remove(url)
                    self._result = False
            elif suffix == 'xlsx' or suffix == 'xls':
                d = pd.read_excel(url)
                d.columns=['TIME_OF_ALARM', 'MAJOR', 'MANUFACTURER', 'NETWORK_ELEMENT_NAME', 'TITLE']
                sh=d.shape
                if d.shape[1] == 5:
                    self.length = d.shape[0]
                    pd.to_datetime(pd.to_datetime(d['TIME_OF_ALARM']), unit='ms')
                    logger.info("[" + self.work_id + "]:shape"+str(sh)+"excel列数量正确")
                    self._result = True
                else:
                    logger.error("[" + self.work_id + "]:shape"+str(sh)+"excel列数量错误")
                    os.remove(url)
                    self._result = False
        except Exception as e:
            logger.error("[" + self.work_id + "]:判断CSV异常:" + str(e))
            os.remove(url)
            self._result = False


def isURL(url):
    strUrl = r"^((https|http|ftp|rtsp|mms)?://)" \
             "?(([0-9a-z_!~*'().&=+$%-]+: )?[0-9a-z_!~*'().&=+$%-]+@)?" \
             "(([0-9]{1,3}\.){3}[0-9]{1,3}" \
             "|" \
             "([0-9a-z_!~*'()-]+\.)*" \
             "([0-9a-z][0-9a-z-]{0,61})?[0-9a-z]\." \
             "[a-z]{2,6})" \
             "(:[0-9]{1,4})?" \
             "((/?)|" \
             "(/[0-9a-z_!~*'().;?:@&=+$,%#-]+)+/?)$"
    m = re.match(strUrl, url)
    if m and m.group() == url:
        return True
    else:
        return False


def get_unique_str():
    uuid_str = str(uuid.uuid4())
    md5 = hashlib.md5()
    md5.update(uuid_str.encode('utf-8'))
    return md5.hexdigest()
