#================================== Import Dependencies ====================>

from flask import Flask, Response, request, jsonify, send_from_directory

from os import environ
import json
import psycopg2
from psycopg2.extras import RealDictCursor


#  Define App
app = Flask(__name__,static_url_path='')


app.route('/', methods=['GET'])
def serve_html():
  return send_static_file('index.html')




#================================== Connect Database ====================>
connstring = "dbname=sdwtkwev user=sdwtkwev password=Qjp6QPRO605LrhiMci2dZdXa5piUkQZ0 host=pellefant.db.elephantsql.com"

dbconn = psycopg2.connect(connstring)

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
      INSERT INTO audioentries (author, description, hyperlink, tags, title) VALUES (
        %(author)s, %(description)s, %(hyperlink)s, %(tags)s, %(title)s
      )
      """, {'author':new_entry.get('author'), 'description': new_entry.get('description'), 'hyperlink': new_entry.get('hyperlink'), 'tags':new_entry.get('tags'), 'title':new_entry.get('title')})
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