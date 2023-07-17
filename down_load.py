import base64
import json
import logging
import os
import requests
import shutil
import subprocess
import time
from Crypto.Cipher import AES
from datetime import datetime
from selenium.webdriver import DesiredCapabilities
from selenium.webdriver import Edge
from selenium.webdriver import EdgeOptions
from selenium.webdriver.common.by import By

# 启动浏览器：& 'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe' --remote-debugging-port=9222 --user-data-dir=D:\tmp

handler = logging.StreamHandler()
handler.setLevel(logging.INFO)
handler.setFormatter(logging.Formatter('%(asctime)s %(message)s'))
logger = logging.getLogger('down_load')
logger.setLevel(logging.INFO)
logger.addHandler(handler)

def init(port):
    options = EdgeOptions()
    options.add_experimental_option('debuggerAddress', '127.0.0.1:{}'.format(port))
    options.add_experimental_option('perfLoggingPrefs', {'enableNetwork': True})
    caps = DesiredCapabilities.EDGE
    caps['ms:loggingPrefs'] = {'performance': 'ALL'}
    browser = Edge(options=options, capabilities=caps)
    return browser

def down_load(browser, url, dir):
    if not os.path.exists(f'{dir}\\ts'):
        os.makedirs(f'{dir}\\ts')
    
    browser.get(url)
    time.sleep(10)
    url_template = ''
    key_url = 'not a url'
    performance_log = browser.get_log('performance')
    for log in performance_log:
        message = json.loads(log['message'])['message']
        method = message['method']
        if method == 'Network.requestWillBeSent' and (not url_template):
            url = message['params']['request']['url']
            if url.find('/drm/') > 0 and url.find('.ts?start') > 0:
                url_template = url
        elif method == 'Network.responseReceived':
            url = message['params']['response']['url']
            if url.find('.m3u8') > 0:
                request_id = message['params']['requestId']
                try:
                    body = browser.execute_cdp_cmd('Network.getResponseBody', {'requestId': request_id})
                    content = base64.b64decode(body['body'])
                    with open(f'{dir}\\a.m3u8', 'wb') as m3u8:
                        m3u8.write(content)
                    with open(f'{dir}\\a.m3u8', 'r') as m3u8:
                        for line in m3u8.readlines():
                            line = line.strip()
                            if line[0] == '#':
                                if line.find('URI') > 0:
                                    key_url = line[line.find('="') + 2: line.find('",')]
                except:
                    pass
            if url.find(key_url) != -1:
                request_id = message['params']['requestId']
                url = message['params']['response']['url']
                _uid = url[url.find('uid') + 4:]
                rsp = requests.get(url=url).content

                if len(rsp) == 16:
                    userid_bytes = bytes(_uid.encode(encoding='utf-8'))
                    result_list = []
                    for index in range(0, len(rsp)):
                        result_list.append(rsp[index] ^ userid_bytes[index])
                    logger.info(result_list)
                    key = bytes(result_list)
                else:
                    logger.error(f"获取异常，请求返回值：{body['body']}")

    if not key:
        return False
    logger.info('开始下载')
    base_url = url_template[url_template.find('https'): url_template.find('/drm/') + 5]
    param = url_template[url_template.find('&sign='):]
    index = 0
    exists_files = os.listdir(f'{dir}\\ts')
    exists_index = len(exists_files)
    with open(f'{dir}\\a.m3u8', 'r') as m3u8:
        with open(f'{dir}\\concat.txt', 'a') as concat:
            lines = m3u8.readlines()
            for i in range(len(lines)):
                if i % 500 < 1:
                    logger.info("下载进度：%.2f%%" % (i * 100 / len(lines)))
                line = lines[i]
                line = line.strip()
                if line[0] == '#':
                    continue
                if line.__len__ == 0:
                    continue
                index += 1
                if index < exists_index -10 :
                    continue
                url = f'{base_url}{line}{param}'
                headers = {
                    "Authority": "btt-vod.xiaoeknow.com",
                    "Accept": "*/*",
                    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
                    "Connection": "keep-alive",
                    "Origin": "https://xiaoe.kaikeba.com",
                    "Referer": "https://xiaoe.kaikeba.com/",
                    "sec-ch-ua": "\"Microsoft Edge\";v=\"113\", \"Chromium\";v=\"113\", \"Not-A.Brand\";v=\"24\"",
                    "sec-ch-ua-mobile": "?0",
                    "sec-ch-ua-platform": "\"Windows\"",
                    "Sec-Fetch-Dest": "empty",
                    "Sec-Fetch-Mode": "cors",
                    "Sec-Fetch-Site": "cross-site",
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36 Edg/113.0.1774.50"
                }
                res = requests.get(url, headers=headers)
                data = res.content
                aes = AES.new(key, AES.MODE_CBC)
                with open(f"{dir}\\ts\\%0.8d.ts" % index, 'wb') as f:
                    f.write(aes.decrypt(data))
                    f.flush()
                    if index > exists_index:
                        concat.write("file 'ts\%0.8d.ts'\n" % index)
    concat_cmd = f'ffmpeg -f concat -safe 0 -i "{dir}\\concat.txt" -c copy "{dir}.{datetime.timestamp(datetime.now())}.mp4"'
    logger.info(f'concat_cmd: {concat_cmd}')
    process = subprocess.run(concat_cmd)
    result = process.returncode == 0

    shutil.rmtree(dir)
    return result
