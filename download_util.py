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
logger = logging.getLogger('download_util')
logger.setLevel(logging.INFO)
logger.addHandler(handler)

class DownloadUtil:
    def __init__(self, port: int = 9222) -> None:
        options = EdgeOptions()
        options.add_experimental_option('debuggerAddress', '127.0.0.1:{}'.format(port))
        options.add_experimental_option('perfLoggingPrefs', {'enableNetwork': True})
        caps = DesiredCapabilities.EDGE
        caps['ms:loggingPrefs'] = {'performance': 'ALL'}
        self.browser = Edge(options=options, capabilities=caps)


    def open(self, url):
        self.browser.get(url)

    def close(self):
        self.browser.close()

    def close_others(self):
        # 关闭其他页面，只保留一个页面操作，避免混乱
        main_handle = self.browser.current_window_handle
        for handle in self.browser.window_handles:
            if handle != main_handle:
                self.browser.switch_to.window(handle)
                self.browser.close()
        self.browser.switch_to.window(main_handle)

    def get_m3u8_content(self):
        content = ''
        try:
            performance_log = self.browser.get_log('performance')
            for log in performance_log:
                message = json.loads(log['message'])['message']
                method = message['method']
                if method == 'Network.responseReceived':
                    url = message['params']['response']['url']
                    if url.find('.m3u8') > 0:
                        request_id = message['params']['requestId']
                        body = self.browser.execute_cdp_cmd('Network.getResponseBody', {'requestId': request_id})
                        content = base64.b64decode(body['body'])
                        break
        except:
            logger.info(111)
            pass
            
        return content
                        