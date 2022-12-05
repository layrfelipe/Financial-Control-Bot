from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    
    CORS(app)

    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///expenses.db'
    # app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    with app.app_context():
        from src.models import Expense
        db.init_app(app)
        db.create_all()
        db.session.commit()

    from .routes.expenses_routes import expenses_routes
    app.register_blueprint(expenses_routes)

    return app