# mosdac_scraper/items.py
import scrapy

class MosItem(scrapy.Item):
    url = scrapy.Field()
    breadcrumbs = scrapy.Field()
    title = scrapy.Field()
    headings = scrapy.Field()
    description = scrapy.Field()
    file_urls = scrapy.Field()
    files = scrapy.Field()
    image_urls = scrapy.Field()
    images = scrapy.Field()
    pdf_text = scrapy.Field()
    file_metadata = scrapy.Field()
