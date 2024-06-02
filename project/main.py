from flask import Blueprint, render_template, request, flash, redirect, url_for, send_from_directory, current_app
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename
import imghdr
import os
from .forms import CommentForm, UploadForm, EditForm, CategoryForm
from .models import Photo, Comment, Category
from . import db

main = Blueprint('main', __name__)

def get_category_choices():
    return [(category.id, category.name) for category in Category.query.all()]

@main.route('/')
def homepage():
    photos = db.session.query(Photo).order_by(Photo.file.asc()).all()
    return render_template('index.html', photos=photos)

@main.route('/uploads/<name>')
def display_file(name):
    return send_from_directory(current_app.config["UPLOAD_DIR"], name)

@main.route('/upload/', methods=['GET', 'POST'])
@login_required
def newPhoto():
    form = UploadForm()
    form.categories.choices = get_category_choices()
    if form.validate_on_submit():
        file = form.fileToUpload.data
        filename = secure_filename(file.filename)

        file.seek(0, os.SEEK_END)
        if file.tell() > 12 * 1024 * 1024:
            flash('File too large!', 'error')
            return redirect(url_for('main.newPhoto'))
        file.seek(0)

        file_type = imghdr.what(file)
        if file_type not in ['jpeg', 'png', 'gif']:
            flash('Invalid image format!', 'error')
            return redirect(url_for('main.newPhoto'))

        file.save(os.path.join(current_app.config["UPLOAD_DIR"], filename))

        new_photo = Photo(
            name=form.user.data,
            caption=form.caption.data,
            description=form.description.data,
            file=filename,
            user_id=current_user.id
        )
        new_photo.categories = Category.query.filter(Category.id.in_(form.categories.data)).all()
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
    form.categories.choices = get_category_choices()
    if form.validate_on_submit():
        photo.name = request.form['user']
        photo.caption = request.form['caption']
        photo.description = request.form['description']
        photo.categories = Category.query.filter(Category.id.in_(form.categories.data)).all()
        db.session.commit()
        flash(f'Photo Successfully Edited {photo.name}', 'success')
        return redirect(url_for('main.homepage'))

    form.categories.data = [category.id for category in photo.categories]
    return render_template('edit.html', form=form, photo=photo)

@main.route('/photo/<int:photo_id>/delete/', methods=['POST'])
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

@main.route('/photo/<int:photo_id>/comment', methods=['POST'])
@login_required
def create_comment(photo_id):
    form = CommentForm()
    if form.validate_on_submit():
        new_comment = Comment(content=form.content.data, user_id=current_user.id, photo_id=photo_id)
        db.session.add(new_comment)
        db.session.commit()
        flash('Comment posted successfully!', 'success')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"Error in the {getattr(form, field).label.text} field - {error}", 'error')
    return redirect(url_for('main.view_photo', photo_id=photo_id))

@main.route('/photo/<int:photo_id>')
def view_photo(photo_id):
    photo = Photo.query.get_or_404(photo_id)
    form = CommentForm()
    return render_template('photo.html', photo=photo, form=form)

@main.route('/category/<int:category_id>')
def view_category(category_id):
    category = Category.query.get_or_404(category_id)
    photos = category.photos
    return render_template('category.html', category=category, photos=photos)

@main.route('/categories')
def list_categories():
    categories = Category.query.all()
    return render_template('categories.html', categories=categories)

@main.route('/add_category', methods=['GET', 'POST'])
@login_required
def add_category():
    form = CategoryForm()
    if form.validate_on_submit():
        category = Category(name=form.name.data)
        db.session.add(category)
        db.session.commit()
        flash('New category added!', 'success')
        return redirect(url_for('main.list_categories'))
    return render_template('add_category.html', form=form)