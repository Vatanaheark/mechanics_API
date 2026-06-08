from dotenv import load_dotenv
load_dotenv()

from flask import Flask
from config import ProductionConfig
from app.models import db
from flask_cors import CORS

def create_app(config_class=ProductionConfig):
    app = Flask(__name__)
    app.config.from_object(config_class)

    CORS(app)
    db.init_app(app)

    # register blueprints here
    # app.register_blueprint(...)

    return app
