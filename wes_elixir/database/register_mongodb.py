import logging

from flask_pymongo import ASCENDING, PyMongo

from wes_elixir.config.config_parser import get_conf
from wes_elixir.ga4gh.wes.utils_service_info import get_service_info


# Get logger instance
logger = logging.getLogger(__name__)


def register_mongodb(app):
    '''Instantiate database and initialize collections'''

    # Initialize PyMongo instance
    uri = "mongodb://{host}:{port}/{name}".format(
        host=get_conf(app.app.config, 'database', 'host'),
        port=get_conf(app.app.config, 'database', 'port'),
        name=get_conf(app.app.config, 'database', 'name'),
    )
    mongo = PyMongo(app.app, uri=uri)
    logger.info("Registered database '{name}' at URI '{uri}' with Connexion application.".format(
        name=get_conf(app.app.config, 'database', 'name'),
        uri=uri,
    ))

    # Add database
    db = mongo.db[get_conf(app.app.config, 'database', 'name')]

    # Add database collection for '/service-info'
    collection_service_info = mongo.db['service-info']
    logger.debug("Added database collection 'service_info'.")

    # Add database collection for '/runs'
    collection_runs = mongo.db['runs']
    collection_runs.create_index([
            ('run_id', ASCENDING),
            ('task_id', ASCENDING),
        ],
        unique=True,
        sparse=True
    )
    logger.debug("Added database collection 'runs'.")

    # Add database and collections to app config
    app.app.config['database']['database'] = db
    app.app.config['database']['collections'] = dict()
    app.app.config['database']['collections']['runs'] = collection_runs
    app.app.config['database']['collections']['service_info'] = collection_service_info

    # Initialize service info
    logger.debug("Initializing service info...")
    get_service_info(app.app.config, silent=True)

    # Return app
    return app