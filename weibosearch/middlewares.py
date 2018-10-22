# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.htmlfrom pip._vendor import requests
import json
import logging
import requests
from scrapy import signals
from scrapy.exceptions import IgnoreRequest


class CookiesMiddleware():
    # 日志输出
    def __init__(self,cookies_pool_url):
        self.logger = logging.getLogger(__name__)
        self.cookies_pool_url = cookies_pool_url

    def _get_random_cookies(self):
        # 调用cookies池
        try:
            response = requests.get('COOKIES_POOL_URL')
            if response.status_code==200:
                return json.loads(response.text)
        except ConnectionError:
            return None

    @classmethod
    def from_crawler(cls,crawler):
        return  cls(
            cookies_pool_url = crawler.settings.get('COOKIES_POOL_URL')
        )

    def process_request(self,request,spider):
        cookies=self._get_random_cookies()
        if cookies:
            request.cookies = cookies
            # 输出 为字符串
            self.logger.debug('Using Cookies'+json.dumps(cookies))
        else:
            self.logger.debug('No Valid Cookies')

    def process_response(self,request,response,spider):
        if response.status in [300,301,302,303]:
            try:
                redirect_url = response.headers['location']
                if 'passport' in redirect_url:
                    self.logger.warning('Need Login, Updating Cookies')
                elif 'weibo.cn/security' in redirect_url:
                    self.logger.warning('Account is Locked!')
                request.cookies = self._get_random_cookies()
                return request
            except:
                raise IgnoreRequest
        elif response.status in [414]:
            return request
        else:
            return response



