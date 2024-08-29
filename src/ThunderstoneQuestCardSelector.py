import secrets

from flask import Flask, render_template
from flask_bootstrap import Bootstrap5
from flask_wtf import FlaskForm, CSRFProtect
from wtforms import SubmitField, widgets
from wtforms.fields.choices import SelectMultipleField, RadioField

from src.cards import Cards

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
    quests_selected = MultiCheckboxField(label="Select Quests:", choices=Cards().quest_number_and_name_list())
    require_all_hero_classes = RadioField('Require all hero classes:', choices=[(1, "Yes"), (0, "No")], default=1)
    combos_per_hero = RadioField('Combos per hero:', choices=[(0, "None"), (1, "One"), (2, "Two")], default=1)
    submit = SubmitField('Generate Card Selections')


@app.route('/', methods=['GET', 'POST'])
def select_quest_page():
    form = NameForm()
    message = ""
    selected_sets = []
    if form.validate_on_submit():
        selected_quests = form.quests_selected.data
        diverse_heroes = bool(form.require_all_hero_classes.data)
        combos_per_hero = int(form.combos_per_hero.data)
        try:
            card_sets = Cards().get_selected_card_sets(selected_quests, debug=True)
            for i in range(6):
                selected = card_sets.select_cards(diverse_heroes=diverse_heroes, combos_per_hero=combos_per_hero)
                selected_sets.append(selected)
        except Exception as e:
            message=str(e)

    return render_template('index.html', form=form, message=message, selected_sets=selected_sets)


@app.route('/about', methods=['GET'])
def about_page():
    return render_template('about.html')

