import argparse

from graph import *

# Use -h for help message
if __name__ == "__main__":
    graph = Graph()
    graph.readJson("data.json")
    parser = argparse.ArgumentParser(description="Query the graph following the below rules.")
    parser.add_argument("-1", metavar='{movie_name}', help="Find how much a movie has grossed", nargs='+')
    parser.add_argument("-2", metavar='{actor_name}', help="List which movies an actor has worked in", nargs='+')
    parser.add_argument("-3", metavar='{movie_name}', help="List which actors worked in a movie", nargs='+')
    parser.add_argument("-4", metavar='{number}', help="List the top X actors with the most total grossing value")
    parser.add_argument("-5", metavar='{number}', help="List the oldest X actors")
    parser.add_argument("-6", metavar='{year}', help="List all the movies for a given year")
    parser.add_argument("-7", metavar='{year}', help="List all the actors for a given year")
    parser.add_argument("-8", metavar='{number}', help="Find top X movies of the most grossing value")
    parser.add_argument("-9", action='store_true', help="Find hub actors")
    parser.add_argument("-10", action='store_true', help="Find the correlation between age and grossing value")
    parser.add_argument("-11", action='store_true',
                        help="(Custom) Find the average box office of movies with respect to the "
                             "progress of time")
    parser.add_argument("-v", metavar='{N}',
                        help="Data visualization for n movies with corresponding actors")

    arg = parser.parse_args().__dict__
    for choice in arg:
        if arg[choice]:
            if type(arg[choice]) == list:
                arg[choice] = ' '.join(arg[choice])
            result = None
            if choice == "1":
                result = graph.getMovieGross(arg[choice])
            elif choice == "2" or choice == "3":
                result = graph.getEdges(arg[choice])
            elif choice == "4":
                result = graph.getTopGross(int(arg[choice]), "Actor")
            elif choice == "5":
                result = graph.getOldestX(int(arg[choice]))
            elif choice == "6":
                result = graph.getSameYear(int(arg[choice]), "Movie")
            elif choice == "7":
                result = graph.getSameYear(int(arg[choice]), "Actor")
            elif choice == "8":
                result = graph.getTopGross(int(arg[choice]), "Movie")
            elif choice == "9":
                result = graph.getHubActors()
            elif choice == "10":
                result = graph.getAgeGross()
            elif choice == "11":
                result = graph.getMovieGrossYear()
            elif choice == "v":
                result = graph.visualize(int(arg[choice]))
            if result:
                print("Result: " + str(result))
            else:
                print("result not found")
