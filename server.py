#!/usr/bin/env python2.7

"""
Columbia's COMS W4111.001 Introduction to Databases
Example Webserver

To run locally:

    python server.py

Go to http://localhost:8111 in your browser.

A debugger such as "pdb" may be helpful for debugging.
Read about it online.
"""

import os
import webbrowser
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, flash, session, request, render_template, g, redirect, Response, url_for

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)

DEBUG = True

SECRET_KEY = 'development key'

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)
app.config.from_object(__name__)

username = None

#
# The following is a dummy URI that does not connect to a valid database. You will need to modify it to connect to your Part 2 database in order to use the data.
#
# XXX: The URI should be in the format of: 
#
#     postgresql://USER:PASSWORD@w4111a.eastus.cloudapp.azure.com/proj1part2
#
# For example, if you had username gravano and password foobar, then the following line would be:
#
#     DATABASEURI = "postgresql://gravano:foobar@w4111a.eastus.cloudapp.azure.com/proj1part2"
#
DATABASEURI = "postgresql://xz2580:nb@zxy98@w4111vm.eastus.cloudapp.azure.com/w4111"


#
# This line creates a database engine that knows how to connect to the URI above.
#
engine = create_engine(DATABASEURI)

#
# Example of running queries in your database
# Note that this will probably not work if you already have a table named 'test' in your database, containing meaningful data. This is only an example showing you how to run queries in your database using SQLAlchemy.
#
engine.execute("""CREATE TABLE IF NOT EXISTS test (
  id serial,
  name text
);""")
engine.execute("""INSERT INTO test(name) VALUES ('grace hopper'), ('alan turing'), ('ada lovelace');""")


@app.before_request
def before_request():
  """
  This function is run at the beginning of every web request 
  (every time you enter an address in the web browser).
  We use it to setup a database connection that can be used throughout the request.

  The variable g is globally accessible.
  """
  try:
    g.conn = engine.connect()
  except:
    print ("uh oh, problem connecting to database")
    import traceback; traceback.print_exc()
    g.conn = None

@app.teardown_request
def teardown_request(exception):
  """
  At the end of the web request, this makes sure to close the database connection.
  If you don't, the database could run out of memory!
  """
  try:
    g.conn.close()
  except Exception as e:
    pass


#
# @app.route is a decorator around index() that means:
#   run index() whenever the user tries to access the "/" path using a GET request
#
# If you wanted the user to go to, for example, localhost:8111/foobar/ with POST or GET then you could use:
#
#       @app.route("/foobar/", methods=["POST", "GET"])
#
# PROTIP: (the trailing / in the path is important)
# 
# see for routing: http://flask.pocoo.org/docs/0.10/quickstart/#routing
# see for decorators: http://simeonfranklin.com/blog/2012/jul/1/python-decorators-in-12-steps/
#

# Methods that connect to webs
@app.route('/')
def index():
  return render_template('index.html')

#login
@app.route('/login', methods=['GET', 'POST'])
def login():

  global username
  
  error = None

  if request.method == 'POST':

    result = engine.execute("SELECT COUNT(*) FROM users U WHERE U.username = %s",
                            request.form['username'])
    userExists = (result.fetchone()[0] != 0)
    result.close()

    if not userExists:
      error = 'Invalid Username'
    if userExists:
      result = engine.execute('SELECT password FROM users U WHERE U.username = %s',
                              request.form['username'])
      password = str.split(str(result.fetchone()['password']))[0]
      result.close()
      if request.form['password'] != password:
        session['logged_in'] = False
        error = 'Invalid Password.'
      else:
        session['logged_in'] = True
        username = request.form['username']
        flash('Login Complete')
        return redirect(url_for('index'))
  return render_template('login.html', error=error)

# Log out
@app.route('/logout')
def logout():

  global username 

  session.pop('logged_in', None)
  username = None
  flash('User Logged Out')
  return redirect(url_for('index'))

# Register
@app.route('/register',methods=['GET','POST'])
def register():

  error = None
  if request.method == 'POST':
    result = engine.execute('SELECT COUNT(*) FROM users U WHERE U.email = %s',
                            [request.form['email']])
    emailExists = (result.fetchone()[0]!=0)
    result.close()

    print("email checked!")

    result = engine.execute('SELECT COUNT(*) FROM users U WHERE U.username = %s',
                            [request.form['username']])
    userExists = (result.fetchone()[0]!=0)
    result.close()

    print("username checked!")
    
    if request.form['password']!=request.form['passwordAgain']:
      error = 'Passwords Do Not Match'
    elif emailExists:
      error = 'Email Already Exists'
    elif userExists:
      error = 'Username Already Exists'
    else:
      engine.execute('INSERT INTO users VALUES (%s, %s, %s)',
                     [request.form['username'],request.form['email'],request.form['password']])
      session['logged_in'] = True
      flash('Account Created')
      return redirect(url_for('index'))
  return render_template('register.html',error=error)

