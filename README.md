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
```FLASK_APP=tasks/task2/app.py python -m flask run```
