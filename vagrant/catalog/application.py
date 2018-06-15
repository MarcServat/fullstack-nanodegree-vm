from flask import Flask, render_template, request
from flask import redirect, url_for, jsonify, flash, session as login_session
import random
import string
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Category, Item, User
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

app = Flask(__name__)

# Get credentials file for login
CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']

# Get database connection
engine = create_engine('sqlite:///categories.db',
                       connect_args={'check_same_thread': False})
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


# Google login
@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
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

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps(
            'Current user is already connected.'), 200)
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

    login_session['username'] = data['name']
    login_session['email'] = data['email']

    user_id = getUserID(login_session["email"])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    flash("you are now logged in as %s" % login_session['username'])
    return output


# Create User if does not exists
def createUser(login_session):
    newUser = User(username=login_session['username'], email=login_session[
                   'email'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


# Use email as unique id
def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


# Google Logout
@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session.get('access_token')
    if access_token is None:
        print 'Access Token is None'
        response = make_response(json.dumps(
            'Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    print 'In gdisconnect access token is %s', access_token
    print 'User name is: '
    print login_session['username']
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' %
    login_session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print 'result is '
    print result
    # Remove user data
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return redirect(url_for('home'))
    else:
        response = make_response(json.dumps(
            'Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


@app.route('/')
def home():
    # make a state for a login session
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state

    # Get all categories
    categories = session.query(Category).all()

    # Get all Items order by most recents
    items = session.query(Item).order_by(Item.id.desc()).all()
    return render_template('main.html',
                           categories=categories,
                           items=items, STATE=state,
                           session=login_session)


@app.route('/catalog/<string:category_name>/items')
def listItem(category_name):
    # Get all categories
    categories = session.query(Category).all()

    # Get items for a given category
    res = session.query(Category, Item).filter_by(
            name=category_name).filter_by(
            id=Item.category_id).all()
    items = []

    # Take just items
    for _, i in res:
        items.append(i)
    return render_template('items.html',
                           categories=categories,
                           items=items,
                           category_name=category_name)


@app.route('/catalog/<string:category_name>/<string:item_title>')
def itemDescription(category_name, item_title):
    # Select specific category
    category = session.query(Category).filter_by(name=category_name).one()

    # Select specific item
    item = session.query(Item).filter_by(title=item_title).one()

    # Make sure it's what we want
    if item.category_id == category.id:
        return render_template('itemdescription.html',
                               item=item,
                               session=login_session)


@app.route('/catalog/create', methods=['GET', 'POST'])
def createCatalogItem():
    # Proctecting from unlogin users
    if 'username' not in login_session:
        return redirect(url_for('home'))

    # Take input values and save them
    if request.method == 'POST':
        if request.form['title']:
            item_title = request.form['title']
        if request.form['description']:
            item_description = request.form['description']
        if request.form['category']:
            item_category_id = request.form['category']

        newItem = Item(title=item_title,
                       description=item_description,
                       category_id=item_category_id)
        session.add(newItem)
        session.commit()
        return redirect(url_for('home'))
    else:

        categories = session.query(Category).all()
        return render_template(
            'createcatalogitem.html', categories=categories)


@app.route('/catalog/<string:item_title>/edit',
           methods=['GET', 'POST'])
def editCatalogItem(item_title):
    # Proctecting from unlogin users
    if 'username' not in login_session:
        return redirect(url_for('home'))

    editedItem = session.query(Item).filter_by(title=item_title).one()

    # Take input values and save them
    if request.method == 'POST':
        if request.form['title']:
            editedItem.title = request.form['title']
        if request.form['description']:
            editedItem.description = request.form['description']
        if request.form['category']:
            editedItem.category_id = request.form['category']
        session.add(editedItem)
        session.commit()
        return redirect(url_for('home'))
    else:
        # Get all categories        
        categories = session.query(Category).all()
        return render_template(
            'editcatalogitem.html', categories=categories, item=editedItem)


@app.route('/catalog/<string:item_title>/delete',
           methods=['GET', 'POST'])
def deleteCatalogItem(item_title):
    # Proctecting from unlogin users
    if 'username' not in login_session:
        return redirect(url_for('home'))

    # Get item from title
    itemToDelete = session.query(Item).filter_by(title=item_title).one()
    if request.method == 'POST':
        session.delete(itemToDelete)
        session.commit()
        return redirect(url_for('home'))
    else:
        return render_template('deletecatalogitem.html', item=itemToDelete)


@app.route('/catalog.json')
def catalogJSON():
    query = session.query(Category, Item).filter_by(
                            id=Item.category_id).all()
    res = []
    data = {}
    for c, i in query:
        res.append({"category": c.serialize, "items": i.serialize})

    return jsonify(res)


if __name__ == '__main__':
    app.secret_key = 'secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
