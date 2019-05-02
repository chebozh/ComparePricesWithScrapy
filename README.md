# ComparePricesWithScrapy
Simple scrapers made with Scrapy to scrape sports products details from two websites I like - deporvillage.com and deichman.com

The scrapers support up to 4 search key words (kw's). 

Example of how to run the scrapers.
To scrape deichman.com with example search terms, run

```
scrapy crawl deichman -a kw1=nike -a kw2=air -o deichman_nike_air_output.jl

```

To scrape deporvillage.com with example search terms run
```
scrapy crawl deporvillage -a kw1=nike -a kw2=air -o deporvillage_nike_air_output.jl 
```
