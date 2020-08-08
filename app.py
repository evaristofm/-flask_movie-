from flask import Flask, render_template,request,redirect,url_for
from pymongo import MongoClient
from bson.objectid import ObjectId



cluster = MongoClient("mongodb+srv://admin:admin@cluster0-4lzge.mongodb.net/movie?retryWrites=true&w=majority")

db = cluster.movie
collection = db.movies

app = Flask(__name__)


@app.route("/movies")
def get_movies():
    movies = collection.find()
    return render_template("index.html", movies=movies)


@app.route("/movies/add", methods=["POST"])
def movie_add():
    name = request.values.get("name")
    theme = request.values.get("theme")
    collection.insert({"_id": ObjectId(),"name": name, "theme": theme, "like": 0, "dislike": 0})
    return redirect(url_for('get_movies'))


@app.route("/movie/thumbs_up/<name>")
def thumbs_up(name):
    movie = collection.update_one(
        {"name": name}, {"$inc": {"like": +1}}
    )
    return redirect(url_for('get_movies'))


@app.route("/movie/thumbs_down/<name>")
def thumbs_down(name):
    movie = collection.update_one(
        {"name": name}, {"$inc": {"dislike": +1}}
    )
    return redirect(url_for('get_movies'))


@app.route("/themes")
def list_themes():
    gru = collection.aggregate(
        [
            {"$match": {} },
            {"$group": {"_id": "$theme",
            "thumbs_up": {"$sum": "$like"},
            "thumbs_down": {"$sum": "$dislike"}}},
            {"$project": {
                "calc": {"$subtract": ["$thumbs_up", {"$divide": ["$thumbs_down", 2]}]}
            }},
            {"$sort": {"calc": -1}}
            
        ]
    )
    return render_template("list_themes.html", gru=gru)
