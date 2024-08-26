from flask import Flask, render_template, redirect, url_for
from flask_bootstrap import Bootstrap5

from flask_wtf import FlaskForm, CSRFProtect
import secrets
from wtforms import StringField, SubmitField
from wtforms.fields.choices import SelectMultipleField
from wtforms.fields.simple import BooleanField
from wtforms.validators import DataRequired, Length

from cards import Cards
app = Flask(__name__)
app.secret_key = secrets.token_urlsafe(16)

# Bootstrap-Flask requires this line
bootstrap = Bootstrap5(app)
# Flask-WTF requires this line
csrf = CSRFProtect(app)

class NameForm(FlaskForm):
    quests_selected = SelectMultipleField(choices=Cards().quest_number_and_name_list())
    submit = SubmitField('Submit')

@app.route('/', methods=['GET', 'POST'])
def hello_world():
    form = NameForm()
    message = ""
    if form.validate_on_submit():
        selected_quests = form.quests_selected.data
        message = cards_from_selected_quests(selected_quests)

    return render_template('index.html', form=form, message=message)

def cards_from_selected_quests(selected_quests):
    card_sets = Cards().get_selected_card_sets(selected_quests)
    # For each hero we want an item which comboes with the hero, or the hero combos with the item
    # heroes = select_heroes(cards)
    pass
