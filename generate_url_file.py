import time
import sys
from selenium.webdriver.common.by import By

from down_load import *


def close_others(browser):
    # 关闭其他页面，只保留一个页面操作，避免混乱
    main_handle = browser.current_window_handle
    for handle in browser.window_handles:
        if handle != main_handle:
            browser.switch_to.window(handle)
            browser.close()
    browser.switch_to.window(main_handle)
    return main_handle

def next_level(browser, super_handles, btn):
    # 进入子页面，并切换至子页面
    btn.click()
    for handle in list(set(browser.window_handles) ^ set(super_handles)):
        browser.switch_to.window(handle)
    time.sleep(5)
    return browser.current_window_handle


if __name__ == '__main__':
    port = sys.argv[1] if len(sys.argv) > 1 and sys.argv[1] else 9222
    if not os.path.exists('classes'):
        os.makedirs('classes')
    browser = init(port)
    main_handle = close_others(browser)
    browser.get('https://xiaoe.kaikeba.com/bought')
    time.sleep(3)
    class_btns = browser.find_elements(By.CSS_SELECTOR, '.btn.theme-customize-bg')
    for i in range(len(class_btns)):
        class_btn = class_btns[i]
        class_handle = next_level(browser, [main_handle], class_btn)
        class_title = None
        for i in range(3):
            try:
                class_title = browser.find_element(By.CSS_SELECTOR, '.course_title').text
            except:
                browser.refresh()
                continue
        if not class_title:
            sys.exit(1)
        print(f'课程：{class_title}')
        load_more_btn = browser.find_element(By.CSS_SELECTOR, '.column_catalog_item_wrap+.load_more_btn')
        while load_more_btn.is_displayed() and load_more_btn.is_enabled():
            try:
                load_more_btn.click()
            except:
                pass
            time.sleep(3)
            load_more_btn = browser.find_element(By.CSS_SELECTOR, '.column_catalog_item_wrap+.load_more_btn')
        lesson_btns = browser.find_elements(By.CSS_SELECTOR, '.column_catalog_item_wrap>.catalogue_item')
        
        if not os.path.exists(f'classes\\{class_title}'):
            os.makedirs(f'classes\\{class_title}')

        performance_log = browser.get_log('performance')
        for log in performance_log:
            message = json.loads(log['message'])['message']
            method = message['method']
            if method == 'Network.responseReceived':
                url = message['params']['response']['url']
                if url == 'https://xiaoe.kaikeba.com/xe.course.business.column.items.get/2.0.0':
                    request_id = message['params']['requestId']
                    request_body = browser.execute_cdp_cmd('Network.getRequestPostData', {'requestId': request_id})
                    class_id = json.loads(request_body['postData'])['column_id']
                    p_idx = json.loads(request_body['postData'])['page_index']
                    response_body = browser.execute_cdp_cmd('Network.getResponseBody', {'requestId': request_id})
                    lesson_list = json.loads(response_body['body'])['data']['list']
                    for j in range(len(lesson_list)):
                        lesson_data = lesson_list[j]
                        lesson_id = lesson_data['resource_id']
                        lesson_title = lesson_data['resource_title']
                        lesson_idx = (p_idx - 1) * 20 + j
                        lesson_url = f'https://xiaoe.kaikeba.com/p/t_pc/course_pc_detail/video/{lesson_id}?product_id={class_id}&content_app_id=&type=6'
                        print(class_title, lesson_idx, lesson_title, lesson_url)
                        with open(f'classes\\{class_title}\\{lesson_idx}-{lesson_title}', 'w') as lesson_file:
                            lesson_file.write(lesson_url)
        
        browser.close()
        browser.switch_to.window(main_handle)
        
