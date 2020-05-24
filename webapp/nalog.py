import requests

from webapp.config import nalog_user, nalog_password, nalog_url


def get_voucher(fn, fd, fp):
    headers = {"Device-Id": 'python', "Device-OS": 'windows'}
    s = requests.Session()
    url = nalog_url.format(fn=fn, fd=fd, fp=fp)
    answer = s.get(url, headers=headers, auth=(nalog_user, nalog_password),)
    return answer.json()
