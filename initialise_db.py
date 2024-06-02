import os
from project import db, create_app, models
from project.models import Photo, User, Category
from werkzeug.security import generate_password_hash
from dotenv import load_dotenv

load_dotenv()

def populate_db():
    session = db.session()

    # Create Users
    user1 = User(username='user1', password=generate_password_hash('password1', method='pbkdf2:sha256', salt_length=int(os.getenv('SALTING_ROUNDS'))), is_admin=True)
    user2 = User(username='user2', password=generate_password_hash('password2', method='pbkdf2:sha256', salt_length=int(os.getenv('SALTING_ROUNDS'))), is_admin=False)
    user3 = User(username='user3', password=generate_password_hash('password3', method='pbkdf2:sha256', salt_length=int(os.getenv('SALTING_ROUNDS'))), is_admin=False)
    
    # Adding Users to the Session
    session.add(user1)
    session.add(user2)
    session.add(user3)
    session.commit()  # Commit to assign IDs
    
    # Create Categories
    categories = ['Nature', 'Animals', 'Technology', 'People', 'Sports']
    category_objs = [Category(name=category) for category in categories]
    session.add_all(category_objs)
    session.commit()  # Commit to assign IDs

    # Now Create Photos with a reference to the user id
    photos = [
        Photo(name='William Warby', caption='Gentoo penguin', description='A penguin with an orange beak standing next to a rock.', file='william-warby-_A_vtMMRLWM.jpg', user_id=user1.id),
        Photo(name='Javier Patino Loira', caption='Common side-blotched lizard', description='A close up of a lizard on a rock.', file='javier-patino-loira-nortqDjv7ak.jpg', user_id=user1.id),
        Photo(name='Jordie Rubies', caption='Griffin vulture flying', description='A large bird flying through a blue sky.', file='jordi-rubies-2wNkdL2oIyU.jpg', user_id=user2.id),
        Photo(name='Jakub Neskora', caption='Jaguar', description='A close up of a leopard near a rock.', file='jakub-neskora-jloJvr74Fcc.jpg', user_id=user2.id),
        Photo(name='William Warby', caption='Japanese macaque', description='A monkey sitting on top of a wooden post.', file='william-warby-ndWikw_TPfc.jpg', user_id=user3.id),
        Photo(name='Ahmed Ali', caption='Berlin', description='An exciting part of Berlin. This place covers so many beautiful attractions in the city.', file='ahmed-ali-Zl7bVVMEfg.jpg', user_id=user3.id),
        Photo(name='Hanvin Cheong', caption='Nakano', description='A group of people walking across a street.', file='hanvin-cheong-9rBj8QYOL1Q.jpg', user_id=user1.id),
        Photo(name='Ekaterina Bogdan', caption='Bologna', description='A bike parked next to a pole.', file='ekaterina-bogdan-BKJWsGB5h1s.jpg', user_id=user2.id),
        Photo(name='Damian Ochrymowicz', caption='Nazare, Portugal', description='', file='damian-ochrymowicz-GZQ7tKmEd9c.jpg', user_id=user3.id),
        Photo(name='Dima DallAcqua', caption='Alcatraz Island', description='A close up of a green plant.', file='dima-dallacqua-U8TAGVPFJc4.jpg', user_id=user1.id),
        Photo(name='Edgar', caption='Oporto, Portugal', description='A man sitting on a bench at a train station.', file='edgar-Q0g5Thf7Ank.jpg', user_id=user2.id),
    ]

    # Adding All Photos to the Session
    session.add_all(photos)
    session.commit()

    # Associating photos to categories
    photo_category_mappings = {
        'Nature': [1, 2, 10],
        'Animals': [1, 2, 4],
        'People': [7, 11],
        'Sports': [9],
        'Technology': [],
    }
    
    for category_name, photo_ids in photo_category_mappings.items():
        category = Category.query.filter_by(name=category_name).first()
        for photo_id in photo_ids:
            photo = session.get(Photo, photo_id)  # Using Session.get() instead of Query.get()
            photo.categories.append(category)
    
    session.commit()

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        db.drop_all()
        db.create_all()
        populate_db()