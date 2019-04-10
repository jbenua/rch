# Revolut challenge

## Installation
```
virtualenv .env
. .env/bin/activate
pip install -r requirements.txt
```

or as alternative (task 3 only)

```
docker-compose build
```

## Testing 
```
green
```
or

```
python -m tasks.task1.tests
python -m tasks.task2.tests
python -m tasks.task3.tests
```


## Usage

### Task 1
```cat data.json |  python tasks/task1/nest.py country```

### Task 2
Run the app:
```FLASK_APP=tasks/task2/app.py python -m flask run```

### Task 3
Set up the db...
```
mysql [...db credentials] < dump.sql
```
... and run the app:
```
FLASK_APP=tasks/task3/app.py python -m flask run
```

or 

simply run
```
docker-compose up
```


