from flask import request, jsonify
from marshmallow import ValidationError
from sqlalchemy import select

from app.blueprints.mechanics import mechanics_bp
from app.extensions import db, cache
from app.models import Mechanics
from .schemas import mechanic_schema, mechanics_schema


# -----------------------------
# CREATE MECHANIC
# -----------------------------
@mechanics_bp.route('', methods=['POST'])
def create_mechanic():
    try:
        # Validate incoming JSON for ONE mechanic
        data = mechanic_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    new_mechanic = Mechanics(**data)
    db.session.add(new_mechanic)
    db.session.commit()

    return mechanic_schema.jsonify(new_mechanic), 201


# -----------------------------
# GET ALL MECHANICS
# -----------------------------
@mechanics_bp.route('', methods=['GET'])
@cache.cached(timeout=30)
def read_mechanics():
    try:
        page = int(request.args.get('page'))
        per_page = int(request.args.get('per_page'))

        query = select(Mechanics)
        mechanics = db.paginate(query, page=page, per_page=per_page)

        # Return only the items, not the pagination object
        return mechanics_schema.jsonify(mechanics.items), 200

    except:
        # Fallback: return all mechanics
        all_mechanics = db.session.query(Mechanics).all()
        return mechanics_schema.jsonify(all_mechanics), 200


# -----------------------------
# GET ONE MECHANIC
# -----------------------------
@mechanics_bp.route('/<int:mechanic_id>', methods=['GET'])
def read_mechanic(mechanic_id):
    mechanic = db.session.get(Mechanics, mechanic_id)
    if not mechanic:
        return jsonify({"message": "Mechanic not found"}), 404

    return mechanic_schema.jsonify(mechanic), 200


# -----------------------------
# UPDATE MECHANIC
# -----------------------------
@mechanics_bp.route('/<int:mechanic_id>', methods=['PUT'])
def update_mechanic(mechanic_id):
    mechanic = db.session.get(Mechanics, mechanic_id)
    if not mechanic:
        return jsonify({"message": "Mechanic not found"}), 404

    try:
        data = mechanic_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    for key, value in data.items():
        setattr(mechanic, key, value)

    db.session.commit()
    return mechanic_schema.jsonify(mechanic), 200


# -----------------------------
# DELETE MECHANIC
# -----------------------------
@mechanics_bp.route('/<int:mechanic_id>', methods=['DELETE'])
def delete_mechanic(mechanic_id):
    mechanic = db.session.get(Mechanics, mechanic_id)
    if not mechanic:
        return jsonify({"message": "Mechanic not found"}), 404

    db.session.delete(mechanic)
    db.session.commit()

    return jsonify({"message": f"Successfully deleted mechanic {mechanic_id}"}), 200


# -----------------------------
# SEARCH MECHANICS
# -----------------------------
@mechanics_bp.route('/search', methods=['GET'])
def search_mechanic():
    phone = request.args.get('phone')
    name = request.args.get('name')

    if phone:
        results = db.session.query(Mechanics).where(Mechanics.phone.like(f"%{phone}%")).all()
    elif name:
        results = db.session.query(Mechanics).where(Mechanics.name.like(f"%{name}%")).all()
    else:
        return jsonify({"message": "No search parameters provided"}), 400

    return mechanics_schema.jsonify(results), 200
