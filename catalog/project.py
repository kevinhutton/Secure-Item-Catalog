from flask import Flask, render_template, request, redirect, jsonify, url_for, flash
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, CategoryItem, Users
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
from flask import make_response
import requests
import json

app = Flask(__name__)

# Retrieve CLIENT ID from client_secrets
CLIENT_ID = json.loads(
    open('/var/www/html/catalog/client_secrets.json', 'r').read())['web']['client_id']

# Define application name , needed for QAuth authentication
APPLICATION_NAME = "Catalog Application"

# Connect to Database and create database session
engine = create_engine('postgresql://catalog:catalog@/catalog')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

# Create anti-forgery state token


@app.route('/login')
def loginPage():
    print "he"
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)

# Create user in Users DB using corresponding third party account information


def createUser(login_session):
    newUser = Users(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(Users).filter_by(email=login_session['email']).one()
    return user.id
# Helper method to get current user email address


def getUserID(email):
    try:
        user = session.query(Users).filter_by(email=email).one()
        return user.id
    except:
        return None

# Display flash message


def flash_message(message):
    login_session.pop('_flashes', None)
    flash(message)

# main page


@app.route('/')
@app.route('/catalog')
def catalog():
    categories = session.query(Category).order_by(asc(Category.name))
    items = session.query(CategoryItem).order_by(asc(CategoryItem.name))
    return render_template('catalog.html', categories=categories, items=items)

# main page in JSON format


@app.route('/catalog/JSON')
def catalogJSON():
    categories = session.query(Category).order_by(asc(Category.name))
    items = session.query(CategoryItem).order_by(asc(CategoryItem.name))
    return jsonify(categories=[category.serialize for category in categories], items=[item.serialize for item in items])

# Display items for a given category


@app.route('/catalog/category/<int:category_id>')
def category(category_id):
    categories = session.query(Category).filter_by(
        id=category_id).order_by(asc(Category.name))
    items = session.query(CategoryItem).filter_by(
        category_id=category_id).order_by(asc(CategoryItem.name))
    return render_template('catalog.html', categories=categories, items=items)

# Display items for a given category in JSON


@app.route('/catalog/category/<int:category_id>/JSON')
def categoryJSON(category_id):
    categories = session.query(Category).filter_by(
        id=category_id).order_by(asc(Category.name))
    items = session.query(CategoryItem).filter_by(
        category_id=category_id).order_by(asc(CategoryItem.name))
    return jsonify(categories=[category.serialize for category in categories], items=[item.serialize for item in items])

# Create new item


@app.route('/catalog/newitem', methods=['GET', 'POST'])
def newItem():
    if 'username' not in login_session:
        flash_message(
            "You must be logged in to create a new item , please login above")
        return redirect(url_for('loginPage'))
    if request.method == 'POST':
        corresponding_category = session.query(Category).filter_by(
            name=request.form['category_select']).one()
        newItem = CategoryItem(name=request.form['name'], description=request.form['description'],
                               category=corresponding_category, user_id=login_session['user_id'])
        session.add(newItem)
        session.commit()
        return redirect(url_for('catalog'))
    else:
        categories = session.query(Category).order_by(asc(Category.name))
        return render_template('newItem.html', categories=categories)

# Edit existing item


@app.route('/catalog/edititem/<int:item_id>', methods=['GET', 'POST'])
def editItem(item_id):

    currentItem = session.query(CategoryItem).filter_by(id=item_id).one()
    if 'username' not in login_session:
        flash_message(
            "You must be logged in to create edit this item , please login")
        return redirect(url_for('loginPage'))
    elif login_session['user_id'] != currentItem.user_id:
        flash_message(
            "You don't have permissions to edit this item, please login using correct credentials")
        return redirect(url_for('loginPage'))
    else:
        if request.method == 'POST':
            currentItem.name = request.form['name']
            currentItem.description = request.form['description']
            currentItem.category = session.query(Category).filter_by(
                name=request.form['category_select']).one()
            session.add(currentItem)
            session.commit()
            return redirect(url_for('catalog'))
        else:
            categories = session.query(Category).order_by(asc(Category.name))
            return render_template('editItem.html', categories=categories, item=currentItem)

# Delete item


@app.route('/catalog/deleteitem/<int:item_id>', methods=['GET'])
def deleteItem(item_id):
    print "Login session"
    print login_session
    item = session.query(CategoryItem).filter_by(id=item_id).one()
    print "The item is %s" % str(vars(item))
    if 'username' not in login_session:
        flash_message(
            "You must be logged in to create edit this item , please login")
        return redirect(url_for('loginPage'))
    elif login_session['user_id'] != item.user_id:
        flash_message(
            "You don't have permissions to edit this item, please login using correct credentials")
        return redirect(url_for('loginPage'))
    else:
        session.delete(item)
        session.commit()
        return redirect(url_for('catalog'))

# Show details about particular item


@app.route('/catalog/showitem/<int:item_id>', methods=['GET'])
def showItem(item_id):
    currentItem = session.query(CategoryItem).filter_by(id=item_id).one()
    return render_template('showItem.html', item=currentItem)

# Show details about particular item in JSON


@app.route('/catalog/showitem/<int:item_id>/JSON', methods=['GET'])
def showItemJSON(item_id):
    currentItem = session.query(CategoryItem).filter_by(id=item_id).one()
    return jsonify(item=currentItem.serialize)

# Login via google . Add user to local DB if authentication is a success


@app.route('/gconnect', methods=['POST'])
def gconnect():

    # Validate anti-forgery token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Obtain authorization code from request
    code = request.data

    try:
        # Convert authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('/var/www/html/catalog/client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])

    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()
    print data

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    login_session['provider'] = 'google'

    # see if user exists, make new user if it doesnt
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("You are now logged in as %s" % login_session['username'])
    print "done!"
    return output

# Logout


@app.route('/logout')
def logout():
    # Only disconnect a connected user.
    print "The login session is %s" % login_session
    access_token = login_session['access_token']
    if access_token is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    print "Running: %s " % url
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] != '200':
        # For whatever reason, the given token was invalid.
        response = make_response(
            json.dumps('Failed to revoke token for given user.'), 400)
        response.headers['Content-Type'] = 'application/json'
        return response
    del login_session['username']
    del login_session['email']
    del login_session['picture']
    del login_session['user_id']
    flash("You have been logged out!")
    return redirect(url_for('catalog'))

if __name__ == '__main__':
    # Secret key to encrypt session variables
    app.debug = True
    app.run(port=80)
