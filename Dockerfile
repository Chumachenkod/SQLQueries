FROM tensorflow/tensorflow:2.8.0

COPY Pipfile .
COPY Pipfile.lock .

RUN apt install -y make automake gcc g++ subversion python3-dev

RUN pip install pipenv && pipenv install --system

RUN apt-get update && apt-get install ffmpeg libsm6 libxext6  -y

COPY . .

WORKDIR web_app

EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
