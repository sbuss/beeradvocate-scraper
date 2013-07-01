#!/usr/bin/env python
# encoding=utf-8
import re

from scrapy.spider import BaseSpider
from scrapy.http import Request
from scrapy.selector import HtmlXPathSelector
from scrapy import log

from beeradvocate.settings import BASE_URL
from beeradvocate.spiders.mixins import BeerDetailPageParserMixin


class BeerAdvocateSpider(BaseSpider, BeerDetailPageParserMixin):
    name = "beeradvocate"
    allowed_domains = ["beeradvocate.com", "www.beeradvocate.com"]
    start_urls = [
        "http://beeradvocate.com/beer/style"
    ]

    def parse(self, response):
        return self.parse_beer_styles(response)

    def parse_beer_styles(self, response):
        self.log("Got beer style list.", level=log.INFO)
        hxs = HtmlXPathSelector(response)
        style_columns = hxs.select('//*[@id="baContent"]/table/tr[1]/td')
        if not style_columns:
            self.log("Failed to get styles", level=log.ERROR)
            return
        for column in style_columns:
            beers = column.select('table/tr[2]')
            if not beers:
                self.log("Failed to find beers field", level=log.ERROR)
            for match in re.finditer(
                    r'href="(/beer/style/\d+)">([^<]+)', beers.extract()[0]):
                yield Request(url=BASE_URL + match.groups()[0],
                              callback=self.parse_beer_list)

    def parse_beer_list_for_brewery(self, response):
        hxs = HtmlXPathSelector(response)
        beer_list_table = hxs.select('//*[@id="baContent"]/table[2]')
        beer_rows = beer_list_table.select(
            '/tr[1]/td/table/tr[position() >= 3]')
        for row in beer_rows:
            name, style, abv, rAvg, num_reviews = \
                row.select('td').extract()[1:]

    def parse_beer_list(self, response):
        self.log("Got beer list for %s" % response.url)
        hxs = HtmlXPathSelector(response)
        beer_list_table = hxs.select('//*[@id="baContent"]/table[2]')
        nav_links = beer_list_table.select('tr[2]/td/a').extract()[::-1]
        next_url = None
        for link in nav_links:
            if 'next' in link:
                next_urls = re.findall(r'href="(/beer/style/\d+/?start=\d+)"',
                                       link)
                if next_urls:
                    next_url = next_urls[0]
                break

        # SUCKS - there should be 50 beers per page, and they should start
        # at the 4th row, so hardcode this stupid thing
        beer_rows = beer_list_table.select('tr[4 <= position()]')
        for beer_row in beer_rows:
            try:
                beer_link = re.findall(r'href="(/beer/profile/\d+/\d+)"',
                                       beer_row.extract())[0]
                yield(Request(url=BASE_URL + beer_link,
                              callback=self.parse_beer_detail))
            except IndexError:
                pass

        # Query the next page last so we don't go depth-first on the beer list
        if next_url:
            yield(Request(url=BASE_URL + next_url,
                          callback=self.parse_beer_list))
