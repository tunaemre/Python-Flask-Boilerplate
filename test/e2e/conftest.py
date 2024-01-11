import pytest
from flask import Flask


@pytest.fixture(scope='session')
def client(app: Flask):
    app.testing = True  # Must be true to PROPAGATE_EXCEPTIONS
    with app.test_client() as test_client:
        with app.app_context():
            yield test_client
