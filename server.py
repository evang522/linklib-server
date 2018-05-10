#================================== Import Dependencies ====================>

from flask import Flask, Response, request, jsonify, send_from_directory
from os import environ
import json
import psycopg2
from psycopg2.extras import RealDictCursor
from flask_cors import CORS
from functools import wraps
import jwt
import bcrypt

#  Define App
app = Flask(__name__)
CORS(app)


#================================== Connect Database ====================>
connstring = "dbname=sdwtkwev user=sdwtkwev password=Qjp6QPRO605LrhiMci2dZdXa5piUkQZ0 host=pellefant.db.elephantsql.com"

dbconn = psycopg2.connect(connstring)

# activate connection cursor
cur = dbconn.cursor(cursor_factory=RealDictCursor)


#================================== Authentication ====================>
jwt_secret = environ.get('JWT_SECRET')

# encoded = jwt.encode({'hi':'there'}, jwt_secret, algorithm='HS256')
# decoded = jwt.decode(encoded, 'jwt_secreta', algorithms='HS256')

# Define Auth middleware
def auth_check(f):
    @wraps(f)
    def func_wrapper(*args, **kwargs):
        if request.headers.get('Authorization') == None:
          return jsonify({'error':'No JWT token present. Please log in','status':403}), 403
        auth_header = request.headers.get('Authorization')
        auth_header = auth_header.split(' ')
        token = auth_header[1]
        try:
          decoded = jwt.decode(token, jwt_secret, algorithms='HS256')
        except:
          return jsonify({'error':'JWT token invalid. Please log in again', 'status':403}), 403
        return f(*args, **kwargs)
    return func_wrapper

@app.route('/api/login', methods=['POST'])
def login():
  submitted_login_data = request.get_json()
  formatted_login_data = {}
  required_fields = ['email','password']
  for k in required_fields:
    if not k in submitted_login_data:
      return jsonify({'error':'Missing required field.'}), 400
    formatted_login_data[k] = submitted_login_data[k]
    formatted_login_data['email'] = formatted_login_data['email'].lower()
  cur.execute(
    """
    SELECT id, name, email, password FROM users WHERE email=%(email)s
    """, {'email':formatted_login_data.get('email')}
  )
  data = cur.fetchall()
  if data == []:
    return jsonify({'error':'User not found. Please create an Account', 'status':404}), 404
  db_password = data[0].get('password')

  if bcrypt.checkpw(formatted_login_data.get('password').encode('utf8'), db_password.encode('utf8')):
    token = jwt.encode({'name':data[0].get('name'), 'email':data[0].get('email'), 'id':data[0].get('id')}, jwt_secret, algorithm='HS256')
    return jsonify({'token':token.decode('utf8')})
  else:
    return jsonify({'error':'Incorrect Password', 'status':400}), 400


#================================== USERS ====================>
#================================== CREATE NEW USER ====================>
@app.route('/api/users', methods=['POST'])
def create_user():
  data = request.get_json()
  required_fields = ['name','email','password','password1']
  new_user = {}
  for k in required_fields:
    if not k in data:
      return jsonify({'error':'Missing required field', 'status':400}), 400
    if k == 'password':
      if len(data.get(k)) < 8:
        return jsonify({'error':'Password requires 8 characters minimum', 'status':400}), 400
      l = data.get(k).strip()
      if len(data.get(k)) != len(l):
        return jsonify({'error':'Password contains whitespace', 'status':400}), 400
      if data.get(k) != data.get('password1'):
        return jsonify({'error':'Passwords do not match.', 'status':400}), 400
    if k == 'email':
      if '@' not in data.get(k):
        return jsonify({'error':'Invalid email format', 'status':400}), 400
    if k != 'password1':
      new_user[k] = data.get(k)
    
  new_user['email'] = new_user.get('email').lower()
  
  hashed_password = bcrypt.hashpw(new_user.get('password').encode('utf8'),bcrypt.gensalt())
  new_user['password'] = hashed_password.decode('utf8')

  cur.execute("""
    INSERT INTO users (name,email,password) VALUES (%(name)s, %(email)s,%(password)s)
  """, {'name':new_user.get('name'), 'email':new_user.get('email'), 'password':new_user.get('password')})
  dbconn.commit()
  print(new_user)
  return jsonify({'message':'New user created!'}), 201






