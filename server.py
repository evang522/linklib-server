#================================== Import Dependencies ====================>

from flask import Flask, Response, request, jsonify
from os import environ
import json
import psycopg2
from psycopg2.extras import RealDictCursor

#  Define App
app = Flask(__name__)


# Example Greeting Route /TODO delete this
@app.route('/api/greeting', methods=['GET'])
def get_user():
  data = {"hello":"no"}
  data = json.dumps(data)
  return Response(data, 200, mimetype='application/json')





#================================== Connect Database ====================>
connstring = "dbname=sdwtkwev user=sdwtkwev password=Qjp6QPRO605LrhiMci2dZdXa5piUkQZ0 host=pellefant.db.elephantsql.com"
try:
  dbconn = psycopg2.connect(connstring)
except:
  print('Database connection failed')

# activate connection cursor
cur = dbconn.cursor(cursor_factory=RealDictCursor)



#================================== GET ALL ENTRIES ROUTE ====================>
@app.route('/api/entries', methods=['GET'])
def get_entries():
  cur.execute("SELECT * FROM audioentries")
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

  # Create new Entry Object
  new_entry = {}
  optional_fields_list = ['description','tags']
  required_fields = ['author','hyperlink']

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
      INSERT INTO audioentries (author, description, hyperlink, tags) VALUES (
        %(author)s, %(description)s, %(hyperlink)s, %(tags)s
      )
      """, {'author':new_entry.get('author'), 'description': new_entry.get('description'), 'hyperlink': new_entry.get('hyperlink'), 'tags':new_entry.get('tags')})
    dbconn.commit()
  except:
    return jsonify({'error':'Internal Server Error', 'status':500}), 500
  return Response(json.dumps(new_entry, default=str), 201, mimetype='application/json')


#================================== Update Entries route ====================>

# @app.route('/api/entries/<id>', methods=['PUT'])
# def edit_entry(id):
#   print('Editing id {0}'.form(id))

#   update_fields = ['author','']
#   updatedata = request.get_json()
#   for k in updatedata:
#     if k




# # Conditional run based on environment
# if __name__ == "__main__":
#   try:
#      app.run(host=environ['IP'],port=int(environ['PORT']))
#   except:
#     raise