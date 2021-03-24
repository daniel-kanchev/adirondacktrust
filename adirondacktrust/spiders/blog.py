import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from adirondacktrust.items import Article


class BlogSpider(scrapy.Spider):
    name = 'blog'
    start_urls = ['https://www.adirondacktrust.com/blog/']

    def parse(self, response):
        links = response.xpath('//h1/a/@href').getall()
        yield from response.follow_all(links, self.parse_article)

        next_page = response.xpath('//span[@class="older-entries"]/a/@href').get()
        if next_page:
            yield response.follow(next_page, self.parse)

    def parse_article(self, response):
        if 'pdf' in response.url:
            return

        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//h1/text()').get()
        if title:
            title = title.strip()

        date = response.xpath('//span[@class="blog-post-date"]//text()').get()
        if date:
            date = date.strip()

        content = response.xpath('//div[@class="col-md-8 col-sm-8 personal-content bftn-blog-content single-blog"]/div[contains(@class, "blog-content")]//text()').getall()
        content = [text for text in content if text.strip()]
        content = "\n".join(content).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
