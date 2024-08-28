from flask import Flask, render_template, redirect, url_for
from flask_bootstrap import Bootstrap5

from flask_wtf import FlaskForm, CSRFProtect
import secrets
from wtforms import StringField, SubmitField, widgets
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

class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(html_tag='ul', prefix_label=False)
    option_widget = widgets.CheckboxInput()

class NameForm(FlaskForm):
    quests_selected = MultiCheckboxField(choices=Cards().quest_number_and_name_list())
    submit = SubmitField('Submit')

@app.route('/', methods=['GET', 'POST'])
def hello_world():
    form = NameForm()
    message = ""
    hero_csv = ""
    marketplace_csv = ""
    if form.validate_on_submit():
        selected_quests = form.quests_selected.data
        hero_csv, marketplace_csv = cards_from_selected_quests(selected_quests)

    return render_template('index.html', form=form, message=message, heroes=hero_csv, marketplace=marketplace_csv)

def cards_from_selected_quests(selected_quests):
    card_sets = Cards().get_selected_card_sets(selected_quests)
    heroes = card_sets.select_diverse_heroes()
    marketplace_cards = card_sets.select_marketplace_cards()
    hero_csv = ", ".join([v.name for v in heroes])
    marketplace_csv = ", ".join([v.name for v in marketplace_cards])
    return hero_csv, marketplace_csv
