from flask_wtf import FlaskForm
from wtforms import validators
from wtforms.fields import *


class song_edit_form(FlaskForm):
    title = TextAreaField('Title', [validators.length(min=6, max=300)],
                          description="Add Title")
    artist = TextAreaField('Artist', [validators.length(min=6, max=300)],
                           description="Add Artist")

    submit = SubmitField()


class song_add_form(FlaskForm):
    title = TextAreaField('Add title', [
        validators.length(min=6, max=300),

    ], description="Title")

    artist = TextAreaField('Add artist', [
        validators.length(min=6, max=300),

    ], description="Artist")

    submit = SubmitField()


class csv_upload(FlaskForm):
    file = FileField()
    submit = SubmitField()
