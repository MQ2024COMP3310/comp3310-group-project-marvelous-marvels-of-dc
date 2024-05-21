from flask import (
  Blueprint, render_template, request, 
  flash, redirect, url_for, send_from_directory, 
  current_app, make_response
)
from flask_login import current_user, login_required
from .models import Photo, Comment
from sqlalchemy import asc, text
from . import db
import os

main = Blueprint('main', __name__)

# This is called when the home page is rendered. It fetches all images sorted by filename.
@main.route('/')
def homepage():
  photos = db.session.query(Photo).order_by(asc(Photo.file))
  return render_template('index.html', photos = photos)

@main.route('/uploads/<name>')
def display_file(name):
  return send_from_directory(current_app.config["UPLOAD_DIR"], name)

from werkzeug.utils import secure_filename
import imghdr

@main.route('/upload/', methods=['GET','POST'])
@login_required
def newPhoto():
    if request.method == 'POST':
        file = request.files.get("fileToUpload")
        
        if not file:
            flash("No file selected!", "error")
            return redirect(request.url)

        # Secure filename path
        filename = secure_filename(file.filename)

        # File size check 12MB
        file.seek(0, os.SEEK_END)
        file_length = file.tell()
        if file_length > 12 * 1024 * 1024:
            flash("File too large!", "error")
            return redirect(request.url)
        file.seek(0)

        # Check file type
        file_type = imghdr.what(file)
        if file_type not in ['jpeg', 'png', 'gif']:
            flash("Invalid image format!", "error")
            return redirect(request.url)

        file.save(os.path.join(current_app.config["UPLOAD_DIR"], filename))

        new_photo = Photo(name=request.form['user'], 
                          caption=request.form['caption'],
                          description=request.form['description'],
                          file=filename,
                          user_id=current_user.id)
        
        db.session.add(new_photo)
        flash(f'New Photo {new_photo.name} Successfully Created')
        db.session.commit()
        return redirect(url_for('main.homepage'))
    else:
        return render_template('upload.html')

# This is called when clicking on Edit. Goes to the edit page.
@main.route('/photo/<int:photo_id>/edit/', methods=['GET', 'POST'])
@login_required
def editPhoto(photo_id):
    editedPhoto = db.session.query(Photo).filter_by(id=photo_id).one()
    if request.method == 'POST':
        if 'user' in request.form and 'caption' in request.form and 'description' in request.form:
            editedPhoto.name = request.form['user']
            editedPhoto.caption = request.form['caption']
            editedPhoto.description = request.form['description']
            db.session.commit()
            flash(f'Photo Successfully Edited {editedPhoto.name}')
            return redirect(url_for('main.homepage'))
        else:
            flash('Missing form fields.', 'error')
            return redirect(url_for('main.editPhoto', photo_id=photo_id))

    return render_template('edit.html', photo=editedPhoto)


# This is called when clicking on Delete. 
@main.route('/photo/<int:photo_id>/delete/', methods=['GET','POST'])
@login_required
def deletePhoto(photo_id):
    photo = Photo.query.get_or_404(photo_id)

    if photo.user_id == current_user.id or current_user.is_admin:
        db.session.delete(photo)
        db.session.commit()
        flash('Photo Successfully Deleted')
        return redirect(url_for('main.homepage'))
    else:
        flash('You do not have permission to delete this photo', 'error')
        return redirect(url_for('main.homepage'))


# This is called when clicking on Comment. Goes to the comment page.
@main.route('/photo/<int:photo_id>/comment', methods=['POST'])
@login_required
def create_comment(photo_id):
    content = request.form.get('content')
    if not content:
        flash('Comment cannot be empty', 'error')
    else:
        new_comment = Comment(content=content, user_id=current_user.id, photo_id=photo_id)
        db.session.add(new_comment)
        db.session.commit()
        flash('Comment posted successfully!', 'success')
    return redirect(url_for('main.view_photo', photo_id=photo_id))

@main.route('/photo/<int:photo_id>')
def view_photo(photo_id):
    photo = Photo.query.get_or_404(photo_id)
    return render_template('photo.html', photo=photo)