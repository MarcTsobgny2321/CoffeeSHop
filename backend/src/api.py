import os
from turtle import title
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
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
'''
db_drop_and_create_all()


# ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks')
def drinks():
    try:
        drinks = Drink.query.all()
    except:
        abort(404)
    formatted_drinks = []
    for drink in drinks:
        dd = drink.short()
        formatted_drinks.append(dd)
    return jsonify({
        "Success": True,
        "drinks": formatted_drinks
    })


'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def drinks_detail(jwt):
    try:
        drinks = Drink.query.all()
    except:
        abort(404)
    formatted_drinks = []
    for drink in drinks:
        dd = drink.long()
        formatted_drinks.append(dd)
    return jsonify({
        "success": True,
        "drinks": formatted_drinks
    })


'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks', methods=['POST'])
@requires_auth("post:drinks")
def create_drinks(jwt):
    
        body = request.get_json()
        new_title = body.get('title', None)
        new_recipe = body.get('recipe', None)
        if (new_title == None) | (new_recipe == None):
            abort(422)
        else:
            recipes=[]
            for recipe in new_recipe:
                name=recipe.get('name')
                color=recipe.get('color')
                parts=recipe.get('parts')
                recipes.append({"name ": name, "color": color, "parts":parts })
            drink = Drink(title=new_title, recipe=json.dumps(recipes))
            drink.insert()


            drinks = Drink.query.all()
            formatted_drinks = []
            for dk in drinks:
                dd = dk.long()
            formatted_drinks.append(dd)

            return jsonify({
                'success': True,
                'drinks': formatted_drinks
            })

   


'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks/<id>', methods=['PATCH'])
@requires_auth("patch:drinks")
def update_drink(jwt,id):
    try:
        body = request.get_json()
        new_title = body.get('title', None)
        new_recipe = body.get('recipe', None)
        drink = Drink.query.get(id)
        if drink == None:
            abort(404)
        else:
            drink.title = new_title
            recipes=[]
            for recipe in new_recipe:
                name=recipe.get('name')
                color=recipe.get('color')
                parts=recipe.get('parts')
                recipes.append({"name ": name, "color": color, "parts":parts })
            drink.recipe = json.dumps(recipes)
            drink.insert()

            return jsonify({
                'success': True,
                'drinks': drink.long(),

            }, 200)
    except:
        abort(404)
    return True


'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks/<id>', methods=['DELETE'])
@requires_auth("delete:drinks")
def delete_drink(jwt,id):

    drink = Drink.query.filter_by(id=id).one_or_none()
    if drink is None:
        abort(404)
    else:
        drink.delete()
        return jsonify({
            'success': True,
            'delete': id
        }, 200)


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
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''


@app.errorhandler(404)
def not_found(error):
    return (jsonify({'success': False,
                     'error': 404,
                     'message': 'resource not found'
                     }),
            404)


'''
@TODO implement error handler for 404
    error handler should conform to general task above
'''


'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''
@app.errorhandler(AuthError)
def handle_error(e):
    response = {
        "message": 401,
        "description": e.error,
    }
    return jsonify(response),401