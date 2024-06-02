import pytest
from app import create_app, db
from flask import url_for
from app.models import User
from werkzeug.security import check_password_hash

@pytest.fixture(scope='module')
def new_user():
    user = User(username='testuser', password='testpassword')
    return user

@pytest.fixture(scope='module')
def test_client():
    flask_app = create_app()
    
    # Create a Flask test client using the Flask application configured for testing
    with flask_app.test_client() as testing_client:
        with flask_app.app_context():
            db.create_all()
            yield testing_client
            db.drop_all()

@pytest.fixture(scope='function')
def login_default_user(test_client):
    test_client.post('/auth/register', data=dict(username='defaultuser', password='123456', confirm='123456'), follow_redirects=True)
    test_client.post('/auth/login', data=dict(username='defaultuser', password='123456'), follow_redirects=True)
    yield
    test_client.get('/auth/logout', follow_redirects=True)


def test_register_user(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/auth/register' page is posted to (POST)
    THEN check that a new user is registered correctly
    """
    response = test_client.post('/auth/register', data=dict(username='newuser', password='newpassword', confirm='newpassword'), follow_redirects=True)
    assert response.status_code == 200
    assert b'Registration successful. You can now log in.' in response.data

    # Query the database and check the new user has been added
    user = User.query.filter_by(username='newuser').first()
    assert user is not None
    assert check_password_hash(user.password, 'newpassword')


def test_register_existing_user(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/auth/register' page is posted to (POST) with an existing user
    THEN check that the user registration is prevented
    """
    response = test_client.post('/auth/register', data=dict(username='defaultuser', password='newpassword', confirm='newpassword'), follow_redirects=True)
    assert response.status_code == 200
    assert b'Username already exists' in response.data


def test_login_user(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/auth/login' page is posted to (POST)
    THEN check that the user is logged in correctly
    """
    response = test_client.post('/auth/login', data=dict(username='defaultuser', password='123456'), follow_redirects=True)
    assert response.status_code == 200
    assert b'Logged in successfully!' in response.data

def test_login_invalid_user(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/auth/login' page is posted to (POST) with invalid credentials
    THEN check that the user login is prevented
    """
    response = test_client.post('/auth/login', data=dict(username='invaliduser', password='invalidpassword'), follow_redirects=True)
    assert response.status_code == 200
    assert b'Invalid username or password' in response.data


def test_logout_user(test_client, login_default_user):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/auth/logout' page is accessed (GET)
    THEN check that the user is logged out correctly
    """
    response = test_client.get('/auth/logout', follow_redirects=True)
    assert response.status_code == 200
    assert b'You have been logged out.' in response.data