from flask import request, jsonify
from marshmallow import ValidationError

from app.blueprints.tickets import tickets_bp
from .schemas import ticket_schema, tickets_schema

from app.models import Tickets, Mechanics, db
from app.blueprints.mechanics.schemas import mechanics_schema

from app.extensions import limiter, cache


# -----------------------------
# CREATE TICKET
# -----------------------------
@tickets_bp.route('', methods=['POST'])
def create_ticket():
    try:
        data = ticket_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    new_ticket = Tickets(**data)
    db.session.add(new_ticket)
    db.session.commit()

    return ticket_schema.jsonify(new_ticket), 201


# -----------------------------
# ADD MECHANIC TO TICKET
# -----------------------------
@tickets_bp.route('/<int:ticket_id>/add-mechanic/<int:mechanic_id>', methods=['PUT'])
@limiter.limit("600 per day", override_defaults=True)
def add_mechanic(ticket_id, mechanic_id):
    ticket = db.session.get(Tickets, ticket_id)
    mechanic = db.session.get(Mechanics, mechanic_id)

    if not ticket or not mechanic:
        return jsonify({"message": "Ticket or mechanic not found"}), 404

    if mechanic not in ticket.mechanics:
        ticket.mechanics.append(mechanic)
        db.session.commit()

        return jsonify({
            "message": f"Successfully added {mechanic.name} to ticket",
            "ticket": ticket_schema.dump(ticket),
            "mechanics": mechanics_schema.dump(ticket.mechanics)
        }), 200

    return jsonify({"message": "Mechanic already assigned to this ticket"}), 400


# -----------------------------
# REMOVE MECHANIC FROM TICKET
# -----------------------------
@tickets_bp.route('/<int:ticket_id>/remove-mechanic/<int:mechanic_id>', methods=['PUT'])
@limiter.limit("200 per day", override_defaults=True)
def remove_mechanic(ticket_id, mechanic_id):
    ticket = db.session.get(Tickets, ticket_id)
    mechanic = db.session.get(Mechanics, mechanic_id)

    if not ticket or not mechanic:
        return jsonify({"message": "Ticket or mechanic not found"}), 404

    if mechanic in ticket.mechanics:
        ticket.mechanics.remove(mechanic)
        db.session.commit()

        return jsonify({
            "message": f"Successfully removed {mechanic.name} from ticket",
            "ticket": ticket_schema.dump(ticket),
            "mechanics": mechanics_schema.dump(ticket.mechanics)
        }), 200

    return jsonify({"message": "Mechanic is not assigned to this ticket"}), 400


# -----------------------------
# GET ALL TICKETS
# -----------------------------
@tickets_bp.route('', methods=['GET'])
def read_tickets():
    tickets = db.session.query(Tickets).all()
    return tickets_schema.jsonify(tickets), 200


# -----------------------------
# GET ONE TICKET
# -----------------------------
@tickets_bp.route('/<int:ticket_id>', methods=['GET'])
def read_ticket(ticket_id):
    ticket = db.session.get(Tickets, ticket_id)

    if not ticket:
        return jsonify({"message": "Ticket not found"}), 404

    return ticket_schema.jsonify(ticket), 200


# -----------------------------
# DELETE TICKET
# -----------------------------
@tickets_bp.route('/<int:ticket_id>', methods=['DELETE'])
def delete_ticket(ticket_id):
    ticket = db.session.get(Tickets, ticket_id)

    if not ticket:
        return jsonify({"message": "Ticket not found"}), 404

    db.session.delete(ticket)
    db.session.commit()

    return jsonify({"message": f"Successfully deleted ticket {ticket_id}"}), 200


# -----------------------------
# UPDATE TICKET
# -----------------------------
@tickets_bp.route('/<int:ticket_id>', methods=['PUT'])
def update_ticket(ticket_id):
    ticket = db.session.get(Tickets, ticket_id)

    if not ticket:
        return jsonify({"message": "Ticket not found"}), 404

    try:
        data = ticket_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    for key, value in data.items():
        setattr(ticket, key, value)

    db.session.commit()
    return ticket_schema.jsonify(ticket), 200

