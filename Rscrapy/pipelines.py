# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import json

import requests
from Rscrapy import settings


class RscrapyPipeline(object):
    def process_item(self, item, spider):
        return item

class RecruitPipeline(object):
    def process_item(self, item, spider):
        # 向数据库服务器保存该条信息
        for i in range(3):
            # 补充职位描述信息
            if item.get('description'):
                result = requests.put(
                    settings.RECRUIT_DATABADE_SERVER % spider.name + '%d/' % int(item['positionId']), item).json()
            # 新增职位信息
            else:
                result = requests.post(settings.RECRUIT_DATABADE_SERVER % spider.name, item).json()
            print(item['source'], item['positionId'], result['errmsg'], result['errno'])
            if result['errno'] in ['0', '4003']:
                break
        return item

class JulyeduPipeline(object):
    def __init__(self):
        self.file = open('Julyedu_quesInfo.json', 'wb+')

    def process_item(self, item, spider):
        content = json.dumps(item, ensure_ascii=False) + "\n"
        self.file.write(content.encode('utf-8'))
        return item

    def close_spider(self):
        self.file.close()