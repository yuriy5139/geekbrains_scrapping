import scrapy
from scrapy.http import HtmlResponse
from bookparser.items import BookparserItem


class LabirintruSpider(scrapy.Spider):
    name = 'labirintru'
    allowed_domains = ['labirint.ru']
    start_urls = ['https://www.labirint.ru/search/%D0%B4%D0%B5%D1%82%D0%B5%D0%BA%D1%82%D0%B8%D0%B2%D1%8B/?stype=0']

    def parse(self, response: HtmlResponse):
        next_page = response.xpath("//a[@title='Следующая']/@href").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

        links = response.xpath("//a[@class='product-title-link']/@href").getall()
        for link in links:
            yield response.follow(link, callback=self.book_parse)

    def book_parse(self, response: HtmlResponse):
        url = response.url
        name = response.xpath("//h1/text()").get()
        author = response.xpath("//a[@data-event-label='author']/text()").get()
        price = response.xpath("//span[@class='buying-price-val-number']/text()").get()
        disc_price = response.xpath("//span[@class='buying-pricenew-val-number']/text()").get()
        rating = response.xpath("//div[@id='rate']/text()").get()

        yield BookparserItem(url=url, name=name, author=author, price=price, disc_price=disc_price, rating=rating)
