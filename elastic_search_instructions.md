# Run elasticsearch

```sh
cd elasticsearch
bin/elasticsearch -f
```

# Create an index

```sh
curl -XPUT localhost:9200/beeradvocate -d @elastic_search_schema.json
```

# Put the beer in 
```sh
# Edit beers.json to have properly formatted timestamps (they're missing the 'T')

while read $beer; do
  curl -XPOST localhost:9200/beeradvocate/beer -d "$beer"
done < beers.json
```

Known issue: unicode is not handled correctly

# To verify mapping:

```sh
curl -XGET localhost:9200/_mapping?pretty=1
```

# Sample searches:

```sh
curl -XGET "localhost:9200/beeradvocate/beer/_search?pretty=1&q=_all:pliny+elder"
curl -XGET "localhost:9200/beeradvocate/beer/_search?pretty=1&q=_all:samuel+adams+octoberfest"
curl -XGET "localhost:9200/beeradvocate/beer/_search?pretty=1&q=_all:octoberfest+samuel+adams"  # Fails!
```
