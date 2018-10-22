# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymongo
from weibosearch.items import WeiboItem
import time,re

class WeibosearchPipeline(object):
    def parse_time(self,datetime):
        if re.match('\d+月\d+日', datetime):
            datetime = time.strftime('%Y年', time.localtime()) + datetime
        if re.match('\d+分钟前', datetime):
            minute = re.match('(\d+)',datetime).group(1)
            datetime = time.strftime('%Y年%m月%d日 %H:%M', time.localtime(time.time()-float(minute)*60))
        if re.match('今天.*', datetime):
            datetime = re.match('今天(.*)',datetime).group(1).strip()
            datetime = time.strftime('%Y年%m月%日 %H:%M', time.localtime(time.time()  )+''+datetime)
        return datetime

    def process_item(self, item, spider):
        if isinstance(item, WeiboItem):
            if item.get("content"):
                item['contenet'] = item['content'].lstrip(':').strip()
            if item.get('posted_at'):
                item['posted_at'] = item['posted_at'].strip()
                item['posted_at'] = self.parse_time(item['posted_at'])

class MongoPipeline():

    def __init__(self,mongo_uri,mongo_db):
        self.mongo_url = mongo_uri
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db = crawler.settings.get('MONGO_DB')
        )

    def open_spider(self,spider):
        self.client = pymongo.MongoClient(self.mongo_url)
        self.db = self.client[self.mongo_db]

    def close_spider(self,spider):
        self.client.close()

    def process_item(self, item, spider):
        self.db[item.table_name].update({'id': item.get('id')},{'$set': dict(item)},True)
        return item