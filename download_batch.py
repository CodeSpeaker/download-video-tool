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
    time.sleep(3)
    return browser.current_window_handle


if __name__ == '__main__':
    port = sys.argv[1] if len(sys.argv) > 1 and sys.argv[1] else 9222
    class_index = sys.argv[2] if len(sys.argv) > 2 and sys.argv[2] else 7
    lesson_index = sys.argv[3] if len(sys.argv) > 3 and sys.argv[3] else 66

    browser = init(port)
    main_handle = close_others(browser)
    browser.get('https://xiaoe.kaikeba.com/bought')
    time.sleep(3)
    class_btns = browser.find_elements(By.CSS_SELECTOR, '.btn.theme-customize-bg')
    for i in range(len(class_btns)):
        if i < int(class_index):
            continue
        
        class_btn = class_btns[i]
        class_handle = next_level(browser, [main_handle], class_btn)
        class_title = browser.find_element(By.CSS_SELECTOR, '.course_title').text
        print(f'课程：{class_title}')
        load_more_btn = browser.find_element(By.CSS_SELECTOR, '.column_catalog_item_wrap+.load_more_btn')
        while load_more_btn.is_displayed() and load_more_btn.is_enabled():
            try:
                load_more_btn.click()
            except:
                pass
            time.sleep(1)
            load_more_btn = browser.find_element(By.CSS_SELECTOR, '.column_catalog_item_wrap+.load_more_btn')
        lesson_btns = browser.find_elements(By.CSS_SELECTOR, '.column_catalog_item_wrap>.catalogue_item')
        for j in range(len(lesson_btns)):
            lesson_btn = lesson_btns[j]
            if j < int(lesson_index):
                continue

            next_level(browser, [main_handle, class_handle], lesson_btn)
            is_success = False
            for retry_times in range(3):
                try:
                    print(f'尝试：{retry_times + 1}次')
                    if down_load(browser, class_title):
                        is_success = True
                        break
                except Exception as e:
                    print(e)
            if not is_success:
                raise Exception(f'发生错误：{i} {j}'.format(i, j))
            browser.close()
            browser.switch_to.window(class_handle)
        
        browser.close()
        browser.switch_to.window(main_handle)
        
