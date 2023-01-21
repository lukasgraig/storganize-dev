
from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from storganize.auth import login_required
from storganize.db import get_db
from storganize.createqr import CreateQR
from storganize.forms import BoxForm, SearchForm

bp = Blueprint('storage', __name__)

@bp.route('/')
def index():
    return render_template('storganize_templates/index.html')

@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_box():
    form = BoxForm()

    if form.validate_on_submit():
        items = request.form.getlist('box_item') # use request.form.getlist when handling a dynamic form or one that has the same name placeholder

        uuid = CreateQR.generate_uuid(g.user['username']) # request to create a qr code

        db = get_db()  # establish connection to db
        db.execute(
            'INSERT INTO storage_box (uuid, username, box_type, box_title, box_desc)'
            ' VALUES (?, ?, ?, ?, ?)',
            (uuid, g.user['username'], form.box_type.data, form.box_title.data, form.box_desc.data)
        )
        for item in items:
            db.execute(
                'INSERT INTO items (item, uuid)'
                ' VALUES (?, ?)',
                (item, uuid)
            )
        db.commit()

        return redirect(url_for('storage.get_all_storage_box'))  # redirect user back to the index page

    return render_template('storganize_templates/create.html', form=form)

@bp.route('/myboxes', methods=['GET'])
@login_required
def get_all_storage_box():
    # returns all the boxes that the user has created

    db = get_db()
    boxes = db.execute('''SELECT * FROM storage_box
                    WHERE storage_box.username = ?''', (g.user['username'],)).fetchall()
    
    return render_template('storganize_templates/myboxes.html', boxes=boxes)

@bp.route('/<uuid>/view', methods=['GET'])
@login_required
def view(uuid, check_author=True):
    user_info, user_items = get_box_from_uuid(uuid)

    if check_author and user_info['username'] != g.user['username']:
        abort(403, render_template('storganize_templates/notfound.html'))
    if not user_info:
        abort(404, render_template('storganize_template/notfound.html'))

    filename = g.user['username'] + '-' + uuid + '.png'
    return render_template('storganize_templates/viewbox.html', info=user_info, items=user_items, img=filename)

def get_box_from_uuid(uuid):
    # function for the program to retrieve box based on what the uuid the user specifies is

    db = get_db()
    user_info = db.execute('''SELECT * FROM storage_box
                    WHERE storage_box.uuid = ?''', (uuid,)).fetchone()
    
    user_items = db.execute('''SELECT items.* FROM items
                        WHERE items.uuid = ?''', (uuid,)).fetchall()

    return user_info, user_items

@bp.route('/<uuid>/update', methods=['GET', 'POST'])
@login_required
def update(uuid):
    user_info, user_items = get_box_from_uuid(uuid)
    
    box_info = {
        'box_title': user_info[5],
        'box_desc': user_info[4],
        'box_type': user_info[3]
    }

    if request.method == 'POST':
        form = BoxForm()

        item = request.form['box_item']

        # check to see if user updated certain fields, if not then dont update them
        #print(form_data.short_name) # gets the name tag in the html tag
        for form_data in form:
            if form_data.data == '':
                form_data.data = box_info[form_data.short_name]

        error = None

        if not form.box_title.data:
           error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute('UPDATE storage_box SET box_type =?, box_title=?, box_desc=? WHERE uuid = ?', 
                (form.box_type.data, form.box_title.data, form.box_desc.data, uuid))
            db.commit()

            return redirect(url_for('storage.index'))

    return render_template('storganize_templates/update.html', info=user_info, items=user_items)

@bp.route('/user/<username>')
@login_required
def user_profile(username):
    user = get_db().execute(
        'SELECT u.username'
        ' FROM user u'
        ' WHERE u.username = ?',
        (username,)).fetchone()

    if user is None:
        abort(404, f"user {username} doesn't exist.")

    return render_template('storganize_templates/profile.html', user=user)

@bp.route('/view/<uuid>/delete', methods=['GET', 'POST'])
@login_required
def delete_box(uuid):
    db = get_db()
    db.execute('DELETE FROM storage_box WHERE uuid=?', (uuid,))
    db.execute('DELETE FROM items WHERE uuid=?', (uuid,))

    db.commit()
    return redirect(url_for('storage.get_all_storage_box'))

#pass stuff to the navbar
@bp.context_processor
def base():
    form = SearchForm()
    return dict(form=form)

@bp.route('/myboxes/search', methods=['POST'])
def search():
    form = SearchForm()
    if form.validate_on_submit():
        #get data from submitted form
        searched = form.searched.data
        #query the database
        db = get_db()
        user_items = db.execute('''SELECT items.* FROM items
                        WHERE items.item = ?''', (searched,)).fetchall()
        
        return render_template("storganize_templates/search.html", form=form, searched=searched, items=user_items)