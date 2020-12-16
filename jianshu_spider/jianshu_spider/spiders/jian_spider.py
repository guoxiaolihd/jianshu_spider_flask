import re

import scrapy
from fake_useragent import UserAgent
from scrapy import Request
from ..items import JianshuUserBaseInfoItem

class JianSpiderSpider(scrapy.Spider):
    base_headers = {'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6,zh-TW;q=0.4',
                    'Host': 'www.jianshu.com',
                    'Accept-Encoding': 'gzip, deflate, sdch',
                    'X-Requested-With': 'XMLHttpRequest',
                    'Accept': 'text/html, */*; q=0.01',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36',
                    'Connection': 'keep-alive',
                    'Referer': 'http://www.jianshu.com'}
    # 只加载列表模块
    ajax_headers = dict(base_headers, **{"X-PJAX": "true", 'User-Agent': UserAgent().random})

    name = 'jian_spider'
    allowed_domains = ['jianshu.com']
    # start_urls = ['http://jianshu.com/']
    def start_requests(self):
        yield Request('https://www.jianshu.com/recommendations/users?page=1&per_page=200',
                      headers=self.base_headers)

    def parse_seeduser(self, response):
        slug = response.meta['slug']
        base_info_item = JianshuUserBaseInfoItem()

        div_main_top = response.xpath('//div[@class="main-top"]')
        nickname = div_main_top.xpath('.//div[@class="title"]//a/text()').extract_first()
        head_pic = div_main_top.xpath('.//a[@class="avatar"]//img/@src').extract_first()
        gender_tmp = div_main_top.xpath('.//div[@class="title"]//i/@class').extract()
        if gender_tmp:
            gender = gender_tmp[0].split('-')[-1]
        else:
            gender = 'No'
        is_contract_tmp = div_main_top.xpath('.//div[@class="title"]//span[@class="author-tag"]').extract()
        if is_contract_tmp:
            is_contract = '签约作者'
        else:
            is_contract = 'No'
        info = div_main_top.xpath('.//li//p//text()').extract()

        base_info_item['nickname'] = nickname
        base_info_item['slug'] = slug
        base_info_item['head_pic'] = head_pic
        base_info_item['gender'] = gender
        base_info_item['is_contract'] = is_contract
        base_info_item['following_num'] = int(info[0])
        base_info_item['followers_num'] = int(info[1])
        base_info_item['articles_num'] = int(info[2])
        base_info_item['words_num'] = int(info[3])
        base_info_item['be_liked_num'] = int(info[4])
        yield base_info_item

    def parse_followers(self,response):
        user_slug = response.meta['slug']
        page = response.meta['page']
        base_info_item = JianshuUserBaseInfoItem()
        user_lis = response.xpath('//li')
        if user_lis:
            page += 1
            yield Request(url=f'https://www.jianshu.com/u/{user_slug}/followers?page={page}'
                          , headers=self.ajax_headers
                          , callback=self.parse_followers()
                          , meta={'slug': user_slug, 'page': page})

            for user in user_lis:
                base_info_item['nickname'] = user.xpath('.//a[@class="name"]/text()').extract_first()
                base_info_item['slug'] = user.xpath('.//a[@class="name"]/@href').extract_first().split('/')[-1]
                base_info_item['head_pic'] = user.xpath('.//img/@src').extract_first()
                span = user.xpath('.//span/text()').extract()
                base_info_item['following_num'] = int(re.search('\d+', span[0]).group())
                base_info_item['followers_num'] = int(re.search('\d+', span[1]).group())
                base_info_item['articles_num'] = int(re.search('\d+', span[2]).group())
                meta_text = user.xpath('.//div[@class="meta"]')[1].xpath('text()').extract_first()
                meta_num = re.findall('\d+', meta_text)
                base_info_item['words_num'] = int(meta_num[0])
                base_info_item['be_liked_num'] = int(meta_num[1])
                print(dict(base_info_item))
                yield base_info_item




    def parse(self, response):
        # print(response.text)
        user_data_lst = response.xpath('.//div[@class="wrap"]/a//@href').extract()
        print(user_data_lst)
        print(len(user_data_lst))
        # /users/51b4ef597b53
        for url in user_data_lst:
            user_slug = url.replace('/users/','')
            yield Request(url=f'https://www.jianshu.com/u/{user_slug}'
                          ,headers=self.base_headers
                          ,callback=self.parse_seeduser
                          ,meta={'slug':user_slug})

            yield Request(url=f'https://www.jianshu.com/u/{user_slug}/followers'
                          , headers=self.ajax_headers
                          , callback=self.parse_followers
                          , meta={'slug': user_slug,'page':1})



