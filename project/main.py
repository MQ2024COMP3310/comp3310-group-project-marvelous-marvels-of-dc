# Importing necessary libraries and modules.
from flask import Blueprint, render_template, request, flash, redirect, url_for, send_from_directory, current_app
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename
import imghdr
import os
from .forms import CommentForm, UploadForm, EditForm, CategoryForm
from .models import Photo, Comment, Category
from . import db

# Defining the blueprint for main routes.
main = Blueprint('main', __name__)

# Utility function to get category choices for forms.
def get_category_choices():
    return [(category.id, category.name) for category in Category.query.all()]

# Homepage route, displays all photos.
@main.route('/')
def homepage():
    photos = db.session.query(Photo).order_by(Photo.file.asc()).all()
    return render_template('index.html', photos=photos)

# Endpoint to display an uploaded file.
@main.route('/uploads/<name>')
def display_file(name):
    return send_from_directory(current_app.config["UPLOAD_DIR"], name)

# Route to upload new photos, requires login.
@main.route('/upload/', methods=['GET', 'POST'])
@login_required
def newPhoto():
    form = UploadForm()
    form.categories.choices = get_category_choices()
    
    # Validate form submission
    if form.validate_on_submit():
        file = form.fileToUpload.data
        filename = secure_filename(file.filename)

        # Check file size (mitigation against denial of service attacks)
        file.seek(0, os.SEEK_END)
        if file.tell() > 12 * 1024 * 1024:
            flash('File too large!', 'error')
            return redirect(url_for('main.newPhoto'))
        file.seek(0)

        # Check file format (mitigation against insecure formats)
        file_type = imghdr.what(file)
        if file_type not in ['jpeg', 'png', 'gif']:
            flash('Invalid image format!', 'error')
            return redirect(url_for('main.newPhoto'))

        # Save the file
        file.save(os.path.join(current_app.config["UPLOAD_DIR"], filename))

        # Create new photo database record
        new_photo = Photo(
            name=form.user.data,
            caption=form.caption.data,
            description=form.description.data,
            file=filename,
            user_id=current_user.id
        )
        
        # Add categories to the photo
        new_photo.categories = Category.query.filter(Category.id.in_(form.categories.data)).all()
        db.session.add(new_photo)
        db.session.commit()
        flash(f'New Photo {new_photo.name} Successfully Created', 'success')
        return redirect(url_for('main.homepage'))

    return render_template('upload.html', form=form)

# Route to edit a photo, requires login.
@main.route('/photo/<int:photo_id>/edit/', methods=['GET', 'POST'])
@login_required
def editPhoto(photo_id):
    photo = db.session.query(Photo).filter_by(id=photo_id).one()

    # Ensure the user has permission to edit the photo (authorization check)
    if photo.user_id != current_user.id and not current_user.is_admin:
        flash('You do not have permission to edit this photo.', 'error')
        return redirect(url_for('main.homepage'))

    form = EditForm(obj=photo)
    form.categories.choices = get_category_choices()
    
    # Validate form submission
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

# Route to delete a photo, requires login.
@main.route('/photo/<int:photo_id>/delete/', methods=['POST'])
@login_required
def deletePhoto(photo_id):
    photo = Photo.query.get_or_404(photo_id)

    # Ensure the user has permission to delete the photo (authorization check)
    if photo.user_id != current_user.id and not current_user.is_admin:
        flash('You do not have permission to delete this photo', 'error')
        return redirect(url_for('main.homepage'))

    db.session.delete(photo)
    db.session.commit()
    flash('Photo Successfully Deleted', 'success')
    return redirect(url_for('main.homepage'))

# Route to create a comment on a photo, requires login.
@main.route('/photo/<int:photo_id>/comment', methods=['POST'])
@login_required
def create_comment(photo_id):
    form = CommentForm()
    
    # Validate form submission
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

# Route to view a particular photo.
@main.route('/photo/<int:photo_id>')
def view_photo(photo_id):
    photo = Photo.query.get_or_404(photo_id)
    form = CommentForm()
    return render_template('photo.html', photo=photo, form=form)

# Route to view photos in a particular category.
@main.route('/category/<int:category_id>')
def view_category(category_id):
    category = Category.query.get_or_404(category_id)
    photos = category.photos
    return render_template('category.html', category=category, photos=photos)

# Route to list all categories.
@main.route('/categories')
def list_categories():
    categories = Category.query.all()
    return render_template('categories.html', categories=categories)

# Route to add a new category, requires login.
@main.route('/add_category', methods=['GET', 'POST'])
@login_required
def add_category():
    form = CategoryForm()
    
    # Validate form submission
    if form.validate_on_submit():
        category = Category(name=form.name.data)
        db.session.add(category)
        db.session.commit()
        flash('New category added!', 'success')
        return redirect(url_for('main.list_categories'))
    return render_template('add_category.html', form=form)