@app.route('/ceramic',methods=['GET','POST'])
def ceramic():
    error = None
    context = dict(error=error)
    if request.method == 'GET':
        result = g.conn.execute('SELECT a.name, a.url FROM AuctionGood a, Genre g \
          WHERE a.url = g.url AND g.class = %s', 'ceramic')
        good_list = []

        for row in result:
            good_list.append(row)

        context["good_list"] = good_list

        return render_template('ceramic.html', **context)
    return render_template('ceramic.html')

@app.route('/bronze',methods=['GET','POST'])
def bronze():
    error = None
    context = dict(error=error)
    if request.method == 'GET':
        result = g.conn.execute('SELECT a.name, a.url FROM AuctionGood a, Genre g \
          WHERE a.url = g.url AND g.class = %s', 'bronze')
        good_list = []

        for row in result:
            good_list.append(row)

        context["good_list"] = good_list

        return render_template('bronze.html', **context)
    return render_template('bronze.html')

@app.route('/furniture',methods=['GET','POST'])
def furniture():
    error = None
    context = dict(error=error)
    if request.method == 'GET':
        result = g.conn.execute('SELECT a.name, a.url FROM AuctionGood a, Genre g \
          WHERE a.url = g.url AND g.class = %s', 'furniture')
        good_list = []

        for row in result:
            good_list.append(row)

        context["good_list"] = good_list

        return render_template('furniture.html', **context)
    return render_template('furniture.html')

@app.route('/jade',methods=['GET','POST'])
def jade():
    error = None
    context = dict(error=error)
    if request.method == 'GET':
        result = g.conn.execute('SELECT a.name, a.url FROM AuctionGood a, Genre g \
          WHERE a.url = g.url AND g.class = %s', 'jade')
        good_list = []

        for row in result:
            good_list.append(row)

        context["good_list"] = good_list

        return render_template('jade.html', **context)
    return render_template('jade.html')

@app.route('/painting',methods=['GET','POST'])
def painting():
    error = None
    context = dict(error=error)
    if request.method == 'GET':
        result = g.conn.execute('SELECT a.name, a.url FROM AuctionGood a, Genre g \
          WHERE a.url = g.url AND g.class = %s', 'painting&calligraphy')
        good_list = []

        for row in result:
            good_list.append(row)

        context["good_list"] = good_list

        return render_template('painting.html', **context)
    return render_template('painting.html')

@app.route('/other',methods=['GET','POST'])
def other():
    error = None
    context = dict(error=error)
    if request.method == 'GET':
        result = g.conn.execute('SELECT a.name, a.url FROM AuctionGood a, Genre g \
          WHERE a.url = g.url AND g.class = %s', 'others')
        good_list = []

        for row in result:
            good_list.append(row)

        context["good_list"] = good_list

        return render_template('other.html', **context)
    return render_template('other.html')


# Connections to webs

# @app.route('link_url', methods=['POST', 'GET'])
# def link_url():
#     if request.method == 'POST':
#         result = g.conn.execute('SELECT url FROM AuctionGood WHERE name LIKE %s',request.form['name'])
#     url = result[0]
#     webbrowser.open(url);

#genre search
@app.route('/search', methods=['POST', 'GET'])
def search():
    error = None
    context = dict(error=error)
    if request.method == 'POST':
        if request.form['class']!='--' and request.form['color']!='--'and request.form['period']!='--':
            result = g.conn.execute('SELECT a.name, a.url FROM AuctionGood a, Genre g, Time t WHERE a.url = g.url \
            AND a.period = t.period \
            AND g.class = %s \
            AND g.color = %s \
            AND t.period = %s', request.form['class'], request.form['color'], request.form['period'])
        elif request.form['class']=='--' and request.form['color']!='--'and request.form['period']!='--':
            result = g.conn.execute('SELECT a.name, a.url FROM AuctionGood a, Genre g, Time t WHERE a.url = g.url \
            AND a.period = t.period \
            AND g.color = %s \
            AND t.period = %s', request.form['color'], request.form['period'])
        elif request.form['class']=='--' and request.form['color']=='--'and request.form['period']!='--':
            result = g.conn.execute('SELECT a.name, a.url FROM AuctionGood a, Genre g, Time t WHERE a.url = g.url \
            AND a.period = t.period \
            AND t.period = %s', request.form['period'])
        elif request.form['class']=='--' and request.form['color']=='--'and request.form['period']=='--':
            result = g.conn.execute('SELECT a.name, a.url FROM AuctionGood a, Genre g, Time t WHERE a.url = g.url \
            AND a.period = t.period')
        elif request.form['class']!='--' and request.form['color']=='--'and request.form['period']!='--':
            result = g.conn.execute('SELECT a.name, a.url FROM AuctionGood a, Genre g, Time t WHERE a.url = g.url \
            AND a.period = t.period \
            AND g.class = %s \
            AND t.period = %s', request.form['class'], request.form['period'])
        else:
            result = g.conn.execute('SELECT a.name, a.url FROM AuctionGood a, Genre g, Time t WHERE a.url = g.url \
            AND a.period = t.period \
            AND g.class = %s', request.form['class'])
        good_list = []

        for row in result:
            good_list.append(row)

        context["good_list"] = good_list

        return render_template('search.html', **context)
    return render_template('search.html')

