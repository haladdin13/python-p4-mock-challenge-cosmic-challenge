#!/usr/bin/env python3

from models import db, Scientist, Mission, Planet
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask import Flask, make_response, jsonify, request
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)


@app.route('/')
def home():
    return ''

class Scientists(Resource):
    def get(self):
        scientists = [scientist.to_dict(rules=("-missions",)) for scientist in Scientist.query.all()]

        return make_response(scientists, 200)
    
    def post(self):
        request_data = request.get_json()
        try:
            new_scientists = Scientist(**request_data) # ** means unpacking the whole dictionary

        
        except:
            return make_response({"errors": ['validation errors']}, 400)
        
        db.session.add(new_scientists)
        db.session.commit()

        return make_response(new_scientists.to_dict(), 201)
    
    
api.add_resource(Scientists, '/scientists')

class ScientistByID(Resource):
    def get(self, id):

        scientist = Scientist.query.filter(Scientist.id == id).first()
        # scientist = Scientist.query.get_or_404(id)
        
        if not scientist:
          return make_response({"error": "Scientist not found"}, 404)
        
        return make_response(scientist.to_dict(), 200)
    
    def delete(self, id):
        scientist = Scientist.query.filter(Scientist.id == id).first()
        if not scientist:
            return make_response({"error": "Scientist not found"}, 404)

        db.session.delete(scientist)
        db.session.commit()
        
        return make_response({}, 204)
    
    def patch(self, id):
        scientist = Scientist.query.filter(Scientist.id == id).first()
        # scientist = Scientist.query.get_or_404(id)
        req_data = request.get_json()
        if not scientist:
            return make_response({"error": "Scientist not found"}, 404)
        try:
            for key, value in req_data.items():
                setattr(scientist, key, value)
        except:
            return make_response({"errors": ["validation errors"]}, 400)
        
        db.session.commit()

        return make_response(scientist.to_dict(), 202)
    
api.add_resource(ScientistByID, '/scientists/<int:id>')


class Planets(Resource):
    def get(self):
        planets = [planet.to_dict(rules=("-missions",)) for planet in Planet.query.all()]

        return make_response(planets, 200)
    
api.add_resource(Planets, '/planets')

class Missions(Resource):
    def post(self):
        req_data = request.get_json()
        try:
            new_missions = Mission(**req_data)
        except:
            return make_response({"errors": ["validation errors"]}, 400)
        
        db.session.add(new_missions)
        db.session.commit()

        return make_response(new_missions.to_dict(), 201)
    
api.add_resource(Missions, '/missions')
        

if __name__ == '__main__':
    app.run(port=5555, debug=True)
