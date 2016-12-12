# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
try:
    from Queue import Queue
except ImportError:
    from queue import Queue

WebCrawlerPipelineItems = Queue() #module-level thread-safe FIFO publication queue
class WebCrawlerQueuePipeline(object):
    def process_item(self, item, spider):
        WebCrawlerPipelineItems.put(item)
        return item
