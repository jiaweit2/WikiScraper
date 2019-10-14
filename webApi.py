from logging.config import dictConfig

from flask import *

# config code Source: https://flask.palletsprojects.com/en/1.0.x/logging/
dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    }},
    'handlers': {'wsgi': {
        'class': 'logging.StreamHandler',
        'stream': 'ext://flask.logging.wsgi_errors_stream',
        'formatter': 'default'
    }},
    'root': {
        'level': 'DEBUG',
        'handlers': ['wsgi']
    }
})

app = Flask(__name__)

with open('data.json') as f:
    input_data = json.load(f)


# actors: input_data[0]
# movies: input_data[1]

# http://localhost:5000/actors/Bruce_Willis
@app.route('/actors/<string:name>', methods=['DELETE'])
def delete_actor(name):
    app.logger.debug("Deleting actor: %s", name)
    try:
        name = ' '.join(name.split("_"))
        if name not in input_data[0]:
            raise Exception("Actor does not exist.")
        del input_data[0][name]
        with open("data.json", 'w') as f:
            json.dump(input_data, f, indent=4)

    except Exception as e:
        return 'Bad Request: ' + str(e), 400

    return 'OK', 200


# http://localhost:5000/movies/Twilight
@app.route('/movies/<string:name>', methods=['DELETE'])
def delete_movie(name):
    app.logger.debug("Deleting movie: %s", name)
    try:
        name = ' '.join(name.split("_"))
        if name not in input_data[1]:
            raise Exception("Movie does not exist.")
        del input_data[1][name]
        with open("data.json", 'w') as f:
            json.dump(input_data, f, indent=4)

    except Exception as e:
        return 'Bad Request: ' + str(e), 400

    return 'OK', 200


# http://localhost:5000/actors  {json}
@app.route('/actors', methods=['POST'])
def add_actor():
    app.logger.debug("Adding a new actor")
    data = request.get_json()
    try:
        name = data['name']
        name = ' '.join(name.split("_"))
        if name in input_data[0]:
            raise Exception("Actor already exists.")
    except Exception as e:
        return 'Bad Request: ' + str(e), 400
    input_data[0][name] = data
    with open("data.json", 'w') as f:
        json.dump(input_data, f, indent=5)
    return 'Created', 201


# http://localhost:5000/movies  {json}
@app.route('/movies', methods=['POST'])
def add_movie():
    app.logger.debug("Adding a new movie")
    data = request.get_json()
    try:
        name = data['name']
        name = ' '.join(name.split("_"))
        if name in input_data[1]:
            raise Exception("Movie already exists.")
    except Exception as e:
        return 'Bad Request: ' + str(e), 400
    input_data[1][name] = data
    with open("data.json", 'w') as f:
        json.dump(input_data, f, indent=5)
    return 'Created', 201


# http://localhost:5000/actors/Bruce_Willis  {json}
@app.route('/actors/<string:name>', methods=['PUT'])
def update_actor(name):
    app.logger.debug("Updating actor %s", name)
    try:
        name = ' '.join(name.split("_"))
        update(name, "ACTORS")
    except Exception as e:
        return 'Bad Request: ' + str(e), 400

    return 'OK', 200


# http://localhost:5000/movies/Twilight {json}
@app.route('/movies/<string:name>', methods=['PUT'])
def update_movie(name):
    app.logger.debug("Updating movie %s", name)
    try:
        name = ' '.join(name.split("_"))
        update(name, "MOVIES")
    except Exception as e:
        return 'Bad Request: ' + str(e), 400

    return 'OK', 200


def update(name, t):
    data = request.get_json()
    for key in data:
        if t == "ACTORS":
            if name not in input_data[0]:
                raise Exception("Actor not found.")
            input_data[0][name][key] = data[key]
        else:
            if name not in input_data[1]:
                raise Exception("Movie not found.")
            input_data[1][name][key] = data[key]
    with open("data.json", 'w') as f:
        json.dump(input_data, f, indent=4)


# http://localhost:5000/movies?year=1994&name=Twilight
@app.route('/movies', methods=['GET'])
def get_movie_by_attr():
    app.logger.debug("Getting movies by attributes")
    ret = []
    try:
        ret = parse_query(list(input_data[1].values()))
    except Exception as e:
        return 'Bad Request: ' + str(e), 400

    return jsonify(ret)


# http://localhost:5000/actors?age=94&gross=0
@app.route('/actors', methods=['GET'])
def get_actor_by_attr():
    app.logger.debug("Getting actors by attributes")
    ret = []
    try:
        ret = parse_query(list(input_data[0].values()))
    except Exception as e:
        return 'Bad Request: ' + str(e), 400

    return jsonify(ret)


# http://localhost:5000/movies/<Movie_Name>
@app.route('/movies/<string:name>', methods=['GET'])
def get_movie_by_name(name):
    app.logger.debug("Getting movie: %s", name)
    try:
        name = ' '.join(name.split("_"))
        ret = input_data[1][name]
    except:
        print(input_data[1])
        return 'Bad Request: cannot find the movie', 400

    return jsonify(ret)


# http://localhost:5000/actors/<Actor_Name>
@app.route('/actors/<string:name>', methods=['GET'])
def get_actor_by_name(name):
    app.logger.debug("Getting actor: %s", name)
    try:
        name = ' '.join(name.split("_"))
        ret = input_data[0][name]
    except:
        print(input_data[0])
        return 'Bad Request: cannot find the actor', 400

    return jsonify(ret)


def parse_query(input_d):
    ret = input_d
    for key, values in request.args.items():
        values = values.split('|')
        ret = filter_result(ret, key, values[0])
        if len(values) > 1:
            for val in values[1:]:
                val = val.split("=")
                if val[0] not in ret[0]:
                    continue
                ret_names = [x['name'] for x in ret]
                other_actors = [x for x in input_d if x["name"] not in ret_names]
                ret += filter_result(other_actors, val[0], val[1])
    return ret


def filter_result(ret, key, value):
    if len(ret) == 0 or key not in ret[0]:
        return ret
    if key == "gross":
        key = "total_gross"
    elif key == "box":
        key = "box_office"
    elif key == "name":
        value = ' '.join(value.split("_"))
    if key in ["gross", "box", "age", "year"]:
        value = int(value)
    out = []
    for entry in ret:
        if entry[key] == value:
            out += [entry]
    return out


# Custom API endpoints
# http://localhost:5000/age/<Actor_Name>
@app.route('/age/<string:name>', methods=['GET'])
def get_age_by_name(name):
    app.logger.debug("Getting age of %s", name)
    ret = {}
    try:
        name = ' '.join(name.split("_"))
        ret["age"] = input_data[0][name]["age"]
    except:
        print(input_data[0])
        return 'Bad Request: cannot find the actor', 400

    return jsonify(ret)


if __name__ == "__main__":
    app.run()
