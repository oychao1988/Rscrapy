import json
import re

import copy
import requests
import scrapy

from scrapy_redis.spiders import RedisSpider

class JulyeduSpider(scrapy.Spider):
    name = 'julyedu'
    allowed_domains = ['julyedu.com']
    # info_str = '[ *] 如果需要启动julyedu爬虫，请在配置的redis中执行：\n lpush julyedu "https://www.julyedu.com/question/index/type/1" \n[ *] 请输入任意继续执行本程序'
    # input(info_str)
    # redis_key = "julyedu"
    start_url = ['https://www.julyedu.com/question/index/type/1']

    def start_requests(self):


        cookies_str = 'UM_distinctid=165d14063631a4-027fee0caefe58-4a531929-100200-165d140636415a; PHPSESSID=k02an4v6mivgl2qpftjsqu73ue; infrom=1; token=21b81d7ac75e7b00-ac04308bd7485061; uid=483681; uname=%E6%89%8B%E6%9C%BA%E7%94%A8%E6%88%B7483681; role=3; CNZZDATA1259748782=1689767588-1536813983-https%253A%252F%252Fwww.baidu.com%252F%7C1544027541; ssid=k02an4v6mivgl2qpftjsqu73ue'
        cookies = {cookie.split('=')[0]: cookie.split('=')[1] for cookie in cookies_str.split('; ')}
        yield scrapy.Request(self.start_url[0], cookies=cookies, callback=self.parse, dont_filter=True)

    # 类别首页
    def parse(self, response):
        # 首页获取分类
        cate_str = re.search(r'var cate =  ({.*})', response.text).group(1)
        # print(cate_str)
        # 内容字典
        cate_dict = json.loads(cate_str)
        for sub_cate in cate_dict['category']:
            item = {}
            # 类别id
            item['kp_id'] = sub_cate['kp_id']
            # 类别名称
            item['kp_name'] = sub_cate['kp_name']
            # 首个问题
            item['ques_id'] = sub_cate['ques_id']
            # 问题数量
            item['ques_num'] = sub_cate['ques_num']
            # 构造问题首页
            item['ques_url'] = 'https://www.julyedu.com/question/big/kp_id/{kp_id}/ques_id/{ques_id}'.format(
                kp_id=item['kp_id'], ques_id=item['ques_id'])
            yield scrapy.Request(item['ques_url'],
                                 callback=self.parse_cate,
                                 meta={'item': copy.deepcopy(item)},
                                 dont_filter=True)

    def parse_cate(self, response):
        item = response.meta['item']
        # print(item)
        # 文档字符串
        json_str = re.search(r'var data = ({.*})', response.text).group(1)
        # 内容字典
        text_dict = json.loads(json_str)
        # kp列表
        kp_list = text_dict['list']
        # 构造问题url
        for kp in kp_list:
            item['ques_id'] = kp['ques_id']
            quesInfo_url = 'https://www.julyedu.com/question/big/kp_id/{kp_id}/ques_id/{ques_id}'.format(
                kp_id=kp['category_id'], ques_id=item['ques_id'])
            yield scrapy.Request(quesInfo_url,
                                 callback=self.parse_quesInfo,
                                 meta={'item': copy.deepcopy(item)},
                                 dont_filter=True)


    def parse_quesInfo(self, response):
        item = response.meta['item']
        print(item)
        # 文档字符串
        json_str = re.search(r'var data = ({.*})', response.text).group(1)
        # 内容字典
        text_dict = json.loads(json_str)
        # 问题和解析
        quesInfo = text_dict['quesInfo']
        # 问题
        item['ques'] = quesInfo['ques']
        # 解析
        item['analysis'] = quesInfo['analysis']
        yield item

