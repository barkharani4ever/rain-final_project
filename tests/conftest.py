"""This makes the test configuration setup"""
# pylint: disable=redefined-outer-name
import os

import pytest
from app import create_app, db


@pytest.fixture()
def application():
    """This makes the app"""
    os.environ['FLASK_ENV'] = 'testing'
    application = create_app()
    application.config['WTF_CSRF_ENABLED'] = False

    with application.app_context():
        db.create_all()
        yield application
        db.session.remove()

@pytest.fixture()
def client(application):
    """This makes the http client"""
    return application.test_client()


@pytest.fixture()
def runner(application):
    """This makes the task runner"""
    return application.test_cli_runner()
