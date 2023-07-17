import requests
import base64
import os
import sys
from Crypto.Cipher import AES



def main(work_dir):
    if not work_dir.endswith('/'):
        work_dir += '/'
    if not os.path.exists(f'{work_dir}ts'):
        os.makedirs(f'{work_dir}ts')
        
    file_name = work_dir[0:-1]
    index = 0
    _uid = 'u_api_62e7922dd7f66_lP6V8g8sxS'
    with open(f'{work_dir}a.m3u8', 'r') as m3u8:
        with open(f'{work_dir}concat.txt', 'w') as concat:
            for line in m3u8.readlines():
                line = line.strip()
                if line[0] == '#':
                    if line.find('URI') > 0:
                        _uri = line[line.find('="') + 2: line.find('",')]
                        _key = get_key_from_url(url=_uri, userid=_uid)
                        key = base64.b64decode(_key)
                    if line.find('EXAMPLE-URL=') > 0:
                        if line.find('/drm/') > 0:
                            base_url = line[line.find('https'): line.find('/drm/') + 5]
                            param = line[line.find('&sign='):]
                        else:
                            ts_idx = line.find('.ts')
                            end = line.rfind('/', ts_idx)
                            base_url = line[line.find('https'): end]
                            param = ''
                    continue
                if line.__len__ == 0:
                    continue
                index += 1
                url = f'{base_url}{line}{param}'
                # url = 'https://btt-vod.xiaoeknow.com/529d8d60vodtransbj1252524126/f5d50315387702303839288504/drm/v.f421220_0.ts?start=860368&end=996303&type=mpegts&sign=49c72a6516bcfe2215964fc694326bbe&t=646eaa80&us=NgXMGMnBuZ'
                headers = {
                    "Authority": "btt-vod.xiaoeknow.com",
                    "Accept": "*/*",
                    # "Accept-Encoding": "gzip, deflate, br",
                    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
                    "Connection": "keep-alive",
                    # "Host": "bf1.aikan-jx.com",
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
                with open(f"{work_dir}ts/%0.8d.ts" % index, 'wb') as f:
                    if key == None:
                        f.write(data)
                    else:
                        f.write(aes.decrypt(data))
                    f.flush()
                    concat.write("file 'ts\%0.8d.ts'\n" % index)
                    print("写入文件成功 ", index)
    concat_cmd = f'ffmpeg -f concat -safe 0 -i {work_dir}concat.txt -c copy {file_name}.mp4'
    os.system(concat_cmd)


def get_key_from_url(url: str, userid: str) -> str:
    """
    通过请求m3u8文件中的key的url,获取解密视频key的base64字符串密钥
    :param url: m3u8文件中获取key的url
    :param userid: 用户id，放视频时飘动的那一串
    :return: key的base64字符串
    """
    # url拼接uid参数
    url += f'&uid={userid}'
    # 发送get请求
    rsp = requests.get(url=url)
    rsp_data = rsp.content
    if len(rsp_data) == 16:
        userid_bytes = bytes(userid.encode(encoding='utf-8'))
        result_list = []
        for index in range(0, len(rsp_data)):
            result_list.append(
                rsp_data[index] ^ userid_bytes[index])
        print(result_list)
        return base64.b64encode(bytes(result_list)).decode()
    else:
        print(f"获取异常，请求返回值：{rsp.text}")
        return ''


if __name__ == '__main__':
    # work_dir = '【2023考研公共课】数学（一）/【数学】高数基础精讲4'
    work_dir = sys.argv[1]
    main(work_dir)

    # for i in range(4382):

    #     key = base64.b64decode('sTtqBJrBjWODruUzPSkf9g====')
    #     aes = AES.new(key, AES.MODE_CBC)
        
    #     with open("ts/%0.4d.ts" % (i + 1), 'rb') as f:
    #         content = f.read()
        
    #     content_de = aes.decrypt(content)

    #     with open("ts-de/%0.4d.ts" % (i + 1), 'wb') as f:
    #         f.write(content_de)

    # _url = 'https://app.xiaoe-tech.com/xe.basic-platform.material-center.distribute.vod.pri.get/1.0.0?app_id=appqszhpsdw5896&mid=m_ZQXmVAEJPfEQf_kKQ4TPXF&urld=d8517a167fc272dc6f3dac053d8d573a'
    # _uid = 'u_api_62e7922dd7f66_lP6V8g8sxS'
    # base64_key = get_key_from_url(url=_url, userid=_uid)
    # print(base64_key)

