# Revolut challenge

## Installation
```
virtualenv .env
. .env/bin/activate
pip install -r requirements.txt
```

## Testing 
```
green
```
or

```
python -m tasks.task1.tests
python -m tasks.task2.tests
```


## Usage

### Task 1
```cat data.json |  python tasks/task1/nest.py country```

### Task 2
Run app:
```FLASK_APP=tasks/task2/app.py python -m flask run```

### Task 3
Set up db:
```mysql [...db credentials] < dump.sql```

Run app:
```FLASK_APP=tasks/task3/app.py python -m flask run```
