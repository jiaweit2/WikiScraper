# Wikipedia Movie/Actor Scraper
Scraping movies and actors metadata from wikipedia to local JSON file.
There are two ways to do queries on the data.<br>
First, you can run main.py which uses a graph class to query the scraped data. <br>
Second, you are provided a flask backend to serve API endpoints which allow you to query or modify the data.<br>

## Query data
See options for querying data using graph structure.
```
python3 main.py -h 
```
or run the flask backend to use the API to query or modify the data.
```
python3 webApi.py
```

## Scraper
data.json is provided but if you want to scrape your own data. You may modify the main function in scraper.py and run
```
python3 scraper.py
```
