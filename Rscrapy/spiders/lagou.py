# -*- coding: utf-8 -*-
import json

import time

import requests
from lxml import etree
from urllib.parse import urlencode

import scrapy
from copy import deepcopy
from scrapy_redis.spiders import RedisSpider


class LagouSpider(RedisSpider):
    name = 'lagou'
    allowed_domains = ['lagou.com']
    info_str = '[ *] 如果需要启动lagou爬虫，请在配置的redis中执行：\n lpush lagou "https://www.lagou.com/" \n[ *] 请输入任意继续执行本程序'
    # input(info_str)
    redis_key = "lagou"
    base_url = 'https://www.lagou.com/jobs/positionAjax.json?'
    detail_url = 'https://www.lagou.com/jobs/%d.html'
    image_prefix = 'http://www.lgstatic.com/thumbnail_120x120/'
    city = '深圳'

    def parse(self, response):
        # 一级类 如：技术、产品、设计...
        print('构造初始请求')
        category_1_selectors = response.xpath('//div[@class="menu_box"]')
        for category_1_selector in category_1_selectors:
            category_1_name = category_1_selector.xpath('./div[1]/div[1]/h2/text()').extract_first().strip()
            # print('一级分类：', category_1_name)
            # 二级类 如：后端开发、移动开发、前端开发...
            category_2_selectors = category_1_selector.xpath('./div[2]/dl')
            for category_2_selector in category_2_selectors:
                category_2_name = category_2_selector.xpath('./dt/span/text()').extract_first()
                # print('二级分类：', category_2_name)
                # 三级类 如：Java、C++、PHP...
                category_3_selectors = category_2_selector.xpath('./dd/a')
                for category_3_selector in category_3_selectors:
                    category_3_name = category_3_selector.xpath('./text()').extract_first().strip()
                    # print('三级分类：', category_3_name)
                    # 职位列表
                    category_3_url = category_3_selector.xpath('./@href').extract_first()
                    # print('三级分类url：', category_3_url)
                    # 构造翻页后的url
                    for pn in range(1, 31):
                        # 构造 Ajax请求
                        item = {'category_1_name': category_1_name,
                                'category_2_name': category_2_name,
                                'category_3_name': category_3_name}
                        query_params = urlencode({"city": self.city,
                                                  "needAddtionalResult": "false"})
                        url = self.base_url + query_params
                        form_data = {'pn': str(pn),
                                     'kd': category_3_name}
                        if pn == 1:
                            form_data['first'] = 'true'

                        headers = response.request.headers
                        headers['Referer'] = "https://www.lagou.com/jobs/list_%s?%s&cl=false&fromSearch=true&labelWords=&suginput=" %\
                                             (urlencode({'keyword': category_3_name}).split('=')[-1], urlencode({'city': self.city})),
                        # 返回职位信息的Ajax请求
                        yield scrapy.FormRequest(url,
                                                 formdata=form_data,
                                                 headers=headers,
                                                 meta={'item': deepcopy(item)},
                                                 callback=self.parse_detail,
                                                 dont_filter=True)
        print('构造初始请求完毕')


    def parse_detail(self, response):
        # 获取详情页信息
        print('解析', response.request.url)
        try:
            content = json.loads(response.body.decode())['content']
        except Exception as e:
            # print(response.url, e)
            return
        # print('content.pageNo:', content['pageNo'])
        # hrInfoMap = content['hrInfoMap']
        result = content['positionResult']['result']

        # 构造cookies
        try:
            cookies_str = response.headers.get('Set-Cookie').decode()
            cookies_list = list(map(lambda x: x.strip(), cookies_str.split(';')))
            cookies = {kv.split('=')[0]: kv.split('=')[1] for kv in cookies_list if kv != ''}
        except Exception as e:
            cookies = {}
        for position in result:
            positionId = position['positionId']
            item = response.meta['item']
            item.update(position)
            item['detailUrl'] = self.detail_url % positionId
            item['source'] = self.name
            item['companyLogo'] = self.image_prefix + item['companyLogo']
            item['createTime'] = int(time.mktime(time.strptime(item['createTime'], "%Y-%m-%d %H:%M:%S")))
            item['updateDate'] = int(item['createTime'])

            yield item
            # print('构造详情页请求：', item['detailUrl'])
            yield scrapy.Request(item['detailUrl'],
                                 callback=self.parse_describe,
                                 cookies=cookies,
                                 meta={'item': deepcopy(item)})

    def parse_describe(self, response):
        item = response.meta['item']
        positionId = item['positionId']
        html = etree.HTML(response.body.decode())
        description = html.xpath('//*[@id="job_detail"]/dd[2]/div/p/text()')
        # print('*' * 50)
        if description:
            # print('=' * 50)
            # print({'description': description,
            #        'positionId': positionId})
            # print('=' * 50)
            yield {'description': description,
                   'positionId': positionId}
        else:
            try:
                cookies_str = response.headers.get('Set-Cookie').decode()
                cookies_list = list(map(lambda x: x.strip(), cookies_str.split(';')))
                cookies = {kv.split('=')[0]: kv.split('=')[1] for kv in cookies_list if kv != ''}
            except Exception as e:
                cookies = {}
        #     print('positionId:', positionId)
            print('parse_describe:', response.request.url, response.status)
        # print('*' * 50)
            yield scrapy.Request(item['detailUrl'],
                                 callback=self.parse_describe,
                                 cookies=cookies,
                                 meta={'item': deepcopy(item)},
                                 dont_filter=True)
