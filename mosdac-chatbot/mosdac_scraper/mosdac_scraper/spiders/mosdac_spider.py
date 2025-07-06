# mosdac_scraper/spiders/mosdac_spider.py
import scrapy
from urllib.parse import urljoin, urldefrag
from mosdac_scraper.items import MosItem
import re

class MosdacSpider(scrapy.Spider):
    name = "mosdac"
    allowed_domains = ["mosdac.gov.in"]
    start_urls = ["https://www.mosdac.gov.in/"]
    visited_urls = set()

    def parse(self, response):
        canonical_url = response.url.split("#")[0]
        if canonical_url in self.visited_urls:
            return
        self.visited_urls.add(canonical_url)

        item = MosItem()
        item["url"] = canonical_url
        item["breadcrumbs"] = response.css('.breadcrumb *::text').getall()
        item["title"] = response.css('title::text, h1::text').get()
        item["headings"] = response.css('h2::text, h3::text').getall()
        item["description"] = response.css('p::text').getall()

        # All file types to download
        file_selectors = 'a[href$=".pdf"], a[href$=".xls"], a[href$=".xlsx"], a[href$=".doc"], a[href$=".docx"], a[href$=".zip"], a[href$=".csv"]'
        raw_file_links = response.css(file_selectors + '::attr(href)').getall()
        item["file_urls"] = [urljoin(response.url, link) for link in raw_file_links]

        # All image links
        raw_image_links = response.css('img::attr(src)').getall()
        item["image_urls"] = [urljoin(response.url, src) for src in raw_image_links]

        yield item

        # Follow all internal links (ignoring anchors, mailto, tel, js)
        links = response.css('a::attr(href)').getall()
        for href in links:
            href = urldefrag(href)[0]  # Remove #fragment
            if (
                href
                and not href.startswith("mailto:")
                and not href.startswith("tel:")
                and not href.startswith("javascript:")
            ):
                full_url = urljoin(response.url, href)
                if self.allowed_domains[0] in full_url:
                    yield response.follow(full_url, callback=self.parse)
