from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_utils import database_exists, create_database

from src.config import app_config_manager
from src.infrastructure.entity.base import mapper_registry


class DBMigrationManager:

    @staticmethod
    def init_migration(app: Flask) -> None:
        config = app_config_manager.get_config()
        url = config.MYSQL_URL.rstrip('/')  # Remove trailing "/" char
        url = f'{url}/{config.MYSQL_DB_NAME}?charset={config.MYSQL_DB_CHARSET}'

        # Use flask-sqlalchemy and flask-migration for migration
        with app.app_context():
            # Import entity models
            from src.infrastructure import entity  # noqa

            # Set flask SQLALCHEMY_DATABASE_URI config for flask-sqlalchemy
            app.config['SQLALCHEMY_DATABASE_URI'] = url
            db = SQLAlchemy(app, metadata=mapper_registry.metadata)

            migration = Migrate()
            migration.init_app(app, db)

            if not database_exists(url):
                create_database(url, encoding=config.MYSQL_DB_CHARSET)

