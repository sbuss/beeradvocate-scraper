# BeerAdvocate scraper

Scrape (most of) the beers from BeerAdvocate. Includes the following data:

* style
* style_id
* name
* beer_id
* brewery
* brewery_id
* abv
* rAvg
* pDev
* num_reviews
* timestamp

# Scraping Beers

```python
scrapy crawl beeradvocate_brewery -o beers.json
```

Note that this crawl will take about an hour, assuming several threads are
being used.

# Spiders

This includes two spiders:

1. BeerAdvocateBrewerySpider
2. BeerAdvocateSpider

## BeerAdvocateBrewerySpider

This spider crawls the list of [breweries by country](http://beeradvocate.com/beerfly/directory)
and indexes all of their beers. This is a much more complete list that the
beers found by crawling the beers-by-style list.

## BeerAdvocateSpider

This spider crawls the list of beers accessible by the
[beer styles](http://beeradvocate.com/beer/style) page. This only returns about
4000 beers, far shy of the 90,000+ beers that BA tracks.
