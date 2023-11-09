FROM python:3.8-alpine

COPY Pipfile Pipfie .

RUN cd SQLQueries/ && pip install pipenv && pipenv install && pipenv shell && cd web_app \
    && python manage.py migrate app && python manage.py migrate trade --database postgres_trade  \
    && python manage.py loaddata main_fixture && python manage.py loaddata trade_fixrure.json --database postgres_trade

EXPOSE 8000
COPY . .
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
