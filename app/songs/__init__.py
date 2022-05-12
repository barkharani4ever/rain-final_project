import csv
import logging
import os

from flask import Blueprint, render_template, abort, url_for, current_app, flash
from flask_login import current_user, login_required
from jinja2 import TemplateNotFound

from app.db import db
from app.db.models import Song
from app.songs.forms import csv_upload
from werkzeug.utils import secure_filename, redirect
from app.songs.forms import song_edit_form
from app.songs.forms import song_add_form

songs = Blueprint('songs', __name__,
                  template_folder='templates')


@songs.route('/songs', methods=['GET'], defaults={"page": 1})
@songs.route('/songs/<int:page>', methods=['GET'])
def songs_browse(page):
    page = page
    per_page = 9
    pagination = Song.query.paginate(page, per_page, error_out=False)
    data = pagination.items
    try:
        return render_template('browse_songs.html', data=data, pagination=pagination)
    except TemplateNotFound:
        abort(404)


@songs.route('/songs_datatables/', methods=['GET'])
def browse_songs_datatables():
    data = Song.query.all()

    retrieve_url = ('songs.edit_song', [('song_id', ':id')])
    edit_url = ('songs.edit_song', [('song_id', ':id')])
    add_url = url_for('songs.add_song')
    delete_url = ('songs.delete_song', [('song_id', ':id')])

    return render_template('browse_songs_datatables.html', add_url=add_url, edit_url=edit_url,
                           delete_url=delete_url, retrieve_url=retrieve_url, data=data, Song=Song,
                           record_type="Songs")

    try:
        return render_template('browse_songs_datatables.html', data=data)
    except TemplateNotFound:
        abort(404)

"""@songs.route('/api/songs/', methods=['GET'])
def api_songs():
    data = Song.query.all()
    try:
        return jsonify(data=[song.serialize() for song in data])
    except TemplateNotFound:
        abort(404)

@songs.route('/songs/songs', methods=['GET'])
def song_2PM():
    spotify_api_key = current_app.config.get('SPOTIFY_API_KEY')
    log = logging.getLogger("myApp")
    log.info(spotify_api_key)
    try:
        return render_template('song_2PM.html', spotify_api_key=spotify_api_key)
    except TemplateNotFound:
        abort(404)"""


@songs.route('/songs/upload', methods=['POST', 'GET'])
@login_required
def songs_upload():
    form = csv_upload()
    if form.validate_on_submit():
        #log = logging.getLogger("myApp")
        filename = secure_filename(form.file.data.filename)
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        form.file.data.save(filepath)
        # user = current_user
        list_of_songs = []
        with open(filepath) as file:
            csv_file = csv.DictReader(file)
            for row in csv_file:
                list_of_songs.append(Song(row['title'], row['artist']))

        current_user.songs = list_of_songs
        db.session.commit()

        return redirect(url_for('songs.browse_songs_datatables'))

    try:
        return render_template('upload.html', form=form)
    except TemplateNotFound:
        abort(404)


@songs.route('/songs/<int:song_id>/edit', methods=['POST', 'GET'])
@login_required
def edit_song(song_id):
    song = Song.query.get(song_id)
    form = song_edit_form(obj=song)
    if form.validate_on_submit():
        song.title = form.title.data
        song.artist = form.artist.data
        db.session.add(song)
        db.session.commit()
        flash('Song edit success', 'success')
        current_app.logger.info("edited the song")
        return redirect(url_for('songs.browse_songs_datatables'))
    return render_template('song_edit.html', form=form)


@songs.route('/songs/new', methods=['POST', 'GET'])
@login_required
def add_song():
    form = song_edit_form()
    if form.validate_on_submit():
        song = Song.query.filter_by(title=form.title.data).first()
        if song is None:
            song = Song(title=form.title.data, artist=form.artist.data)
            db.session.add(song)
            db.session.commit()
            flash('Added a song', 'success')
            return redirect(url_for('songs.browse_songs_datatables'))
        else:
            flash('Song already added')
            return redirect(url_for('songs.songs_browse'))
    return render_template('song_add.html', form=form)


@songs.route('/songs/<int:song_id>/delete', methods=['POST'])
@login_required
def delete_song(song_id):
    song = Song.query.get(song_id)
    db.session.delete(song)
    db.session.commit()
    flash('Song deleted', 'success')
    return redirect(url_for('songs.browse_songs_datatables'), 302)