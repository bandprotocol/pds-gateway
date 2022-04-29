from config import config
from app import create_app


app = create_app(__name__, config)
