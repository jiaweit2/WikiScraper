import logging
import json
import re
import matplotlib.pyplot as plt
import networkx as nx
from datetime import datetime
from collections import defaultdict
import scraper


# Can be actor or movie
class Node(object):
    def __init__(self, name, json_class):
        self.name = name
        self.json_class = json_class
        self.edges = {}
        self.year = 0
        self.gross = 0
        self.wiki_page = ""


class Graph(object):
    # Constructor of the graph
    def __init__(self):
        self.map = {}
        self.movie_count = 0
        self.actor_count = 0

    def add(self, name, json_class, cursor, movie_data=None, find_more=True):
        if name in self.map:
            logging.warning("Node already exist")
            return
        if not cursor and not movie_data:
            logging.warning("Cursor passed in is null")
            return
        node = Node(name, json_class)
        if json_class == "Movie":
            self.movie_count += 1
            casts = None
            if movie_data:
                node.gross = movie_data[2]
                node.year = movie_data[3]
                casts = movie_data[4]
            self.map[name] = node.__dict__
            if casts and len(casts) > 0:
                casts = casts[::-1]
                for i in range(len(casts)):  # Give weights according to the cast list
                    node.edges[casts[i][0]] = i
                self.map[name] = node.__dict__
                return casts
            else:
                logging.warning("No casts found for this movie")
                return
        else:
            self.actor_count += 1
            node.year = scraper.findAge(cursor)
            if movie_data:
                node.gross = movie_data[2]
                node.edges[movie_data[0]] = movie_data[2]
            self.map[name] = node.__dict__
            if not find_more:
                return
            total_gross = node.gross
            movies = scraper.findMovies(cursor)
            if movies and len(movies) > 0:
                for i in range(len(movies)):  # Give weights according to the grossing
                    if movies[i][1]:
                        movie_cursor = scraper.getSoup(scraper.wiki + movies[i][1])
                        gross = scraper.findGross(movie_cursor)
                        if not gross:
                            gross = 0
                        total_gross += gross
                        movies[i] += [gross]
                        movies[i] += [scraper.findYear(movie_cursor)]
                        movies[i] += [scraper.findCasts(movie_cursor)]
                    node.edges[movies[i][0]] = gross
                node.gross = total_gross
                self.map[name] = node.__dict__
                return movies
            else:
                logging.warning("No movies found for this actor")
                return

    # Write JSON to file
    def writeJson(self, filename):
        logging.info("Write json data to file")
        output = []
        with open(filename, 'w+') as f:
            for x in self.map:
                output += [self.map[x]]
            json.dump(output, f)

    # Load a JSON object from file
    def readJson(self, filename):
        with open(filename, 'r') as f:
            data = json.load(f)
        try:  # try format 1
            for m in data:
                for node in m:
                    node = m[node]
                    node_new = Node(node["name"], node["json_class"])
                    if node["json_class"] == "Actor":
                        node_new.year = datetime.now().year - node["age"]
                        node_new.gross = node["total_gross"]
                        node_new.edges = node["movies"]
                        self.actor_count += 1
                    else:
                        node_new.year = node["year"]
                        node_new.gross = node["box_office"]
                        node_new.edges = node["actors"]
                        node_new.wiki_page = node["wiki_page"]
                        self.movie_count += 1
                    self.map[node["name"]] = node_new
        except:
            for node in data:
                self.map[node["name"]] = node
                if node["json_class"] == "Actor":
                    self.actor_count += 1
                else:
                    self.movie_count += 1

    def getOldestX(self, x):  # List the X oldest
        filtered = []
        for name in self.map:
            if self.map[name]["json_class"] == "Actor" and self.map[name]["year"] and self.map[name]["year"] > 0:
                filtered += [[name, self.map[name]["year"]]]
                sorted(filtered, key=lambda i: i[1])
        return [a[0] for a in filtered[:x]]

    # List the top X gross
    def getTopGross(self, x, type_data):
        filtered = []
        for name in self.map:
            if self.map[name]["json_class"] == type_data:
                filtered += [[name, self.map[name]["gross"]]]
        sorted(filtered, key=lambda i: i[1])
        return [a[0] for a in filtered[-x:]]

    # List which movies an actor has worked in or
    # list which actors worked in a movie
    def getEdges(self, node_name):
        for name in self.map:
            if node_name == re.sub(r'.\(.*\)', '', name):
                return list(self.map[name]["edges"].keys())

    # Find how much a movie has grossed
    def getMovieGross(self, movie):
        for name in self.map:
            if movie == re.sub(r'.\(.*\)', '', name):
                try:
                    return self.map[name]["gross"]
                except:
                    return self.map[name].gross

    # Find all the nodes for a given year
    def getSameYear(self, year, json_class):
        nodes = []
        for name in self.map:
            if self.map[name]["json_class"] == json_class and self.map[name]["year"] == year:
                nodes += [name]
        return nodes

    # Find the "hub" actors in the dataset
    def getHubActors(self):
        m = defaultdict(set)
        for movie in self.map:
            if self.map[movie].json_class == "Movie":
                actors = self.map[movie].edges
                for actor in actors:
                    for other_actor in actors:
                        if other_actor != actor:
                            m[actor].add(other_actor)
        hub_actors = sorted(m.items(), key=lambda x: len(x[1]))[-5::][::-1]
        indices = [x[0] for x in hub_actors]
        counts = [len(x[1]) for x in hub_actors]
        plt.bar(indices, counts)
        plt.xlabel("Actor")
        plt.ylabel("Amount of Connections")
        plt.tight_layout()
        plt.show()
        return "result shown as plot"

    # Find the age group that generates the most amount of money
    def getAgeGross(self):
        m = defaultdict(int)
        for actor in self.map:
            if self.map[actor].json_class == "Actor":
                age = datetime.now().year - self.map[actor].year
                if age > 0:
                    age_group = int(age / 10)
                    m[age_group] += self.map[actor].gross
        m = sorted(m.items(), key=lambda x: x[0])
        indices = [str(x[0] * 10) for x in m]
        counts = [x[1] for x in m]
        plt.bar(indices, counts)
        plt.xlabel("Age Group")
        plt.ylabel("Gross Income")
        plt.show()
        return "result shown as plot"

    # Find the box office of movies on average with respect to the progress of time
    def getMovieGrossYear(self):
        m = defaultdict(int)
        m_count = defaultdict(int)
        for movie in self.map:
            if self.map[movie].json_class == "Movie":
                if self.map[movie].year > 1700:
                    year_group = int(self.map[movie].year / 10)
                    m[year_group] += self.map[movie].gross
                    m_count[year_group] += 1
        m = sorted(m.items(), key=lambda x: x[0])
        indices = [str(x[0] * 10) + 's' for x in m]
        box_office = [int(x[1] / m_count[x[0]]) for x in m]
        plt.bar(indices, box_office)
        plt.xlabel("Year")
        plt.ylabel("Average Box Office Per Movie")
        plt.show()
        return "result shown as plot"

    def visualize(self, n):
        movies = {}
        actors = {}
        edges = []
        # Add part of movies and actors
        for name in self.map:
            if len(movies) >= n:
                break
            if self.map[name].json_class == "Movie":
                movies[name] = self.map[name]
                for actor in self.map[name].edges:
                    if actor not in self.map:
                        continue
                    actors[actor] = self.map[actor]
                    edges += [(name, actor)]
        # Create graph and nodes
        color_map = {'Movie': '#FFDD33', 'Actor': '#FFAABB'}
        g = nx.Graph()
        g.add_nodes_from(actors, type='actor')
        g.add_nodes_from(movies, type='movie')
        g.add_edges_from(edges)
        plt.figure()
        pos = nx.spring_layout(g, k=10, iterations=20)
        nx.draw(g, pos=pos, node_color=[color_map[self.map[node].json_class] for node in g], with_labels=True,
                font_size=8, node_size=500)

        # Display attributes
        pos_attrs = {}
        for node, coords in pos.items():
            pos_attrs[node] = (coords[0], coords[1] - 0.04)

        attrs = {}
        for name in movies:
            attrs[name] = "box_office: " + str(movies[name].gross)
        for name in actors:
            attrs[name] = "age: " + (str(datetime.now().year - actors[name].year) if name in actors else '0')

        nx.draw_networkx_labels(g, pos_attrs, labels=attrs, font_size=6)

        x_values, y_values = zip(*pos.values())
        x_margin = (max(x_values) - min(x_values)) * 0.15
        plt.xlim(min(x_values) - x_margin, max(x_values) + x_margin)
        y_margin = (max(y_values) - min(y_values)) * 0.15
        plt.ylim(min(y_values) - y_margin, max(y_values) + y_margin)
        plt.show()
        return "result shown as graph"

    # Printing format
    def __repr__(self):
        return "Movies count: " + str(self.movie_count) + "\n" + "Actors count: " + str(self.actor_count) + "\n"

# if __name__ == "__main__":
#     graph = Graph()
#     graph.readJson('data.json')
# print(graph.getHubActors())
# print(graph.getAgeGross())
# print(graph.getMovieGrossYear())
# graph.visualize(10)
