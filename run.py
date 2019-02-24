from scrapy import cmdline

def run():
    # cmdline.execute(['scrapy', 'crawl', 'lagou'])
    cmdline.execute(['scrapy', 'crawl', 'julyedu'])


if __name__ == '__main__':
    run()

