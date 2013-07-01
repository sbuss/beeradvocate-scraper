# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/topics/items.html

from scrapy.item import Item, Field

from beeradvocate.settings import BASE_URL


class BeerAdvocateItem(Item):
    style = Field()
    style_id = Field()
    name = Field()
    beer_id = Field()
    brewery = Field()
    brewery_id = Field()
    abv = Field()
    rAvg = Field()
    pDev = Field()
    num_reviews = Field()
    timestamp = Field()

    def get_url(self):
        return self.get_brewery_url() + "/%s" % self.beer_id

    def get_brewery_url(self):
        return BASE_URL + "/beer/profile/%s" % self.brewery_id

    def get_style_url(self):
        return BASE_URL + "/beer/style/%s" % self.style_id
