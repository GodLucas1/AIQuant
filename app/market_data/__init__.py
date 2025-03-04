from flask import Blueprint

market_data_bp = Blueprint('market_data', __name__)

from app.market_data import routes