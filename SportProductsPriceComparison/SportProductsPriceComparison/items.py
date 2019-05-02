# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import re

from scrapy.item import Item, Field
from scrapy.loader.processors import TakeFirst, MapCompose


class ProductItem(Item):
    name = Field(output_processor=TakeFirst())
    price = Field(
        input_processor=MapCompose(
            lambda x: x.replace(',', '.'),
            lambda x: x.replace('€', ''),
            float
        ),
        output_processor=TakeFirst()
    )
    sizes = Field(input_processor=MapCompose(
        lambda x: re.search(r'(\d{2})(\(\d+)?', x).group(1),
        int
    ))
    store_url = Field(output_processor=TakeFirst())
    item_url = Field(output_processor=TakeFirst())
