#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.types import Enum
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from datetime import datetime


#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate= Migrate(app, db)

# TODO: connect to a filter postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#


class Venue(db.Model):
    __tablename__ = 'Venue'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website=db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean())
    talent_description = db.Column(db.Text)
    genres=db.Column(db.ARRAY(db.String()))
    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    artists = db.relationship('Artist', secondary='show', backref='playing_venues')
    # def get_venue(self, city, state):
    #     return self.query.filter(self.city==city, self.state==state).all()
    
class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String()))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, default = False)
    seeking_description = db.Column(db.Text)
    venues = db.relationship('Venue', secondary='show', backref='venue_artists')

    # DONE: implement any missing fields, as a database migration using Flask-Migrate

     
# DONE Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

class Show(db.Model):
    __tablename__ = 'show'
    artist_id=db.Column(db.Integer, db.ForeignKey('Artist.id'), primary_key=True)
    venue_id=db.Column(db.Integer, db.ForeignKey('Venue.id'), primary_key=True)
    start_time = db.Column(db.DateTime, default=datetime.utcnow)
    
#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # DONE: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  filters = []
  all_venues = Venue.query.distinct(Venue.city, Venue.state).all()
  for venue in all_venues:
      filter = {
          'city': venue.city,
          'state': venue.state
      }
      filters.append(filter)
  venues = Venue.query.all()
  for filter in filters:
      filter["venues"] = []
      for venue in venues:
          if venue.city == filter["city"] and venue.state == filter["state"]:
              v = {
                  'id': venue.id,
                  'name': venue.name
              }
              filter["venues"].append(v)

  return render_template('pages/venues.html', areas=filters) 
  
@app.route('/venues/search', methods=['POST'])
def search_venues():
  # DONE: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search_term = request.form.get('search_term', '')
  venues = Venue.query.filter(Venue.name.ilike('%'+search_term+'%')).all()
  data=[]
  for venue in venues:
    num_upcoming_shows=0
    shows=Show.query.filter(Show.venue_id==venue.id)
    for show in shows:
      if (show.start_time>datetime.now()):
        num_upcoming_shows +=1
    data.append({
      'id':venue.id,
      'name':venue.name,
      'num_upcoming_shows':num_upcoming_shows
    })
  response={
    'count':len(venues),
    'data':data
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))
  
