import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
'''
db_drop_and_create_all()


# ROUTES
@app.route('/drinks',methods=['GET'])
@requires_auth('get:drinks')
def get_drinks(payload):
    try:
        drinks = Drink.query.all()
        drinks = [drink.short() for drink in drinks]        
        if payload:
            return jsonify({                
                'success':True,
                'drinks':drinks
            })
        else:
            abort(403)
    except AuthError:
        abort(401)


@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def get_drink_details(payload):
    try:
        drinks = Drink.query.all()
        drinks = [drink.long() for drink in drinks]
        if payload:
            return jsonify({                
                'success':True,
                'drinks':drinks
            })
        else:
            abort(403)
    except AuthError:
        abort(401)


@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def post_drinks(payload):
    try:        
        request_data = request.get_json()        
        title_data=request_data.get('title',None)        
        recipe_data=request_data.get('recipe',None)        
        if title_data or recipe_data:
            new_drink = Drink(               
                title = title_data,
                recipe = recipe_data
            )
            if payload:    
                new_drink.insert()
                drink = Drink.query.filter(Drink.title == title_data).one_or_none()
                                   
                return jsonify({                    
                    "success":True,
                    "drinks":[drink.long()]                    
                })
            else:
                abort(403)
        else:
            abort(422)        
    except AuthError:
        abort(401)


@app.route('/drinks/<int:drink_id>',methods=['PATCH'])
@requires_auth('patch:drinks')
def edit_drink(drink_id,payload):
    try:
        request_data = request.get_json()
        title = request_data.get('title',None)
        recipe = request_data.get('recipe',None)
        if title or recipe:
            drink = Drink.query.filter(Drink.id == drink_id).one_or_none()
            if drink is None:
                abort(404)
            else:
                if payload:
                    drink.title = title
                    drink.recipe = recipe
                    drink.update()  
                                  
                    return jsonify({
                        "status code": 200,
                        "success": True,
                        "drinks": drink.long()
                    })
                else:
                    abort(403)
        else:
            abort(422)
    except AuthError:
        abort(401)


@app.route('/drinks/<int:drink_id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(drink_id,payload):
    try:
        drink = Drink.query.filter(Drink.id == drink_id).one_or_none()
        if drink is None:
            abort(404)
        else:
            if payload:
                drink.delete()
                return jsonify({
                    "status code": 200,
                    "success":True,
                    "delete": drink_id
                })
            else:
                abort(403)
    except AuthError:
        abort(401)

# Error Handling
'''
Example error handling for unprocessable entity
'''


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422



@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success":False,
        "error":404,
        "message":"resource not found"
    }),404


@app.errorhandler(401)
def not_authenticated(error):
    return jsonify({
        "success":False,
        "error":401,
        "message":"invalid claim, unable to verify token"        
    }),401

@app.errorhandler(403)
def not_authorized(error):
    return jsonify({
        "success":False,
        "error":403,
        "message":"unauthorized"        
    }),403