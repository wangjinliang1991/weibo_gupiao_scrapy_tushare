# -*- coding: utf-8 -*-
import re
from urllib import response
from urllib.request import Request
from weibosearch.items import *
import scrapy
from scrapy import FormRequest, Spider
import tushare as ts


class WeiboSpider(scrapy.Spider):
    name = 'weibo'
    allowed_domains = ['weibo.cn']
    search_url = 'https://weibo.cn/search/mblog'
    max_page = 100

    def start(self):
        result = ts.get_hs300s()
        keywords = result['code'].tolist()
        for keyword in keywords:
            url = '{url}?keyword={keyword}.format(url=self.search_url,keyword=keyword)'
            for page in range(self.max_page+1):
                data = {
                    'mp': str(self.max_page),
                    'page': str(page)
                }
                yield FormRequest(url, callback=self.parse_index,meta={'keyword': response.meta['keyword']},formdata=data)

    def parse_index(self,response):
        # print(response.text)
        weibos = response.xpath('//div[@class="c" and contains(@id, "M_")]')
        print(weibos)
        for weibo in weibos:
            is_forward = bool(weibo.xpath('.//span[@class="cmt"]').extract_first())
            if is_forward:
                detail_url = weibo.xpath('.//a[contains(., "原文评论[")]//@href').extract_first()
            else:
                detail_url = weibo.xpath('.//a[contains(., "评论[")]//@href').extract_first()
            print(detail_url)
            yield Request(detail_url,callback=self.parse_detail)

    def parse_detail(self,response):
        id = re.search('comment\/(.*?)\?',response.url).group(1)
        url = response.url
        content = ''.join(response.xpath('//div[@id="M_"]//span[@class="ctt"]//text()').extract())
        print(id,url,content)
        comment_count = response.xpath('//span[@class="pms"]//text()').re_first('评论\[(.*)]')
        forward_count = response.xpath('//a[contains(.,"转发[")]//text()').re_first('转发\[.*]')
        like_count = response.xpath('//a[contains(.,"赞[")]').re_first('赞\[(.*)]')
        print(comment_count,forward_count,like_count)
        posted_at = response.xpath('//div[@id="M_"]//span[@class="ct"]//text()').extract_first(default=None)
        user = response.xpath('//div[@id="M_"]/div[1]/a/text()').extract_first(default=None)
        keyword = response.meta['keyword']
        weibo_item = WeiboItem()
        for field in weibo_item.fields:
            try:
                weibo_item[field] = eval(field)
            except NameError:
                self.logger.debug("Field is not defined" + field)
        yield weibo_item




















