#!/usr/bin/env python3

from models import db, Activity, Camper, Signup
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


@app.route('/')
def home():
    return ''

@app.route('/campers', methods = ['GET', 'POST'])
def campers():
    if request.method == 'GET':

        campers = Camper.query.all()

        campers_dict = [camper.to_dict(rules = ('-signups', )) for camper in campers]

        response = make_response(
            jsonify(campers_dict),
            200
        )
        return response
    
    elif request.method == 'POST':
        data = request.get_json() 

        try:
            new_camper = Camper(
                name = data['name'],
                age = data['age']
            )

            db.session.add(new_camper)
            db.session.commit()

            response = make_response(
                jsonify(new_camper.to_dict(rules = ('-acitivies', ))),
                201
            )
            return response
        
        except ValueError:

            response = make_response(
                { "errors": ["validation errors"] },
                400
            )
            return response

@app.route('/campers/<int:id>', methods = ['GET', 'PATCH'])
def campers_by_id(id):
    if request.method == 'GET':
        camper = Camper.query.filter(Camper.id == id).first()
        if camper:
            camper_dict = camper.to_dict()

            response = make_response(
                jsonify(camper_dict),
                200
            )
            return response
        else:
            response = make_response(
                {
                    "error" : "Camper not found"
                },
                404
            )
            return response
        
    elif request.method == 'PATCH':
        camper = Camper.query.filter(Camper.id == id).first()

        if camper:

            try:

                data = request.get_json()

                setattr(camper, 'name', data['name'])
                setattr(camper, 'age', data['age'])

                db.session.add(camper)
                db.session.commit()
                response = make_response(
                    jsonify(camper.to_dict()),
                    202
                )

                return response
            
            except ValueError:

                response = make_response(
                    {
                        "errors": ["validation errors"]
                    },
                    400
                )

                return response
            
        else:

            response = make_response(
                {
                "error": "Camper not found"
                },
                404
            )
            
            return response


@app.route('/activities', methods = ['GET'])
def activities():
    activities = Activity.query.all()

    activities_dict = [activity.to_dict(rules = ('-campers', )) for activity in activities]

    response = make_response(
        jsonify(activities_dict),
        200
    )

    return response


app.route('/activities/<int:id>', methods = ['DELETE'])
def activity_by_id(id):

    activity = Activity.query.filter(Activity.id == id).first()

    if activity:

        db.session.delete(activity)

        db.session.commit()

        response = make_response(
            {},
            204
        )
    
        return response
    
    else:

        response = make_response(
            {
                "error": "Activity not found"
            },
            404
        )

        return response

@app.route('/signups', methods = ['POST'])
def signups():

    try:
        data = request.get_json()

        new_signup = Signup(
            time = data['time'],
            camper_id = data['camper_id'],
            activity_id = data['activity_id'] 
        )

        db.session.add(new_signup)

        db.session.commit()

        response = make_response(
            jsonify(new_signup.to_dict()),
            201
        )

        return response
    
    except ValueError:

        response = make_response(
            { "errors": ["validation errors"] },
            400
        )

        return response
    

        


if __name__ == '__main__':
    app.run(port=5555, debug=True)
