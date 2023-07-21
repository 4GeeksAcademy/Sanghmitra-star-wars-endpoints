"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Planet, Character, Favorite
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/user', methods=['GET'])
def handle_get_all_user():
    all_user = User.query.all()
    print(all_user)
    result = list(map(lambda item: item.serialize(), all_user))
    return jsonify(result), 200

@app.route('/user/<int:id>', methods=['GET'])
def handle_get_one_user(id):
    user = User.query.get(id)
    user_serialize = user.serialize()
    return jsonify(user_serialize), 200

@app.route('/user', methods=['POST'])
def handle_create_one_user():
    data = request.get_json()
    new_user = User(
        name = data.get("name"),
        email = data.get("email"),
        password = data.get("password"),
        is_active = data.get("is_active")
    )
    db.session.add(new_user)
    db.session.commit()
    return jsonify(new_user.serialize()), 200

@app.route('/planet', methods=['GET'])
def handle_get_all_planet():
    all_planet = Planet.query.all()
    print(all_planet)
    result = list(map(lambda item: item.serialize(), all_planet))
    return jsonify(result), 200

@app.route('/planet/<int:id>', methods=['GET'])
def handle_get_one_planet(id):
    planet = Planet.query.get(id)
    if planet:
        return jsonify (planet.serialize()), 200
    else:
        return jsonify ({"message" : "Planet not found"}), 404

@app.route('/character', methods=['GET'])
def handle_get_all_character():
    all_character = Character.query.all()
    print(all_character)
    result = list(map(lambda item: item.serialize(), all_character))
    return jsonify(result), 200

@app.route('/character/<int:id>', methods=['GET'])
def handle_get_one_character(id):
    character = Character.query.get(id)
    if character:
        return jsonify (character.serialize()), 200
    else:
        return jsonify ({"message" : "Character not found"}), 404

@app.route('/favorite', methods=['GET'])
def handle_get_all_favorite():
    all_favorite = Favorite.query.all()
    print(all_favorite)
    result = list(map(lambda item: item.serialize(), all_favorite))
    return jsonify(result), 200

@app.route('/favorite/<int:id>', methods=['GET'])
def handle_get_one_favorite(id):
    favorite = Favorite.query.get(id)
    if favorite:
        return jsonify (favorite.serialize()), 200
    else:
        return jsonify ({"message" : "Favorite not found"}), 404
    
@app.route('/user/favorite/<int:id>', methods=['GET'])
def handle_user_favorites(id):
    user = User.query.get(id)
    if user:
        favorites = user.favorites
        return jsonify([favorite.serialize() for favorite in favorites])
    else:
        return jsonify({'message': 'User not found'}), 404
    
@app.route('/favorite/planet/<int:id>', methods=['POST'])
def create_favorite_planet(id):
    data = request.get_json() 
    user_id = data.get('id') 
    
    user = User.query.get(user_id)  
    if user:
        planet = Planet.query.get(id) 
        if planet:
            new_favorite = Favorite(planet_id=planet.id, user_id=user.id)
            db.session.add(new_favorite)
            db.session.commit()
            
            return jsonify({'message': 'Favorite planet created successfully.'}), 200
        else:
            return jsonify({'message': 'Planet not found'}), 404
    else:
        return jsonify({'message': 'User not found'}), 404
    
@app.route('/favorite/character/<int:id>', methods=['POST'])
def create_favorite_character(id):
    data = request.get_json() 
    user_id = data.get('id')  
    
    user = User.query.get(user_id)
    if user:
        character = Character.query.get(id)
        if character:
            new_favorite = Favorite(character_id=character.id, user_id=user.id)
            db.session.add(new_favorite)
            db.session.commit()
            
            return jsonify({'message': 'Favorite character created successfully.'}), 200
        else:
            return jsonify({'message': 'Character not found'}), 404
    else:
        return jsonify({'message': 'User not found'}), 404

@app.route('/favorite/character/<int:id>', methods=['DELETE'])
def delete_favorite_character(id):
    data = request.get_json() 
    user_id = data.get('id')  
    
    user = User.query.get(user_id)  
    if user:
        favorite = Favorite.query.filter_by(character_id=id, user_id=user.id).first()  
        if favorite:
            db.session.delete(favorite)  
            db.session.commit()
            
            return jsonify({'message': 'Favorite deleted successfully.'}), 200
        else:
            return jsonify({'message': 'Favorite not found'}), 404
    else:
        return jsonify({'message': 'User not found'}), 404
    

@app.route('/favorite/planet/<int:id>', methods=['DELETE'])
def delete_favorite_planet(id):
    data = request.get_json() 
    user_id = data.get('id')  
    
    user = User.query.get(user_id)  
    if user:
        favorite = Favorite.query.filter_by(planet_id=id, user_id=user.id).first()  
        if favorite:
            db.session.delete(favorite)  
            db.session.commit()
            
            return jsonify({'message': 'Favorite deleted successfully.'}), 200
        else:
            return jsonify({'message': 'Favorite not found'}), 404
    else:
        return jsonify({'message': 'User not found'}), 404


# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
