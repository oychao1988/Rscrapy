# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html
import time
import faker
import requests
from scrapy import signals

from Rscrapy import settings

fake = faker.Faker('zh_CN')

class RscrapySpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Response, dict
        # or Item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class RscrapyDownloaderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)

class UserAgentMiddleware(object):
    def process_request(self, request, spider):
        user_agent = fake.user_agent()
        request.headers['User-Agent'] = user_agent


class ProxyMiddleware(object):
    proxy_servers = [proxy_server for proxy_server in settings.__dict__.keys() if 'PROXY_POOL_SERVER' in proxy_server]

    def process_request(self, request, spider):
        success = False
        # print('=' * 25 + 'proxy' + '=' * 25)
        while not success:
            for proxy_server in self.proxy_servers:
                proxy = requests.get(getattr(settings, proxy_server)).text
                if proxy == 'no proxy!':
                    # print('*' * 25 + 'proxy' + '*' * 25)
                    print(getattr(settings, proxy_server), '：暂无代理ip！')
                else:
                    # print('*' * 25 + 'proxy' + '*' * 25)
                    # print('proxy:', proxy)
                    request.meta['proxy'] = 'http://%s' % proxy
                    success = True
                    # print('=' * 25 + 'proxy' + '=' * 25)
                    break
            else:
                print('代理ip不足，请稍候')
                time.sleep(60)

