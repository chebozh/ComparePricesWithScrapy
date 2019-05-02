# -*- coding: utf-8 -*-
import json
import re

import scrapy
from scrapy.loader import ItemLoader

from ..items import ProductItem


class DeichmanSpider(scrapy.Spider):
    name = 'deichman'
    store_url = 'www.deichmann.com'

    def start_requests(self):
        url = 'https://www.deichmann.com/ES/es/shop/search.html?q='

        # handle up to 4 search terms / keywords
        kw1 = getattr(self, 'kw1', None)
        kw2 = getattr(self, 'kw2', None)
        kw3 = getattr(self, 'kw3', None)
        kw4 = getattr(self, 'kw4', None)

        if kw1:
            url = url + kw1
        if kw2:
            url = url + ' ' + kw2
        if kw3:
            url = url + ' ' + kw3
        if kw4:
            url = url + ' ' + kw4

        yield scrapy.Request(url, self.parse)

    def parse(self, response):
        """Method to parse search result product listing page."""
        for product in response.css('div.product-item'):
            name = product.css('a.product-seolink::attr(data-producttileinfo)').get()
            relative_url = product.css('a.product-seolink::attr(href)').get()
            url = f'https://www.deichmann.com{relative_url}'
            brand_search_term = getattr(self, "kw1", None)

            # getting a couple of unwanted Puma results when looking for adidas
            if brand_search_term != 'puma' and 'puma' not in name.lower():
                loader = ItemLoader(item=ProductItem(), response=response)
                loader.add_value('name', name.lower(), re=f'\d* {brand_search_term} (.*)')

                # prepare request for product page
                product_page_request = scrapy.Request(
                    url=url,
                    callback=self.parse_product
                )
                product_page_request.meta['item'] = loader.load_item()
                yield product_page_request

        # navigate pagination
        next_page_link_selector = response.css('div.PAGINGUP_DOWN:nth-child(3) > ul:nth-child(1) > li:nth-child(3) > '
                                               'a:nth-child(1)::attr(href)')
        if next_page_link_selector:
            next_page_link = next_page_link_selector.get()
            yield scrapy.Request(url=response.urljoin(next_page_link))

    def parse_product(self, response):
        """Method to parse an individual product page"""
        loader = ItemLoader(item=response.meta['item'], response=response)
        price = response.xpath('//*[@itemprop="price"]/text()').get()
        loader.add_value('price', price)

        product_id = re.search('es/shop/(\d*)/', response.request.url).group(1)
        json_api_url = f'https://www.deichmann.com/ES/es/shop/ws/restapi/v1/product/{product_id}?' \
                       f'property=variants'
        product_sizes_request = scrapy.Request(
            url=json_api_url,
            callback=self.parse_available_sizes
        )
        product_sizes_request.meta['item'] = loader.load_item()
        product_sizes_request.meta['url_to_set'] = response.request.url

        yield product_sizes_request

    def parse_available_sizes(self, response):
        """Method to parse JSON response containing item available sizes"""
        loader = ItemLoader(item=response.meta['item'], response=response)
        json_data = json.loads(response.text)
        variants = json_data.get('variants', None)
        sizes = []

        if variants:
            for variant in variants:
                sizes.append(variant['size']['value'])

        loader.add_value('sizes', sizes)
        loader.add_value('store_url', self.store_url)
        loader.add_value('item_url', response.meta['url_to_set'])

        yield loader.load_item()
