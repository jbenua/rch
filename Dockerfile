FROM python:3.6
EXPOSE 5000
WORKDIR /app
COPY requirements.txt /app
RUN pip install -r requirements.txt

COPY . /app
CMD FLASK_APP=tasks/task3/app.py python -m flask run --host=0.0.0.0
