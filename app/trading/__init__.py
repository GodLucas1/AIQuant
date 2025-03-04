from flask import Blueprint

trading_bp = Blueprint('trading', __name__)

from app.trading import routes