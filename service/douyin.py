import json
import re
from django.http import HttpResponse
from core.interface import Service
from core.model import Result, ErrorResult
from tools import http_utils
from core import config
from core.type import Video


headers = {
    "user-agent": config.douyin_agent
}

download_headers = {
    "accept": "*/*",
    "accept-encoding": "identity;q=1, *;q=0",
    "accept-language": "zh-CN,zh;q=0.9,ja;q=0.8,en;q=0.7,zh-TW;q=0.6,de;q=0.5,fr;q=0.4,ca;q=0.3,ga;q=0.2",
    "range": "bytes=0-",
    "sec-fetch-dest": "video",
    "sec-fetch-mode": "no-cors",
    "sec-fetch-site": "cross-sit",
    "user-agent": config.user_agent
}

vtype = Video.DOUYIN


class DouyinService(Service):

    @classmethod
    def get_prefix_pattern(cls) -> str:
        # www.iesdouyin.com
        return 'douyin\.com\/'

    @classmethod
    def make_url(cls, index) -> str:
        return 'https://v.douyin.com/' + index

    @classmethod
    def convert_share_urls(cls, url: str):
        """
        用于将分享链接(短链接)转换为原始链接/Convert share links (short links) to original links
        :return: 原始链接/Original link
        """
        # 检索字符串中的链接/Retrieve links from string
        url = cls.get_url(url)
        # 判断是否有链接/Check if there is a link
        if url is None:
            print('无法检索到链接/Unable to retrieve link')
            return None
        # 判断是否为抖音分享链接/judge if it is a douyin share link
        if 'douyin' in url:
            """
            抖音视频链接类型(不全)：
            1. https://v.douyin.com/MuKhKn3/
            2. https://www.douyin.com/video/7157519152863890719
            3. https://www.iesdouyin.com/share/video/7157519152863890719/?region=CN&mid=7157519152863890719&u_code=ffe6jgjg&titleType=title&timestamp=1600000000&utm_source=copy_link&utm_campaign=client_share&utm_medium=android&app=aweme&iid=123456789&share_id=123456789
            抖音用户链接类型(不全)：
            1. https://www.douyin.com/user/MS4wLjABAAAAbLMPpOhVk441et7z7ECGcmGrK42KtoWOuR0_7pLZCcyFheA9__asY-kGfNAtYqXR?relation=0&vid=7157519152863890719
            2. https://v.douyin.com/MuKoFP4/
            抖音直播链接类型(不全)：
            1. https://live.douyin.com/88815422890
            """
            if 'v.douyin' in url:
                # 转换链接/convert url
                # 例子/Example: https://v.douyin.com/rLyAJgf/8.74
                url = re.compile(r'(https://v.douyin.com/)\w+', re.I).match(url).group()
                print('正在通过抖音分享链接获取原始链接...')
                try:
                    response = http_utils.get(url, header=headers)
                    # if response.status == 302:
                    #     url = response.headers['Location'].split('?')[0] if '?' in response.headers[
                    #         'Location'] else \
                    #         response.headers['Location']
                    #     print('获取原始链接成功, 原始链接为: {}'.format(url))
                    #     return url
                    print(response.headers)
                    print(response.url)
                    url = response.headers['Location'].split('?')[0] if '?' in response.headers[
                        'Location'] else \
                        response.headers['Location']
                    print('获取原始链接成功, 原始链接为: {}'.format(url))
                    return url
                    # with aiohttp.ClientSession() as session:
                    #        with session.get(url, headers=cls.headers, allow_redirects=False,
                    #                            timeout=10) as response:
                    #         if response.status == 302:
                    #             url = response.headers['Location'].split('?')[0] if '?' in response.headers[
                    #                 'Location'] else \
                    #                 response.headers['Location']
                    #             print('获取原始链接成功, 原始链接为: {}'.format(url))
                    #             return url
                except Exception as e:
                    print('获取原始链接失败！')
                    print(e)
                    return None
            else:
                print('该链接为原始链接,无需转换,原始链接为: {}'.format(url))
                return url
        # 判断是否为TikTok分享链接/judge if it is a TikTok share link
        # elif 'tiktok' in url:
        #     """
        #     TikTok视频链接类型(不全)：
        #     1. https://www.tiktok.com/@tiktok/video/6950000000000000000
        #     2. https://www.tiktok.com/t/ZTRHcXS2C/
        #     TikTok用户链接类型(不全)：
        #     1. https://www.tiktok.com/@tiktok
        #     """
        #     if '@' in url:
        #         print('该链接为原始链接,无需转换,原始链接为: {}'.format(url))
        #         return url
        #     else:
        #         print('正在通过TikTok分享链接获取原始链接...')
        #         try:
        #             async with aiohttp.ClientSession() as session:
        #                 async with session.get(url, headers=self.headers, proxy=self.proxies, allow_redirects=False,
        #                                        timeout=10) as response:
        #                     if response.status == 301:
        #                         url = response.headers['Location'].split('?')[0] if '?' in response.headers[
        #                             'Location'] else \
        #                             response.headers['Location']
        #                         print('获取原始链接成功, 原始链接为: {}'.format(url))
        #                         return url
        #         except Exception as e:
        #             print('获取原始链接失败！')
        #             print(e)
        #             return None

    @classmethod
    def get_douyin_video_id(cls, original_url: str):
        """
        获取视频id
        :param original_url: 视频链接
        :return: 视频id
        """
        # 正则匹配出视频ID
        try:
            video_url = DouyinService.convert_share_urls(original_url)
            # video_url = original_url
            print(video_url+'127行')
            # 链接类型:
            # 视频页 https://www.douyin.com/video/7086770907674348841
            if '/video/' in video_url:
                key = re.findall('/video/(\d+)?', video_url)[0]
                print('获取到的抖音视频ID为: {}'.format(key))
                return key
            # 发现页 https://www.douyin.com/discover?modal_id=7086770907674348841
            elif 'discover?' in video_url:
                key = re.findall('modal_id=(\d+)', video_url)[0]
                print('获取到的抖音视频ID为: {}'.format(key))
                return key
            # 直播页
            elif 'live.douyin' in video_url:
                # https://live.douyin.com/1000000000000000000
                video_url = video_url.split('?')[0] if '?' in video_url else video_url
                key = video_url.replace('https://live.douyin.com/', '')
                print('获取到的抖音直播ID为: {}'.format(key))
                return key
            # note
            elif 'note' in video_url:
                # https://www.douyin.com/note/7086770907674348841
                key = re.findall('/note/(\d+)?', video_url)[0]
                print('获取到的抖音笔记ID为: {}'.format(key))
                return key
        except Exception as e:
            print('获取抖音视频ID出错了:{}'.format(e))
            return None
    @classmethod
    def fetch(cls, url: str, mode=0) -> Result:
        url = cls.get_url(url)
        if url is None:
            return ErrorResult.URL_NOT_INCORRECT

        # 请求短链接，获得itemId
        res = http_utils.get(url, header=headers)
        if http_utils.is_error(res):
            return Result.error(res)

        html = str(res.content)
        try:
             item_id = re.findall(r"(?<=video/)\d+", res.url)[0]
            # item_id = res.url.split("?")[0].split("video/")[1]
        except IndexError:
            return Result.failed(res.reason)
        # try:
        #     # item_id = re.findall(r"(?<=video/)\d+", res.url)[0]
        #     item_id =DouyinService.get_douyin_video_id(url)
        # except IndexError:
        #     print('获取失败')
        # 组装视频长链接
        # infourl = "https://www.iesdouyin.com/web/api/v2/aweme/iteminfo/?item_ids=" + item_id + "&dytk="# + dytk
        infourl = f"https://www.iesdouyin.com/aweme/v1/web/aweme/detail/?aweme_id={item_id}&aid=1128&version_name=23.5.0&device_platform=android&os_version=2333&Github=Evil0ctal&words=FXXK_U_ByteDance"

        # 请求长链接，获取play_addr
        url_res = http_utils.get(infourl, header=headers)
        if http_utils.is_error(url_res):
            return Result.error(url_res)

        data = json.loads(str(url_res.text))
        if not data['status_code'] == 0:
            return Result.failed(data['status_msg'])
        print(data)
        # item = data['item_list'][0]
        item = data['aweme_detail']
        url_type_code = item['aweme_type']
        url_type_code_dict = {
            # 抖音/Douyin
            2: 'image',
            4: 'video',
            68: 'image',
            # TikTok
            0: 'video',
            51: 'video',
            55: 'video',
            58: 'video',
            61: 'video',
            150: 'image'
        }
        url_type = url_type_code_dict.get(url_type_code, 'video')
        if url_type == 'video':
            result = DouyinService.get_video(item)
        elif url_type == 'image':
            result = DouyinService.get_image(item)
            result.extra = ".zip"
        else:
            return ErrorResult.VIDEO_ADDRESS_NOT_FOUNT
        # if item['aweme_type'] == 4:
        #     result = DouyinService.get_video(item)
        # elif item['aweme_type'] == 2:
        #     result = DouyinService.get_image(item)
        #     result.extra = ".zip"
        # else:
        #     return ErrorResult.VIDEO_ADDRESS_NOT_FOUNT

        if mode == 1:
            result.ref = res.url

        return result

    @staticmethod
    def get_video(data) -> Result:
        # try:
        #     vid = data['video']['vid']
        # except Exception as e:
        #     return ErrorResult.VIDEO_ADDRESS_NOT_FOUNT
        #
        # try:
        #     ratio = data['video']['ratio']
        # except Exception as e:
        #     ratio = "540p"
        #
        # link = "https://aweme.snssdk.com/aweme/v1/play/?video_id=" + vid + \
        #         "&line=0&ratio="+ratio+"&media_type=4&vr_type=0&improve_bitrate=0" \
        #         "&is_play_url=1&is_support_h265=0&source=PackSourceEnum_PUBLISH"

        uri = data['video']['play_addr']['uri']
        # 有水印
        wm_video_url = data['video']['play_addr']['url_list'][0]
        wm_video_url_HQ = f"https://aweme.snssdk.com/aweme/v1/playwm/?video_id={uri}&radio=1080p&line=0"
        # 无水印
        nwm_video_url = wm_video_url.replace('playwm', 'play')
        nwm_video_url_HQ = f"https://aweme.snssdk.com/aweme/v1/play/?video_id={uri}&ratio=1080p&line=0"
        return Result.success(json.dumps({
            "code":200,
            "data":nwm_video_url_HQ
        } ))

    @staticmethod
    def get_image(data) -> Result:
        try:
            images = data['images']
        except Exception as e:
            return ErrorResult.VIDEO_ADDRESS_NOT_FOUNT

        image_urls = []
        for image in images:
            urls = image['url_list']
            url = urls[-1]
            image_urls.append(url)

        result = Result.success(image_urls)
        result.type = 1
        return result

    @classmethod
    def download(cls, url) -> HttpResponse:
        return cls.proxy_download(vtype, url, download_headers, ".mp4")


if __name__ == '__main__':
    DouyinService.fetch('https://v.douyin.com/cCBrrq/')
