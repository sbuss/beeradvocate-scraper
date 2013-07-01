from scrapy.spider import BaseSpider
from scrapy.http import Request
from scrapy.selector import HtmlXPathSelector
from scrapy import log

from beeradvocate.settings import BASE_URL
from beeradvocate.spiders.mixins import BeerDetailPageParserMixin


class BeerAdvocateBrewerySpider(BaseSpider, BeerDetailPageParserMixin):
    name = "beeradvocate_brewery"
    allowed_domains = ["beeradvocate.com", "www.beeradvocate.com"]
    start_urls = [
        "http://beeradvocate.com/beerfly/directory?show=all"
    ]

    def parse(self, response):
        return self.parse_country_list(response)

    def parse_country_list(self, response):
        self.log("Got country list %s" % response.url, level=log.INFO)
        hxs = HtmlXPathSelector(response)
        countries = hxs.select('//*[@id="baContent"]/table/tr[2]/td/table')
        country_urls = countries.select('tr/td[2]/li/a/@href').extract()
        for country_url in country_urls:
            url = ("http://beeradvocate.com/beerfly/list?c_id=%s"
                   "&s_id=0&brewery=Y") % country_url.split('/')[-1]
            yield Request(url=url, callback=self.parse_country_details)

    def parse_country_details(self, response):
        self.log("Got country details %s" % response.url, level=log.INFO)
        hxs = HtmlXPathSelector(response)
        brewery_table = hxs.select('//*[@id="baContent"]/table')

        nav_links = brewery_table.select('tr[2]/td/a')
        next_url = None
        for link in nav_links:
            if link.select('b[contains(text(), "next")]'):
                next_url = BASE_URL + link.select('@href').extract()[0]
                break

        breweries = brewery_table.select(
            'tr/td/a[contains(@href, "/beer/profile")]')
        for brewery in breweries:
            url = BASE_URL + brewery.select('@href').extract()[0]
            url += "/?view=beers&show=all"
            yield Request(url=url, callback=self.parse_beer_list)

        if next_url:
            yield Request(url=next_url, callback=self.parse_country_details)

    def parse_beer_list(self, response):
        self.log("Got beer list %s" % response.url, level=log.INFO)
        hxs = HtmlXPathSelector(response)
        beer_table = hxs.select('//*[@id="baContent"]/table[2]/tr[1]/td/table')
        beer_urls = beer_table.select(
            'tr/td/a[contains(@href, "/beer/profile/")]')
        for beer_url in beer_urls:
            url = BASE_URL + beer_url.select('@href').extract()[0]
            yield Request(url=url, callback=self.parse_beer_detail)
