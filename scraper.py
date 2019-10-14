import logging
import ssl
from urllib.request import urlopen
from time import time
import re

from bs4 import BeautifulSoup

import graph

logging.getLogger().setLevel(logging.DEBUG)
ssl._create_default_https_context = ssl._create_unverified_context

# Define wiki
wiki_start = "https://en.wikipedia.org/wiki/Johnny_Depp"
wiki = "https://en.wikipedia.org"


# Get Actor's Age
def findAge(cursor):
    logging.info("Find actor\'s age")
    if not cursor:
        logging.warning("The cursor passed in is null")
        return
    cursor = cursor.find("table", {"class": "infobox biography vcard"})
    if cursor:
        for tr in cursor.find_all("tr"):
            if tr.find_all(string=re.compile("Born")):
                birthday = tr.find("span", {"class": "bday"})
                if birthday:
                    return int(re.findall('\d{4}', birthday.text)[0])
        logging.warning("Fail to find the age")


def findName(cursor):  # Get Actor's Name
    logging.info('Find actor\'s name')
    if not cursor:
        logging.warning("The cursor passed in is null")
        return
    cursor = cursor.find("h1", {"id": "firstHeading"})
    if cursor:
        return cursor.text.strip()


def findCasts(cursor):  # Find which actors worked in a movie
    logging.info("Find which actors worked in a movie")
    if not cursor:
        logging.warning("The cursor passed in is null")
        return
    result = cursor.find("div", {"class": "div-col columns column-width"})
    if not result:
        result = cursor.find("table", {"class": "infobox vevent"})
        if result:
            for r in result.find_all("tr"):
                if r.find_all(string=re.compile("Starring")):
                    output = []
                    for actor in r.find_all("a"):
                        output += [
                            [str(actor["title"]).replace(" (actor)", ""), str(actor["href"]).replace(" (actor)", "")]]
                    return output
        logging.warning("No cast list found")
        return
    return getDataFromList(result)


def findMovies(cursor):  # Find which movies actor has worked in
    logging.info("Find which movies actor has worked in")
    if not cursor:
        logging.warning("The cursor passed in is null")
        return
    # Work on actor biography page
    result = cursor.find("div", {"class": "div-col columns column-width"})
    if result:
        return getDataFromList(result)
    else:
        # Work on actor filmography page
        movie_list = []
        try:
            result = cursor.find("table", {"class": "wikitable sortable"}).find("tbody")
            result = result.find_all("tr")
        except:
            return movie_list
        if result:
            for tr in result:
                tds = tr.find_all("td")
                if tds and tds[0].text != "TBA":
                    for td in tds:
                        tag_i = td.find("i")
                        if tag_i:
                            tag_a = tag_i.find("a")
                            if tag_a:
                                movie_list += [[tag_a["title"], tag_a["href"]]]
        return movie_list
    return []


def findGross(cursor):  # Find how much a movie has grossed
    logging.info("Find how much a movie has grossed")
    if not cursor:
        logging.warning("The cursor passed in is null")
        return
    cursor = cursor.find("table", {"class": "infobox vevent"})
    if not cursor:
        logging.warning("No gross information found")
        return
    tr = cursor.find("tbody").find_all("tr")
    for td in tr:
        if td.text[:7] == "Box off":
            try:
                return int(re.findall('\d+', td.text)[0])
            except:
                logging.warning("No gross information found")


def findYear(cursor):  # Find what year is a movie released
    logging.info("Find what year is a movie released")
    if not cursor:
        logging.warning("The cursor passed in is null")
        return
    cursor = cursor.find("table", {"class": "infobox vevent"})
    if not cursor:
        logging.warning("No year information found")
        return
    tr = cursor.find("tbody").find_all("tr")
    for td in tr:
        if "Release date" in td.text:
            return int(re.findall('\d{4}', td.text)[0])


# helper functions
def getSoup(url):
    try:
        page = urlopen(url).read()
        return BeautifulSoup(page, "html.parser")
    except:
        logging.warning("Website not found")


def getDataFromList(cursor):
    metadata = []
    try:
        data_list = cursor.find_all("li")
        for data in data_list:
            data = data.find("a")
            if data and data.text and data["href"]:
                metadata += [[data.text.strip(), data["href"]]]
    except:
        logging.warning("Data missing from the list")
    return metadata

def main():
    curr_time = int(time())
    g = graph.Graph()
    cursor = getSoup(wiki_start)
    movies = g.add("Michael Caine", "Actor", cursor)
    i = 0
    while g.movie_count <= 125 or g.actor_count <= 250:
        i += 1
        movie = movies.pop(0)
        actors = g.add(movie[0], "Movie", None, movie)
        logging.info("[{}] adding new movie".format(i))
        if actors:
            for actor in actors:
                if g.actor_count > 250:
                    break
                g.add(actor[0], "Actor", getSoup(wiki + actor[1]), movie, False)
    g.writeJson("data.json")
    logging.debug(graph)
    logging.debug("Passed " + str(int(time() - curr_time)) + " seconds")

if __name__ == "__main__":
    main()
