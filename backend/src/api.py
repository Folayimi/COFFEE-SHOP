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

'''
    GET /drinks
        a public endpoint
        it contains only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
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

'''
    GET /drinks-detail
        it requires the 'get:drinks-detail' permission
        it contains the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''

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
'''
    POST /drinks
        it creates a new row in the drinks table
        it requires the 'post:drinks' permission
        it contains the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''

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
                recipe = recipe_data if type(recipe_data) == str else json.dumps(recipe_data)                
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
    except TypeError:
        abort(422)
    except AuthError:
        abort(401)

'''
    PATCH /drinks/<id>
        where <id> is the existing model id
        it responds with a 404 error if <id> is not found
        it updates the corresponding row for <id>
        it requires the 'patch:drinks' permission
        it contains the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''

@app.route('/drinks/<int:id>',methods=['PATCH'])
@requires_auth('patch:drinks')
def edit_drink(payload,id):    
    print("drink")
    try:
        request_data = request.get_json()
        title = request_data.get('title',None)
        recipe = request_data.get('recipe',None)        
        if title or recipe:
            drink = Drink.query.filter(Drink.id == id).one_or_none()
            
            if drink is None:
                abort(404)
            else:
                if payload:
                    drink.title = title
                    drink.recipe = recipe if type(recipe) == str else json.dumps(recipe)

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
    except TypeError:
        abort(422)
    except AuthError:
        abort(401)

'''
    DELETE /drinks/<id>
        where <id> is the existing model id
        it responds with a 404 error if <id> is not found
        it deletes the corresponding row for <id>
        it requires the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''

@app.route('/drinks/<int:drink_id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(payload,drink_id):
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

'''
    each error handler returns (with approprate messages):
             jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''

'''
    implements error handler for 404
'''

@app.errorhandler(AuthError)
def AuthError(error):
    
    """
    Need to return JSON and we'll have to get a response
    
    """
    response = jsonify(error.error)
    response.status_code = error.status_code
    return response

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success":False,
        "error":404,
        "message":"resource not found"
    }),404

'''
    implements error handler for AuthError
'''

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