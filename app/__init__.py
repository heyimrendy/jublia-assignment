from flask import Flask

from app.extensions import db, migrate, mail, make_celery
from config import Config


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)

    celery = make_celery(app)
    celery.set_default()

    from app.api import bp as api_bp

    app.register_blueprint(api_bp, url_prefix="/api")

    return app, celery
