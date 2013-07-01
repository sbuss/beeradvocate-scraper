from datetime import datetime
from decimal import Decimal
import re

from scrapy.selector import HtmlXPathSelector
from scrapy import log

from beeradvocate.items import BeerAdvocateItem


class BeerDetailPageParserMixin(object):
    def parse_beer_detail(self, response):
        self.log("Got beer detail for %s" % response.url, level=log.INFO)
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
