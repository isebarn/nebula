from flask import Flask
from flask_restx import Resource, Api
from flask import request
from model import Player
from model import Follow

app = Flask(__name__)
api = Api(app)


@api.route("/player/<vid>")
class PlayerController(Resource):
    def get(self, vid):
        return Player(vid=vid).get().to_json()

    def post(self, vid):
        return Player(**{**request.get_json(), "vid": vid}).save().to_json()


@api.route("/follow/<start>/<stop>")
class FollowController(Resource):
    def post(self, start, stop):
        return (
            Follow(**{**request.get_json(), "start": start, "stop": stop})
            .save()
            .to_json()
        )