@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # DONE: replace with real venue data from the venues table, using venue_id
  venue=Venue.query.get_or_404(venue_id)
  return render_template('pages/show_venue.html', venue=venue)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # done: insert form data as a new Venue record in the db, instead
  # done: modify data to be the data object returned from db insertion
  form = VenueForm(request.form)
  new_venue=Venue(
                  name=form.name.data,
                  city=form.city.data,
                  state=form.state.data,
                  address=form.address.data,
                  phone=form.phone.data,
                  website=form.website.data,
                  facebook_link=form.facebook_link.data,
                  image_link=form.image_link.data,
                  seeking_talent=form.seeking_talent.data,
                  talent_description=form.talent_description.data,
                  genres=form.genres.data
  )
  if form.validate_on_submit():
      db.session.add(new_venue)
      db.session.commit()
  # on successful db insert, flash success
      flash('Venue ' + request.form['name'] + ' was successfully listed!')
      return render_template('pages/home.html', form=form)
  else:
  # TODO: on unsuccessful db insert, flash an error instead.
      flash('An error occurred. Venue ' + new_venue.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html', form=form)  

@app.route('/venues/<venue_id>/delete', methods=['POST'])
def delete_venue(venue_id):
  
  # done: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  venue=Venue.query.get_or_404(venue_id)
  db.session.delete(venue)
  db.session.commit()
  flash('your venue has been deleted!')
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return redirect(url_for('index'))

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # DONE: replace with real data returned from querying the database
  artists=Artist.query.all()
  return render_template('pages/artists.html', artists=artists)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # DONE: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  
  search_term = request.form.get('search_term', '')
  artists = Artist.query.filter(Artist.name.ilike('%'+search_term+'%')).all()
  data=[]
  for artist in artists:
    num_upcoming_shows=0
    shows=Show.query.filter(Show.artist_id==artist.id)
    for show in shows:
      if (show.start_time>datetime.now()):
        num_upcoming_shows +=1
    data.append({
      'id':artist.id,
      'name':artist.name,
      'num_upcoming_shows':num_upcoming_shows
    })
  response={
    'count':len(artists),
    'data':data
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))
  
  
  # response={
  #   "count": 1,
  #   "data": [{
  #     "id": 4,
  #     "name": "Guns N Petals",
  #     "num_upcoming_shows": 0,
  #   }]
  # }

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # done: replace with real venue data from the venues table, using venue_id
  artist=Artist.query.get_or_404(artist_id)
  return render_template('pages/show_artist.html', artist=artist)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist=Artist.query.get_or_404(artist_id)
  form.name.data=artist.name
  form.city.data=artist.city
  form.state.data=artist.state
  form.phone.data=artist.phone
  form.website.data=artist.website
  form.facebook_link.data=artist.facebook_link
  form.image_link.data=artist.image_link
  form.seeking_venue.data=artist.seeking_venue
  form.seeking_description.data=artist.seeking_description
  # Done: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # Done: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  form=ArtistForm()
  artist=Artist.query.get_or_404(artist_id)
  artist.name=form.name.data
  artist.city=form.city.data
  artist.state=form.state.data
  artist.phone=form.phone.data
  artist.website=form.website.data
  artist.facebook_link=form.facebook_link.data
  artist.image_link=form.image_link.data
  artist.genres=form.genres.data
  artist.seeking_venue=form.seeking_venue.data
  artist.venue_description=form.seeking_description.data
  db.session.commit()
  flash('Artist '+ request.form['name'] + ' has been updated')
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue=Venue.query.get_or_404(venue_id)
  form.name.data=venue.name
  form.city.data=venue.city
  form.state.data=venue.state
  form.address.data=venue.address
  form.phone.data=venue.phone
  form.genres.data=venue.genres
  form.website.data=venue.website
  form.facebook_link.data=venue.facebook_link
  form.image_link.data=venue.image_link
  form.seeking_talent.data=venue.seeking_talent
  form.talent_description.data=venue.talent_description
  # done: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # done: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  form=VenueForm()
  venue=Venue.query.get_or_404(venue_id)
  venue.name=form.name.data
  venue.city=form.city.data
  venue.state=form.state.data
  venue.address=form.address.data
  venue.phone=form.phone.data
  venue.genres=form.genres.data
  venue.website=form.website.data
  venue.facebook_link=form.facebook_link.data
  venue.image_link=form.image_link.data
  venue.seeking_talent=form.seeking_talent.data
  venue.talent_description=form.talent_description.data
  db.session.commit()
  flash('venue '+ request.form['name'] + ' has been updated')
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # done: insert form data as a new Venue record in the db, instead
  # done: modify data to be the data object returned from db insertion
  form = ArtistForm()
  new_artist=Artist(
                  name=form.name.data,
                  city=form.city.data,
                  state=form.state.data,
                  phone=form.phone.data,
                  genres=form.genres.data,
                  website=form.website.data,
                  facebook_link=form.facebook_link.data,
                  image_link=form.image_link.data,
                  seeking_venue=form.seeking_venue.data,
                  seeking_description=form.seeking_description.data
  )
  if form.validate_on_submit():
    db.session.add(new_artist)
    db.session.commit()
  # on successful db insert, flash success
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  else:
    flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  
  result = []
  shows = Show.query.join(Venue, Show.venue_id == Venue.id).join(Artist, Artist.id == Show.artist_id).all()
  for show in shows:
    print(show.artist.name)
    show_obj = {"venue_id": show.venue_id,
    "venue_name": show.venue.name,
    "artist_id": show.artist_id,
    "artist_name": show.artist.name,
    "artist_image_link": show.artist.image_link,
    "start_time": str(show.start_time)
    }
    result.append(show_obj)
    
  # data=[{
  #   "venue_id": 1,
  #   "venue_name": "The Musical Hop",
  #   "artist_id": 4,
  #   "artist_name": "Guns N Petals",
  #   "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
  #   "start_time": "2019-05-21T21:30:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 5,
  #   "artist_name": "Matt Quevedo",
  #   "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
  #   "start_time": "2019-06-15T23:00:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 6,
  #   "artist_name": "The Wild Sax Band",
  #   "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #   "start_time": "2035-04-01T20:00:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 6,
  #   "artist_name": "The Wild Sax Band",
  #   "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #   "start_time": "2035-04-08T20:00:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 6,
  #   "artist_name": "The Wild Sax Band",
  #   "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #   "start_time": "2035-04-15T20:00:00.000Z"
  # }]
  return render_template('pages/shows.html', shows=shows)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)
  

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # DONE: insert form data as a new Show record in the db, instead
  form=ShowForm()
  show=Show(
          artist_id = form.artist_id.data,
          venue_id = form.venue_id.data,
          start_time=form.start_time.data
  )
  try:
    db.session.add(new_show)
    db.session.commit()
    flash('Show was successfully listed')
  except:
    flash('An error occurred. Show could not be added')
  finally:
    db.session.close()
  return render_template('pages/home.html')
  # on successful db insert, flash success
  flash('Show was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''