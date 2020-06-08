from webapp import create_app
from webapp.db import db
from webapp.catalog.models import Catalog
from webapp.user.models import User

app = create_app()

with app.app_context():
    if not User.query.count():
        users = ['admin', 'user']
        for username in users:
            if not User.query.filter_by(username=username).count():
                if username == 'admin':
                    new_user = User(username=username, role='admin')
                else:
                    new_user = User(username=username, role='user')
                new_user.set_password(username)
                db.session.add(new_user)
                print(f'Добавлен пользователь {username}')
        db.session.commit()

    if not Catalog.query.count():
        catalog = {'Фрукты, овощи, ягоды':
                   {'Фрукты': ['Бананы', 'Яблоки', 'Авокадо'],
                    'Овощи': ['Огурцы', 'Помидоры', 'Дайкон', 'Картофель', 'Лук', 'Морковь'],
                    'Ягоды': ['Малина', 'Черника', 'Виктория']
                    },
                   'Молоко, сыр, яйца':
                   {'Молочная продукция': ['Молоко', 'Сливки', 'Кефир', 'Сливочное масло'],
                    'Сыры': ['Твердые сыры', 'Творожные сыры', 'Копченые сыры'],
                    'Яйца': []
                    },
                   'Макароны, крупы, масло, консервы':
                   {'Макаронные изделия': ['Паста', 'Рожки'],
                    'Крупы': ['Рис', 'Греча', 'Чечевица'],
                    'Масло': ['Растительное масло', 'Кукурузное масло'],
                    'Консервы': ['Рыбные консервы', 'Мясные консервы', 'Фруктовые консервы']
                    }
                   }
        for key_0, value_0 in catalog.items():
            level_0 = Catalog.query.filter_by(name=key_0).first()
            if not level_0:
                level_0 = Catalog(name=key_0, parent_id=None, level=0)
                db.session.add(level_0)
                print(f'Добавлен каталог {key_0}')
            for key_1, value_1 in value_0.items():
                level_1 = Catalog.query.filter_by(name=key_1).first()
                if not level_1:
                    level_1 = Catalog(name=key_1, parent_id=level_0.id, level=1)
                    db.session.add(level_1)
                    print(f'Добавлен каталог {key_1}')
                for key_2 in value_1:
                    if not Catalog.query.filter_by(name=key_2).count():
                        level_2 = Catalog(name=key_2, parent_id=level_1.id, level=2)
                        db.session.add(level_2)
                        print(f'Добавлен каталог {key_2}')
        db.session.commit()

    print('Обновление данных завершено!')
