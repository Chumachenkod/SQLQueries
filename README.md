Для початку потрібно встановити необхідне П.З.:
1. Docker-Compose
2. Python

Після цього необхідно завантажити своє фото за цим шляхом: web_app/app/avatars та назвати його 1.jpg

Для того щоб запустити програму, треба ввести такі команди:
1. cd SQLQueries/
2. pip install pipenv
3. pipenv install
4. docker-compose up -d
5. pipenv shell
6. cd web_app
7. python manage.py migrate app
8. python manage.py migrate trade --database postgres_trade
9. python manage.py loaddata main_fixture
10. python manage.py loaddata trade_fixrure.json --database postgres_trade
11. python manage.py runserver

Після цього програма почне працювати за адресою: localhost:8000
логін/пароль для входу: admin@gmail.com/password
