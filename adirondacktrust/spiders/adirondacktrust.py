import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from adirondacktrust.items import Article


class AdirondacktrustSpider(scrapy.Spider):
    name = 'adirondacktrust'
    start_urls = ['https://www.adirondacktrust.com/about/news/']

    def parse(self, response):
        articles = response.xpath('//table//tbody/tr')
        for article in articles:
            link = article.xpath('./td[2]/a/@href').get()
            date = article.xpath('./td[1]/text()').get()
            if date:
                date = date.strip()

            yield response.follow(link, self.parse_article, cb_kwargs=dict(date=date))

    def parse_article(self, response, date):
        if 'pdf' in response.url:
            return

        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//h2/text()').get()
        if title:
            title = title.strip()

        content = response.xpath('//div[@class="entry-content"]//text()').getall()
        content = [text for text in content if text.strip()]
        content = "\n".join(content).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