#================================== ENTRIES ====================>
#================================== GET ALL ENTRIES ROUTE ====================>
@app.route('/api/entries', methods=['GET'])
@auth_check
def get_entries():
  if request.args.get('searchTerm') != None:
    searchTerm = request.args.get('searchTerm').lower()
    print(searchTerm)
    sql="SELECT audioentries.id,author,date, poster, description,hyperlink,title,tags, users.name as postername,users.email as posteremail FROM audioentries LEFT JOIN users ON audioentries.poster = users.id WHERE title ILIKE %(like)s OR description ILIKE %(like)s OR author ILIKE %(like)s OR array_to_string(tags, '||') ILIKE %(like)s"
    cur.execute(sql, dict(like= '%'+searchTerm+'%'))
  else:
    cur.execute("SELECT audioentries.id,author,date, poster, description,hyperlink,title,tags, users.name as postername,users.email as posteremail FROM audioentries LEFT JOIN users ON audioentries.poster = users.id")
  data = cur.fetchall()
  return Response(json.dumps(data, default=str), 200, mimetype='application/json')


  
#================================== GET ENTRY BY ID ====================>
@app.route('/api/entries/<id>')
def get_entry(id):
  cur.execute("""
  SELECT * FROM audioentries WHERE id=%(id)s
  """,
   {'id':id})
  data = cur.fetchall()
  return Response(json.dumps(data, default=str), 200, mimetype='application/json')


#================================== NEW POST ====================>
@app.route('/api/entries', methods=['POST'])
def new_entry():
  data = request.get_json()
  authtoken = request.headers.get('Authorization').split(' ')[1]
  userinfo = jwt.decode(authtoken, jwt_secret, algorithms='HS256')
  print(userinfo)

  # Create new Entry Object
  new_entry = {}
  optional_fields_list = ['description','tags']
  required_fields = ['author','hyperlink','title']

  for k in required_fields:
    if data.get(k) == None:
      return jsonify({'error':'Missing required field `{0}`'.format(k)}), 400
    else:
      new_entry[k] = data[k]
  
  for l in optional_fields_list:
    if data.get(l) != None:
      new_entry[l] = data[l]
  
  try:
    cur.execute("""
      INSERT INTO audioentries (author, description, hyperlink, tags, title, poster) VALUES (
        %(author)s, %(description)s, %(hyperlink)s, %(tags)s, %(title)s, %(poster)s
      )
      """, {'author':new_entry.get('author'), 'description': new_entry.get('description'), 'hyperlink': new_entry.get('hyperlink'), 'tags':new_entry.get('tags'), 'title':new_entry.get('title'), 'poster':userinfo.get('id')})
    dbconn.commit()
  except:
    raise
    return jsonify({'error':'Internal Server Error', 'status':500}), 500
  return Response(json.dumps(new_entry, default=str), 201, mimetype='application/json')


#================================== Update Entries route ====================>

@app.route('/api/entries/<id>', methods=['PUT'])
def edit_entry(id):
  print('Editing id {0}'.format(id))

  update_fields = ['author','description','hyperlink','title']
  updatedata = request.get_json()
  update_dict = {}

  for k in update_fields:
    if updatedata.get(k) != None:
      update_dict[k] = updatedata.get(k)

  try: 
    cur.execute("""
    UPDATE audioentries SET
    author = COALESCE(%(author)s,author),
    description = COALESCE(%(description)s, description),
    hyperlink = COALESCE(%(hyperlink)s, hyperlink),
    title = COALESCE(%(title)s, title)
    WHERE id=%(id)s
    """, {'author':update_dict.get('author'), 'description':update_dict.get('description'), 'hyperlink':update_dict.get('hyperlink'), 'title':update_dict.get('title'), 'id':id})
    dbconn.commit()
  except:
    raise
    return jsonify({'error':'Internal Server Error', 'status':'500'}), 500
  
  return jsonify({'status':200, 'message':'Update Successful', 'updated fields': update_dict}), 200


#================================== Delete Item Route ====================>

@app.route('/api/entries/<id>', methods=['DELETE'])
def delete_entry(id):

  try:
    cur.execute("""
    DELETE FROM audioentries WHERE id=%(id)s
    """, {'id':id})
    dbconn.commit()
  except:
    raise
    return jsonify({'error':'Internal server error', 'status':'500'}), 500
  
  return jsonify({'status':204, 'message':'deleted successfully'}), 204





# Conditional run based on environment
if __name__ == "__main__":
  try:
     app.run(host=environ.get('IP', '0.0.0.0'),port=int(environ.get('PORT', '8080')))
  except:
    raise