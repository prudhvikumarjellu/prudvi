import os

from app import create_app, register_blueprints, attach_middleware

config_name = os.getenv('FLASK_CONFIG')
app = create_app(config_name)
register_blueprints(app)
attach_middleware(app)

if __name__ == '__main__':
    app.run(port=5000)
