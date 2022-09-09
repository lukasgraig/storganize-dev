from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from storganize.auth import login_required
from storganize.db import get_db
from storganize.createqr import CreateQR
from storganize.forms import CreateBoxForm

bp = Blueprint('storage', __name__)

@bp.route('/')
def index():
    return render_template('storganize_templates/index.html')

@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_box():
    form = CreateBoxForm()

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
    posts = db.execute('''SELECT * FROM storage_box
                    WHERE storage_box.username = ?''', (g.user['username'],)).fetchall()
    
    return render_template('storganize_templates/myboxes.html', posts=posts)

@bp.route('/view/<uuid>', methods=['GET'])
@login_required
def view(uuid, check_author=True):
    info, items = get_post(uuid)

    if check_author and info['username'] != g.user['username']:
        abort(403, render_template('storganize_templates/notfound.html'))
    if not info:
        abort(404, render_template('storganize_template/notfound.html'))

    filename = g.user['username'] + '-' + uuid + '.png'
    return render_template('storganize_templates/viewbox.html', info=info, items=items, img=filename)

def get_post(uuid):
    db = get_db()
    
    info = db.execute('''SELECT * FROM storage_box
                    WHERE storage_box.uuid = ?''', (uuid,)).fetchone()
    
    items = db.execute('''SELECT items.* FROM items
                        WHERE items.uuid = ?''', (uuid,)).fetchall()

    return info, items

@bp.route('/<uuid>/update', methods=['GET', 'POST'])
@login_required
def update(uuid):
    info, items = get_post(uuid)

    if request.method == 'POST':
        box_title = request.form['box_title']
        box_desc = request.form['box_desc']
        box_type = request.form['box_type']
        item = request.form['box_item']

        error = None

        if not box_title:
           error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE storage_box (box_type, box_title, box_desc)'
                ' VALUES (?, ?, ?) WHERE uuid = ?',
                (box_type, box_title, box_desc, uuid))
            db.commit()
            return redirect(url_for('storage.index'))

    return render_template('storganize_templates/update.html', info=info, items=items)

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
    return redirect(url_for('storage.box_list'))
