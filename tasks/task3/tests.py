import base64
import json
import unittest
import time
from pathlib import Path
from copy import deepcopy
from flask_mysqldb import MySQL
import yaml
try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader


from .app import app
path = Path('.').resolve()


app.config['TESTING'] = True
app.config['WTF_CSRF_ENABLED'] = False
app.config['DEBUG'] = False

path = Path('.').resolve()
with open(f'{path}/etc/task3_config.yaml') as config:
    app.config.update(yaml.load(config.read(), Loader=Loader))
VALID_CREDENTIALS = base64.b64encode(
    '{}:{}'.format(
        app.config['BASIC_AUTH_USERNAME'],
        app.config['BASIC_AUTH_PASSWORD']
    ).encode()).decode('utf-8')
HEADERS = {
    'Authorization': f'BASIC {VALID_CREDENTIALS}',
    'Content-Type': 'application/json'
}

db = MySQL()


with app.app_context():
    with db.connection.cursor() as cursor:
        cursor.execute(
            '''SELECT id, country, city, currency, amount FROM deposits LIMIT 1''')
        res = cursor.fetchone()

RANDOM_ROW = dict(
    zip(['id', 'country', 'city', 'currency', 'amount'], res))


# TODO set up and tear down db with data for proper testing


class TestListDeposits(unittest.TestCase):

    def test_get_no_auth(self):
        """Get list without auth fails"""
        response = app.test_client().get('/api/v1/deposit')
        self.assertEqual(response.status_code, 401, msg="Success without auth")

    def test_get_auth_ok(self):
        """Simple list is ok"""
        with app.app_context():
            with db.connection.cursor() as cursor:
                cursor.execute('''
                    SELECT count(*)
                    FROM deposits
                ''')
                res = cursor.fetchone()[0]

        response = app.test_client().get(
            '/api/v1/deposit', headers=HEADERS
        )
        self.assertEqual(response.status_code, 200,
                         msg="Fail getting deposits")
        self.assertEqual(
            len(json.loads(response.get_data()).get('data')),
            res,
            msg="Returned wrong number of deposits"
        )


class TestCreateDeposit(unittest.TestCase):
    def test_create_no_auth(self):
        """Get list without auth fails"""
        response = app.test_client().post('/api/v1/deposit', data={})
        self.assertEqual(response.status_code, 401, msg="Success without auth")

    def test_simple_create(self):
        """Simple create"""
        data = {
            "country": "RU",
            "city": str(time.mktime(time.gmtime())),
            "currency": "RUR"
        }
        response = app.test_client().post(
            '/api/v1/deposit',
            headers=HEADERS,
            data=json.dumps(data))
        self.assertEqual(200, response.status_code, msg="Fail to post ok data")
        with app.app_context():
            with db.connection.cursor() as cursor:
                cursor.execute('''
                    SELECT *
                    FROM deposits
                    WHERE
                        country=%(country)s and
                        city=%(city)s and
                        currency=%(currency)s
                ''', data)
                res = cursor.fetchone()
        self.assertIsNotNone(res, msg="Nothing appeared in db")

    def test_create_duplicate(self):
        """Cannot create dumplicate"""
        r = deepcopy(RANDOM_ROW)
        r.pop('id')
        r.pop('amount')
        response = app.test_client().post(
            '/api/v1/deposit',
            headers=HEADERS,
            data=json.dumps(r))
        self.assertEqual(400, response.status_code,
                         msg="Succeded to post duplicate")


