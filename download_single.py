import sys
from down_load import *

def download_single(port, class_title):
    browser = init(port)
    down_load(browser, class_title)

if __name__ == '__main__':
    port = sys.argv[1]
    class_title = sys.argv[2] if sys.argv[2] else 'unnamed'

    download_single(port, class_title)




    # download_single(9222, '电子琴高效系统入门班0606期')



    # dir = '电子琴高效系统入门班0606期\\2.VIP陪练课程'
    # concat_cmd = f'ffmpeg -f concat -safe 0 -i {dir}\\concat.txt -c copy {dir}.mp4'
    # print(f'concat_cmd: {concat_cmd}')
    # process = subprocess.run(concat_cmd)
    # print(process)