from flask import Blueprint

backtest_bp = Blueprint('backtest', __name__)

from app.backtest import routes