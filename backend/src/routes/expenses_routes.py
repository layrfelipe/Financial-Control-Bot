import json
from flask import Blueprint, request

from src import db
from src.models import Expense

expenses_routes = Blueprint('expenses_routes', __name__)

@expenses_routes.route("/register", methods=["POST"])
def register():
        request_data = request.get_json()
        print(request_data)
        
        description = request_data["description"]
        value = request_data["value"]
        value = value.replace(",", ".", 1)
        date = request_data["date"]
        
        expense = Expense(description = description, value=value, date=date)
        db.session.add(expense)
        db.session.commit()

        return json.dumps(expense.as_dict())

@expenses_routes.route("/expenses", methods=["GET"])
def expenses():
    json_response = []

    db_response = db.session.query(Expense).all()

    for item in db_response:
        json_response += [item.as_dict()]
    
    return json.dumps(json_response)