import os
import logging
from down_load import *

handler = logging.StreamHandler()
handler.setLevel(logging.INFO)
handler.setFormatter(logging.Formatter('%(asctime)s %(message)s'))
logger = logging.getLogger('choose_lesson')
logger.setLevel(logging.INFO)
logger.addHandler(handler)

def close_others(browser):
    # 关闭其他页面，只保留一个页面操作，避免混乱
    main_handle = browser.current_window_handle
    for handle in browser.window_handles:
        if handle != main_handle:
            browser.switch_to.window(handle)
            browser.close()
    browser.switch_to.window(main_handle)
    return main_handle

if __name__ == '__main__':
    browser = init(9222)
    close_others(browser)

    for file in os.listdir('classes'):
        if os.path.isdir(f'classes\\{file}'):
            logger.info(file)
    
    while True:
        try:
            class_title = input('请选择：')
            full_file_list = os.listdir(f'classes\\{class_title}')
            full_file_list.sort(key = lambda str : int(str[0:str.find('-')]))
            file_list = []
            for file in full_file_list:
                exists = False
                file_name = file[file.find('-') + 1:]
                for root, dirs, files in os.walk(class_title):
                    for exsits_file in files:
                        if exsits_file[0: len(file_name)] == file_name:
                            exists = True
                            break
                    if exists:
                        break
                if exists:
                    continue
                file_list.append(file)

            for i in range(len(file_list)):
                for j in range(i, min(i + 3, len(file_list))):
                    logger.info(f'待下载-{j - i + 1}：{file_list[j]}')
                logger.info('进度：{}/{}'.format(len(full_file_list) - len(file_list) + i, len(full_file_list)))
                file = file_list[i]
                exists = False
                file_name = file[file.find('-') + 1:]
                for root, dirs, files in os.walk(class_title):
                    for exsits_file in files:
                        if exsits_file[0: len(file_name)] == file_name:
                            exists = True
                            break
                    if exists:
                        break
                if exists:
                    continue
                with open(f'classes\\{class_title}\\{file}', 'r') as f:
                    url = f.readline()
                    lesson_name = file[file.find('-') + 1:]
                    dir = '{}\\{}'.format(class_title, lesson_name)
                    is_success = False
                    while not is_success:
                        try:
                            is_success = down_load(browser, url, dir)
                        except Exception:
                            continue
                        
        except Exception:
            pass
        