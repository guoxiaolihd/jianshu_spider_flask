# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import pymongo

class JianshuSpiderPipeline:

    def __init__(self,mongo_host,mongo_db):
        self.collection_name = 'user'
        self.mongo_host = mongo_host
        self.mongo_db = mongo_db
        self.client = pymongo.MongoClient(self.mongo_host)
        self.db = self.client[self.mongo_db]


    def process_item(self, item, spider):
        self.db[self.collection_name].update({'slug':item['slug']},{'$setOnInsert':item},upsert=True)
        return item

    @classmethod
    def from_crawler(cls,crawler):
        host = crawler.settings.get('MONGO_HOST')
        db = crawler.settings.get('MONGO_DATABASE')
        return cls(host,db)


