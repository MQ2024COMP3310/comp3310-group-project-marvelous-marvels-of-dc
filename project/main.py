from flask import Blueprint, render_template, request, flash, redirect, url_for, send_from_directory, current_app
from flask_login import current_user, login_required
from sqlalchemy import asc
from werkzeug.utils import secure_filename
import imghdr
import os
from .models import Photo
from .forms import UploadForm, EditForm
from . import db

main = Blueprint('main', __name__)

@main.route('/')
def homepage():
    photos = db.session.query(Photo).order_by(asc(Photo.file)).all()
    return render_template('index.html', photos=photos)

@main.route('/uploads/<name>')
def display_file(name):
    return send_from_directory(current_app.config["UPLOAD_DIR"], name)

@main.route('/upload/', methods=['GET', 'POST'])
@login_required
def newPhoto():
    form = UploadForm()
    if form.validate_on_submit():
        file = form.fileToUpload.data
        filename = secure_filename(file.filename)

        file.seek(0, os.SEEK_END)
        if file.tell() > 12 * 1024 * 1024:
            flash('File too large!', 'error')
            return redirect(request.url)
        file.seek(0)

        file_type = imghdr.what(file)
        if file_type not in ['jpeg', 'png', 'gif']:
            flash('Invalid image format!', 'error')
            return redirect(request.url)

        file.save(os.path.join(current_app.config["UPLOAD_DIR"], filename))

        new_photo = Photo(
            name=form.user.data,
            caption=form.caption.data,
            description=form.description.data,
            file=filename,
            user_id=current_user.id
        )
        db.session.add(new_photo)
        db.session.commit()
        flash(f'New Photo {new_photo.name} Successfully Created', 'success')
        return redirect(url_for('main.homepage'))

    return render_template('upload.html', form=form)

@main.route('/photo/<int:photo_id>/edit/', methods=['GET', 'POST'])
@login_required
def editPhoto(photo_id):
    photo = db.session.query(Photo).filter_by(id=photo_id).one()
    if photo.user_id != current_user.id and not current_user.is_admin:
        flash('You do not have permission to edit this photo.', 'error')
        return redirect(url_for('main.homepage'))
    
    form = EditForm(obj=photo)
    if form.validate_on_submit():
        photo.name = request.form['user']
        photo.caption = request.form['caption']
        photo.description = request.form['description']
        db.session.commit()
        flash(f'Photo Successfully Edited {photo.name}', 'success')
        return redirect(url_for('main.homepage'))
    
    return render_template('edit.html', form=form, photo=photo)


# This is called when clicking on Delete. 
@main.route('/photo/<int:photo_id>/delete/', methods=['GET','POST'])
@login_required
def deletePhoto(photo_id):
    photo = Photo.query.get_or_404(photo_id)

    if photo.user_id != current_user.id and not current_user.is_admin:
        flash('You do not have permission to delete this photo', 'error')
        return redirect(url_for('main.homepage'))

    db.session.delete(photo)
    db.session.commit()
    flash('Photo Successfully Deleted', 'success')
    return redirect(url_for('main.homepage'))