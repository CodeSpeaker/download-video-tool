import time
import sys

from download_util import *

if __name__ == '__main__':
    port = sys.argv[1] if len(sys.argv) > 1 and sys.argv[1] else 9222
    download_util = DownloadUtil(port)
    download_util.close_others()
    if not os.path.exists('m3u8s'):
        os.makedirs('m3u8s')

    for class_title in os.listdir('classes'):
        if os.path.isdir(f'classes\\{class_title}'):
            logger.info(class_title)
            if not os.path.exists(f'm3u8s\\{class_title}'):
                os.makedirs(f'm3u8s\\{class_title}')

        full_file_list = os.listdir(f'classes\\{class_title}')
        full_file_list.sort(key = lambda str : int(str[0:str.find('-')]))
        for file in full_file_list:
            lesson_name = file[file.find('-') + 1:]
            m3u8_name = f'm3u8s\\{class_title}\\{lesson_name}.m3u8'
            if os.path.exists(m3u8_name):
                continue
            with open(f'classes\\{class_title}\\{file}', 'r') as f:
                url = f.readline()
                content = ''
                while not content:
                    download_util.open(url)
                    time.sleep(3)
                    logger.info(m3u8_name)
                    content = download_util.get_m3u8_content()
                    if content:
                        with open(m3u8_name, 'wb') as m3u8:
                            m3u8.write(content)