class TestDepositAPI(unittest.TestCase):

    def test_get_no_auth(self):
        """Cannot get anything without auth"""
        id_ = RANDOM_ROW['id']
        response = app.test_client().get(f'/api/v1/deposit/{id_}')
        self.assertEqual(response.status_code, 401, msg="Success without auth")

    def test_simple_get(self):
        """Cannot get anything without auth"""
        id_ = RANDOM_ROW['id']
        d = deepcopy(RANDOM_ROW)
        d.pop('id')
        response = app.test_client().get(
            f'/api/v1/deposit/{id_}',
            headers=HEADERS
        )
        self.assertEqual(response.status_code, 200, msg="Unknown error")
        self.assertEqual(
            json.loads(response.get_data())['data'],
            d, msg="Got something strange"
        )

    def test_get_nonexisting(self):
        """Get somethin that doesnt exist fails"""
        with app.app_context():
            with db.connection.cursor() as cursor:
                cursor.execute('''
                    SELECT max(id)
                    FROM deposits''')
                res = cursor.fetchone()[0]
        response = app.test_client().get(
            f'/api/v1/deposit/{res + 1}',
            headers=HEADERS
        )
        self.assertEqual(response.status_code, 404,
                         msg="Succeded to get something")

    def test_delete_no_auth(self):
        """Cannot delete anything without auth"""
        id_ = RANDOM_ROW['id']
        response = app.test_client().delete(f'/api/v1/deposit/{id_}')
        self.assertEqual(response.status_code, 401, msg="Success without auth")

    def test_delete_nonexisting(self):
        """Delete somethin that doesnt exist fails"""
        with app.app_context():
            with db.connection.cursor() as cursor:
                cursor.execute('''
                    SELECT max(id)
                    FROM deposits''')
                res = cursor.fetchone()[0]
        response = app.test_client().delete(
            f'/api/v1/deposit/{res + 1}',
            headers=HEADERS
        )
        self.assertEqual(response.status_code, 400,
                         msg="Succeded to delete something")

    def test_delete(self):
        """Regular delete works ok"""
        with app.app_context():
            with db.connection.cursor() as cursor:
                cursor.execute('''
                    INSERT INTO deposits
                    (country, city, currency, amount)
                    VALUES ("russiaa", "moscowww", "rur", 100)
                ''')
                res = cursor.fetchone()
                id_ = cursor.lastrowid
            db.connection.commit()

        response = app.test_client().delete(
            f'/api/v1/deposit/{id_}',
            headers=HEADERS
        )
        self.assertEqual(response.status_code, 200,
                         msg="Failed to delete deposit")
        with app.app_context():
            with db.connection.cursor() as cursor:
                cursor.execute('''
                    SELECT *
                    FROM deposits
                    WHERE id=%s
                ''', (id_,))
            res = cursor.fetchone()
        self.assertIsNone(res, msg="Didnt delete anything from db")

    def test_update_no_auth(self):
        """Cannot update anything without auth"""
        id_ = RANDOM_ROW['id']
        response = app.test_client().post(f'/api/v1/deposit/{id_}')
        self.assertEqual(response.status_code, 401, msg="Success without auth")

    def test_update_no_body(self):
        """Cannot update anything without body"""
        id_ = RANDOM_ROW['id']
        response = app.test_client().post(
            f'/api/v1/deposit/{id_}',
            data={},
            headers=HEADERS)
        self.assertEqual(
            response.status_code, 400,
            msg="Success to update with empty data")

    def test_update_wrong_body(self):
        """Cannot update anything with wrong body"""
        id_ = RANDOM_ROW['id']
        response = app.test_client().post(
            f'/api/v1/deposit/{id_}',
            data={'amount': 'lkjuytfghj'},
            headers=HEADERS)
        self.assertEqual(
            response.status_code, 400,
            msg="Success to update with invalid data")

    def test_update_ok(self):
        """Proper update works correct"""
        id_ = RANDOM_ROW['id']
        new_amount = RANDOM_ROW['amount'] * -1
        response = app.test_client().post(
            f'/api/v1/deposit/{id_}',
            data=json.dumps({'amount': new_amount}),
            headers=HEADERS
        )
        self.assertEqual(response.status_code, 200, msg="Failed to update")
        with app.app_context():
            with db.connection.cursor() as cursor:
                cursor.execute('''
                    SELECT amount
                    FROM deposits
                    WHERE id=%s''', (id_,))
                res = cursor.fetchone()[0]

        self.assertEqual(new_amount, res, msg="Didnt update deposit")


if __name__ == "__main__":
    unittest.main()
