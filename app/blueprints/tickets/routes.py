from app.blueprints.tickets import tickets_bp
from .schemas import ticket_schema, tickets_schema
from flask import request, jsonify
from marshmallow import ValidationError
from app.models import Tickets, db, Mechanics
from app.blueprints.mechanics.schemas import mechanics_schema
from app.extensions import limiter, cache


# CREATE TICKET
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


# ADD MECHANIC TO TICKET
@tickets_bp.route('/<int:ticket_id>/add-mechanic/<int:mechanic_id>', methods=['PUT'])
@limiter.limit("600 per day", override_defaults=True)
def add_mechanic(ticket_id, mechanic_id):
    ticket = db.session.get(Tickets, ticket_id)
    mechanic = db.session.get(Mechanics, mechanic_id)

    if mechanic not in ticket.mechanics:
        ticket.mechanics.append(mechanic)
        db.session.commit()
        return jsonify({
            'message': f'successfully added {mechanic.name} to ticket',
            'ticket': ticket_schema.dump(ticket),
            'mechanics': mechanics_schema.dump(ticket.mechanics)
        }), 200

    return jsonify("This mechanic is already on the ticket"), 400


# REMOVE MECHANIC FROM TICKET
@tickets_bp.route('/<int:ticket_id>/remove-mechanic/<int:mechanic_id>', methods=['PUT'])
@limiter.limit("200 per day", override_defaults=True)
def remove_mechanic(ticket_id, mechanic_id):
    ticket = db.session.get(Tickets, ticket_id)
    mechanic = db.session.get(Mechanics, mechanic_id)

    if mechanic in ticket.mechanics:
        ticket.mechanics.remove(mechanic)
        db.session.commit()
        return jsonify({
            'message': f'successfully removed {mechanic.name} from ticket',
            'ticket': ticket_schema.dump(ticket),
            'mechanics': mechanics_schema.dump(ticket.mechanics)
        }), 200

    return jsonify("This mechanic is not on the ticket"), 400


# READ ALL TICKETS
@tickets_bp.route('', methods=['GET'])
def read_tickets():
    tickets = db.session.query(Tickets).all()
    return tickets_schema.jsonify(tickets), 200


# READ ONE TICKET
@tickets_bp.route('/<int:ticket_id>', methods=['GET'])
def read_ticket(ticket_id):
    ticket = db.session.get(Tickets, ticket_id)
    return ticket_schema.jsonify(ticket), 200


# DELETE TICKET
@tickets_bp.route('/<int:ticket_id>', methods=['DELETE'])
def delete_ticket(ticket_id):
    ticket = db.session.get(Tickets, ticket_id)
    db.session.delete(ticket)
    db.session.commit()
    return jsonify({"message": f"Successfully deleted ticket {ticket_id}"}), 200


# UPDATE TICKET
@tickets_bp.route('/<int:ticket_id>', methods=['PUT'])
def update_ticket(ticket_id):
    ticket = db.session.get(Tickets, ticket_id)

    if not ticket:
        return jsonify({"message": "ticket not found"}), 404

    try:
        ticket_data = ticket_schema.load(request.json)
    except ValidationError as e:
        return jsonify({"message": e.messages}), 400

    for key, value in ticket_data.items():
        setattr(ticket, key, value)

    db.session.commit()
    return ticket_schema.jsonify(ticket), 200
