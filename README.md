# Linklib
## A cache of links to audio files that you find interesting and enlightening. Sharable and discussable. 



The aim of Linklib is to play the role of a digital library of audio files such as lectures, debates, and podcasts (publicly available content) so that one can maintain their own cache of links they find helpful.


ScreenShots: 
## 
![alt text](http://evanhgarrett.com/src/img/linklib.png "Linklib Full Screen")

## Linklib allows users to play back audio from within the site.
![alt text](http://evanhgarrett.com/src/img/linklibfullscreen.png "Linklib Audio Playback")
## Mobile Friendly
![alt text](http://evanhgarrett.com/src/img/linklibmobile.png "Linklib Mobile View")


# Tech Stack
* HTML Audio
* React
* Custom JWT Authentication Middleware 
* Python3
* Flask HTTP Framework


# Linklib API  (Flask HTTP Framework)

API Url: https://linklib.herokuapp.com/api

## Login:
* `POST /api/login`
  * Requires `email` and `password`
  * Returns JWT token on verified password
  * This is custom JWT authentication middleware that makes use of the python JWT library.


## Users:
* `POST /api/users`
  * Requires `name`,`email`,`password`, `password1`(verify password)
  * Creates a new User

## Entries: 
* `GET /api/entries`
  * Returns a list of entries
  * If `searchTerm` query parameter is present, will return entries mathinc searchterm.
```
"SELECT audioentries.id,author,date, poster, description,hyperlink,title,tags, users.name as postername,users.email as posteremail FROM audioentries LEFT JOIN users ON audioentries.poster = users.id WHERE title ILIKE %(like)s OR description ILIKE %(like)s OR author ILIKE %(like)s OR array_to_string(tags, '||') ILIKE %(like)s"
```
* `GET /api/entries/:id`
  * Requires entry ID, returns entry with specified ID
* `POST /api/entries`
  * Requires `author`,`hyperlink`, and `title` fields, and optionally accepts `description` and `tags` fields.
  * Creates a new entry.

* `PUT /api/entries/:id`
  * Requires an entry ID
  * Updates entry with specified ID by provision of update fields for `author`,`description`,`hyperlink`,`title`.

* `DELETE /api/entries/:id`
  * Requires an entry ID
  * Deletes entry with specified ID