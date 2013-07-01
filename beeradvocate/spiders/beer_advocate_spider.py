#!/usr/bin/env python
# encoding=utf-8
from datetime import datetime
from decimal import Decimal
import re

from scrapy.spider import BaseSpider
from scrapy.http import Request
from scrapy.selector import HtmlXPathSelector
from scrapy import log

from beeradvocate.settings import BASE_URL
from beeradvocate.items import BeerAdvocateItem


class BeerAdvocateSpider(BaseSpider):
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

    def parse_beer_detail(self, response):
        self.log("Got beer detail for %s" % response.url)
        hxs = HtmlXPathSelector(response)
        item = BeerAdvocateItem()

        ids = re.findall(r'profile/(?P<brewery_id>\d+)/(?P<beer_id>\d+)',
                         response.url)[0]
        item['brewery_id'] = ids[0]
        item['beer_id'] = ids[1]

        beer_name = hxs.select(
            '//*[@id="content"]/div/div/div/div/div[2]/h1/text()').extract()[0]
        item['name'] = beer_name

        details = hxs.select(
            '//*[@id="baContent"]/table[1]/tr/td[2]/table/tr[2]/td').\
            extract()[0]
        brewery = re.findall(
            r'href="/beer/profile/%s"><b>([^<]+)' % item['brewery_id'],
            details)[0]
        item['brewery'] = brewery
        style = re.findall(
            r'href="/beer/style/(\d+)"><b>([^<]+)',
            details)[0]
        item['style_id'] = style[0]
        item['style'] = style[1]
        abv = re.findall(r'([0-9.]+)% <a href="/articles/518">ABV</a>',
                         details)
        if abv:
            item['abv'] = Decimal(abv[0])

        ratings_cell = hxs.select(
            '//*[@id="baContent"]/table[1]/tr/td[2]/table/tr[1]/td/table/'
            'tr/td[3]').extract()[0]
        rAvg = re.findall(r'rAvg: ([0-9.]+)', ratings_cell)[0]
        pDev = re.findall(r'pDev: ([0-9.]+)%', ratings_cell)[0]
        num_reviews = re.findall(r'Reviews: (\d+)', ratings_cell)[0]
        item['rAvg'] = Decimal(rAvg)
        item['pDev'] = Decimal(pDev)
        item['num_reviews'] = Decimal(num_reviews)

        item['timestamp'] = datetime.utcnow()

        return item
