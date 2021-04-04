from flask import Flask, request, jsonify
from pymongo import MongoClient
import os
import json
import redis

application = Flask(__name__)
mongoClient = MongoClient('mongodb://' + os.environ['MONGODB_USERNAME'] + ':' + os.environ['MONGODB_PASSWORD'] +
                          '@' + os.environ['MONGODB_HOSTNAME'] + ':27017/' + os.environ['MONGODB_AUTHDB'])
db = mongoClient[os.environ['MONGODB_DATABASE']]
redisClient = redis.Redis(host=os.environ.get("REDIS_HOST", "localhost"), port=os.environ.get(
    "REDIS_PORT", 6379), db=os.environ.get("REDIS_DB", 0))
collection_game = db.game

@application.route('/')
def index():
    game = collection_game.find_one()
    if game == None:
        mydict = {
            "question": ["_","_","_","_"], 
            "answer": [], 
            "index_now": 0, 
            "count": 0
        }
        collection_game.insert_one(mydict)
        body = '<h1> Four Word Guessing Game </h1>'
        body += '<h2> lets play </h2>'
        body += '<button> <a href="/">Play</a></button>'

    if game != None:
        question = ' '.join(game['question'])
        nember = game['index_now']
        body = '<h1>Four Word Guessing Game </h1>'
        body += '<h1>Time to create the question </h1>'
        body += '<h2>Please Choose A or B or C or D to create the question</h2>'
        body += 'Nember: ' + str(nember)
        body += '<br></br>'
        body += 'Question: ' + question
        body += '<br></br>'
        body += '<a href="/a/"><button>A</button></a>'
        body += '<a href="/b/"><button>B</button></a>'
        body += '<a href="/c/"><button>C</button></a>'
        body += '<a href="/d/"><button>D</button></a>'
        if game['index_now'] == 4:
            body = '<h1>Four Word Guessing Game </h1>'
            body += '<h2>Create sucsess</h1>'
            body += 'Question: ' + question
            body += '<br></br>'
            body += '<a href="/ingame/"><button> Time To Guess</button></a>'
            return body
    return body

@application.route('/a/')
def ans_A():
    game = collection_game.find_one()
    if game['index_now'] < 4:
        insert_question(game, 'A')
        return index()
    if game['index_now'] >= 4:
        insert_answer(game, 'A')
        return play()

@application.route('/b/')
def ans_B():
    game = collection_game.find_one()
    if game['index_now'] < 4:
        insert_question(game, 'B')
        return index()
    if game['index_now'] >= 4:
        insert_answer(game, 'B')
        return play()

@application.route('/c/')
def ans_C():
    game = collection_game.find_one()
    if game['index_now'] < 4:
        insert_question(game, 'C')
        return index()
    if game['index_now'] >= 4:
        insert_answer(game, 'C')
        return play()

@application.route('/d/')
def ans_D():
    game = collection_game.find_one()
    if game['index_now'] < 4:
        insert_question(game, 'D')
        return index()
    if game['index_now'] >= 4:
        insert_answer(game, 'D')
        return play()

def insert_question(game, word):
    index_now = game["index_now"]
    collection_game.update_one({}, {"$set": {"question." + str(index_now) : word}})
    index_now += 1
    collection_game.update_one({}, {"$set": {"index_now" : index_now}})

def insert_answer(game, word):
    if game['question'] == game['answer']:
        return win()
    index_now = game["index_now"]
    current_count = game["count"]
    current_count += 1
    if game['question'][index_now - 4] == word:
        collection_game.update_one({}, {"$set": {"answer." + str(index_now - 4) : word}})
        index_now += 1
        collection_game.update_one({}, {"$set": {"index_now" : index_now}})
    collection_game.update_one({}, {"$set": {"count": current_count}})

@application.route('/ingame/')
def play():
    remain = ''
    collection_game = db.game
    game = collection_game.find_one()
    now = 8 - game['index_now']
    for i in range(now):
        remain += '* '
    if game['question'] == game['answer']:
        return win()
    ans_text = ' '.join(game['answer'])
    body = '<h1>Four Word Guessing Game</h1>'
    body += '<h2>Please Choose A or B or C or D to guess.</h2>'
    body += 'Words remaining: ' + remain
    body += '<br> <br>'
    body += 'Your Answer: ' + ans_text
    body += '<br> <br>'
    body += 'Total Count: ' + str(game["count"] )
    body += '<br> <br>'
    body += 'Choose:'  
    body += '<a href="/a"><button> A </button></a>' 
    body += '<a href="/b"><button> B </button></a>'
    body += '<a href="/c"><button> C </button></a>'
    body += '<a href="/d"><button> D </button></a>'
    return body

@application.route('/win/')
def win():
    collection_game = db.game
    game = collection_game.find_one()
    question = ' '.join(game['question'])
    body = '<h1>Four Word Guessing Game</h1>'
    body += '<h2>You win! </h2>'
    body += ' Answer is ' + question
    body += '<br> <br> '
    body += '<b>Total Count: </b>' + str(game['count'])
    body += '<br> <br>'
    body += '<a href="/again"><button> Play Again </button></a>'
    return body

@application.route('/again/')
def again():
    collection_game = db.game
    mydict = {
        "question": ["_","_","_","_"], 
        "answer": [], 
        "index_now": 0,
        "count":0, 
    }
    collection_game.update_one({}, {"$set": mydict})
    return index()

if __name__ == "__main__":
    ENVIRONMENT_DEBUG = os.environ.get("FLASK_DEBUG", True)
    ENVIRONMENT_PORT = os.environ.get("FLASK_PORT", 5000)
    application.run(host='0.0.0.0', port=ENVIRONMENT_PORT, debug=ENVIRONMENT_DEBUG)