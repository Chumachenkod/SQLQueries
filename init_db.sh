#!/bin/bash

python manage.py migrate app
python manage.py migrate trade --database postgres_trade
python manage.py loaddata main_fixture && python manage.py loaddata trade_fixrure.json --database postgres_trade