#auction search
@app.route('/auction', methods=['POST', 'GET'])
def auction():
    error = None
    context = dict(error=error)
    if request.method == 'POST':
        if request.form['location']!='--' and request.form['house']!='--'and request.form['year']!='--' and request.form['month']!= '--':
                result = g.conn.execute('SELECT a.name, u.title, p.hammerprice \
                FROM AuctionGood a, Auction u, Auctionhouse h, Dealtime d, Price p WHERE u.title = a.title \
                AND a.url = p.url \
                AND u.year = d.year \
                AND u.month = d.month \
                AND u.name = h.name \
                AND u.name = %s \
                AND d.year = %s \
                AND d.month = %s \
                AND u.location = %s \
                GROUP BY a.name, u.title, p.hammerprice', request.form['house'], request.form['year'], request.form['month'], request.form['location'])
        elif request.form['location']=='--' and request.form['house']!='--'and request.form['year']!='--'and request.form['month']!= '--':
                result = g.conn.execute('SELECT a.name, u.title, p.hammerprice \
                FROM AuctionGood a, Auction u, Auctionhouse h, Dealtime d, Price p WHERE u.title = a.title \
                AND a.url = p.url \
                AND u.year = d.year \
                AND u.month = d.month \
                AND u.name = h.name \
                AND u.name = %s \
                AND d.year = %s\
                AND d.month = %s\
                GROUP BY a.name, u.title, p.hammerprice', request.form['house'], request.form['year'], request.form['month'])
        elif request.form['location']=='--' and request.form['house']=='--'and request.form['year']!='--' and request.form['month']!='--':
                result = g.conn.execute('SELECT a.name, u.title, p.hammerprice \
                FROM AuctionGood a, Auction u, Auctionhouse h, Dealtime d, Price p WHERE u.title = a.title \
                AND a.url = p.url \
                AND u.year = d.year \
                AND u.month = d.month \
                AND u.name = h.name \
                AND d.year = %s \
                AND d.month = %s\
                GROUP BY a.name, u.title, p.hammerprice', request.form['year'], request.form['month'])
        elif request.form['location']=='--' and request.form['house']=='--'and request.form['year']=='--' and request.form['month']!='--':
                result = g.conn.execute('SELECT a.name, u.title, p.hammerprice \
                FROM AuctionGood a, Auction u, Auctionhouse h, Dealtime d, Price p WHERE u.title = a.title \
                AND a.url = p.url \
                AND u.year = d.year \
                AND u.month = d.month \
                AND u.name = h.name \
                AND d.month = %s\
                GROUP BY a.name, u.title, p.hammerprice', request.form['month'])
        elif request.form['location']=='--' and request.form['house']=='--'and request.form['year']!='--' and request.form['month']=='--':
                result = g.conn.execute('SELECT a.name, u.title, p.hammerprice \
                FROM AuctionGood a, Auction u, Auctionhouse h, Dealtime d, Price p WHERE u.title = a.title \
                AND a.url = p.url \
                AND u.year = d.year \
                AND u.month = d.month \
                AND u.name = h.name \
                AND d.year = %s\
                GROUP BY a.name, u.title, p.hammerprice', request.form['year'])
        elif request.form['location']=='--' and request.form['house']=='--'and request.form['year']=='--' and request.form['month']=='--':
                result = g.conn.execute('SELECT a.name, u.title, p.hammerprice \
                FROM AuctionGood a, Auction u, Auctionhouse h, Dealtime d, Price p WHERE u.title = a.title \
                AND a.url = p.url \
                AND u.year = d.year \
                AND u.month = d.month \
                AND u.name = h.name \
                GROUP BY a.name, u.title, p.hammerprice')
        elif request.form['location']=='--' and request.form['house']!='--'and request.form['year']=='--' and request.form['month']=='--':
                result = g.conn.execute('SELECT a.name, u.title, p.hammerprice \
                FROM AuctionGood a, Auction u, Auctionhouse h, Dealtime d, Price p WHERE u.title = a.title \
                AND a.url = p.url \
                AND u.year = d.year \
                AND u.month = d.month \
                AND u.name = h.name \
                AND u.name = %s\
                GROUP BY a.name, u.title, p.hammerprice', request.form['house'])
        elif request.form['location']!='--' and request.form['house']=='--'and request.form['year']!='--' and request.form['month']!='--':
                result = g.conn.execute('SELECT a.name, u.title, p.hammerprice \
                FROM AuctionGood a, Auction u, Auctionhouse h, Dealtime d, Price p WHERE u.title = a.title \
                AND a.url = p.url \
                AND u.year = d.year \
                AND u.month = d.month \
                AND u.name = h.name \
                AND u.year = %s \
                AND u.month = %s \
                AND u.location = %s\
                GROUP BY a.name, u.title, p.hammerprice', request.form['year'], request.form['month'], request.form['location'])
        elif request.form['location']!='--' and request.form['house']=='--'and request.form['year']=='--' and request.form['month']!='--':
                result = g.conn.execute('SELECT a.name, u.title, p.hammerprice \
                FROM AuctionGood a, Auction u, Auctionhouse h, Dealtime d, Price p WHERE u.title = a.title \
                AND a.url = p.url \
                AND u.year = d.year \
                AND u.month = d.month \
                AND u.name = h.name \
                AND u.month = %s \
                AND u.location = %s\
                GROUP BY a.name, u.title, p.hammerprice', request.form['month'], request.form['location'])
        elif request.form['location']!='--' and request.form['house']=='--'and request.form['year']=='--' and request.form['month']=='--':
                result = g.conn.execute('SELECT a.name, u.title, p.hammerprice \
                FROM AuctionGood a, Auction u, Auctionhouse h, Dealtime d, Price p WHERE u.title = a.title \
                AND a.url = p.url \
                AND u.year = d.year \
                AND u.month = d.month \
                AND u.name = h.name \
                AND u.location = %s\
                GROUP BY a.name, u.title, p.hammerprice', request.form['location'])
        elif request.form['location']!='--' and request.form['house']!='--'and request.form['year']=='--' and request.form['month']!='--':
                result = g.conn.execute('SELECT a.name, u.title, p.hammerprice \
                FROM AuctionGood a, Auction u, Auctionhouse h, Dealtime d, Price p WHERE u.title = a.title \
                AND a.url = p.url \
                AND u.year = d.year \
                AND u.month = d.month \
                AND u.name = h.name \
                AND u.name = %s \
                AND u.month = %s \
                AND u.location = %s\
                GROUP BY a.name, u.title, p.hammerprice', request.form['house'], request.form['month'], request.form['location'])
        elif request.form['location']!='--' and request.form['house']!='--'and request.form['year']=='--' and request.form['month']=='--':
                result = g.conn.execute('SELECT a.name, u.title, p.hammerprice \
                FROM AuctionGood a, Auction u, Auctionhouse h, Dealtime d, Price p WHERE u.title = a.title \
                AND a.url = p.url \
                AND u.year = d.year \
                AND u.month = d.month \
                AND u.name = h.name \
                AND u.name = %s \
                AND u.location = %s\
                GROUP BY a.name, u.title, p.hammerprice', request.form['house'], request.form['location'])
        else:
                result = g.conn.execute('SELECT a.name, u.title, p.hammerprice \
                FROM AuctionGood a, Auction u, Auctionhouse h, Dealtime d, Price p WHERE u.title = a.title \
                AND a.url = p.url \
                AND u.year = d.year \
                AND u.month = d.month \
                AND u.name = h.name \
                AND u.name = %s \
                AND u.month = %s \
                AND u.location = %s\
                GROUP BY a.name, u.title, p.hammerprice', request.form['house'], request.form['month'], request.form['location'])

        
        auction_list = []
        for row in result:
                auction_list.append(row)

        context["auction_list"] = auction_list

        return render_template('auction.html', **context)
    return render_template('auction.html')


# Example of adding new data to the database
@app.route('/add', methods=['POST'])
def add():
  name = request.form['name']
  g.conn.execute('INSERT INTO test VALUES (NULL, ?)', name)
  return redirect('/')


if __name__ == "__main__":
  import click

  @click.command()
  @click.option('--debug', is_flag=True)
  @click.option('--threaded', is_flag=True)
  @click.argument('HOST', default='0.0.0.0')
  @click.argument('PORT', default=8111, type=int)
  def run(debug, threaded, host, port):
    """
    This function handles command line parameters.
    Run the server using:

        python server.py

    Show the help text using:

        python server.py --help

    """

    HOST, PORT = host, port
    print ("running on %s:%d" % (HOST, PORT))
    app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)


  run()
