from waitress import serve
import config
from FLASK_with_ETL import app

if __name__ == "__main__":
    print(f"Starting Waitress on {config.FLASK_HOST}:{config.FLASK_PORT} ...")
    serve(
        app,
        host=config.FLASK_HOST,
        port=config.FLASK_PORT
    )
