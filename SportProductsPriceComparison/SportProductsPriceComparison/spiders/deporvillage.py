# -*- coding: utf-8 -*-
import scrapy
from scrapy.loader import ItemLoader

from ..items import ProductItem


class DeporvillageSpider(scrapy.Spider):
    name = 'deporvillage'
    store_url = 'www.deporvillage.com'

    def start_requests(self):
        url = 'https://www.deporvillage.com/catalogsearch/result/?q='

        # handle up to 4 search terms / keywords
        kw1 = getattr(self, 'kw1', None)
        kw2 = getattr(self, 'kw2', None)
        kw3 = getattr(self, 'kw3', None)
        kw4 = getattr(self, 'kw4', None)

        if kw1:
            url = url + kw1
        if kw2:
            url = url + '+' + kw2
        if kw3:
            url = url + '+' + kw3
        if kw4:
            url = url + '+' + kw4

        yield scrapy.Request(url, self.parse)

    def parse(self, response):
        """Method to parse most Item field values from product listing page."""
        products = response.css('li.item')

        for product in products:
            # get the ProductItem field values
            name = product.css('img.lazy::attr(alt)').get()
            price = product.css('span.price::text').get()
            relative_url = product.css('a.product-image::attr(href)').get()
            url = f'https://www.deporvillage.com{relative_url}'

            # looking for adult-size shoes only
            if 'infantil' not in name.lower():
                # Load the field values
                loader = ItemLoader(item=ProductItem(), response=response)
                loader.add_value('name', name)
                loader.add_value('price', price)

                # prepare request for product page
                product_page_request = scrapy.Request(
                    url=url,
                    callback=self.parse_product
                )
                product_page_request.meta['item'] = loader.load_item()

                yield product_page_request

    def parse_product(self, response):
        """Method to request specific (detailed) product description page.

        Used to get the available sizes of a running shoe and the page url.
        """
        loader = ItemLoader(item=response.meta['item'], response=response)
        available_sizes = response.css('li.size_option a.opt::text').getall()
        loader.add_value('sizes', available_sizes)
        loader.add_value('store_url', self.store_url)
        loader.add_value('item_url', response.request.url)

        yield loader.load_item()
