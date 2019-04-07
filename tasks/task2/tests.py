import base64
import json
import unittest


from .app import app


VALID_CREDENTIALS = base64.b64encode(
    '{}:{}'.format(
        app.config['BASIC_AUTH_USERNAME'],
        app.config['BASIC_AUTH_PASSWORD']
    ).encode()).decode('utf-8')


class TestAPI(unittest.TestCase):
    def test_no_auth(self):
        """Getting something without auth fails"""
        response = app.test_client().post('/', data={})
        self.assertEqual(
            response.status_code, 401,
            msg="Basic auth lets get through!"
        )

    def test_auth_ok(self):
        """Everything is ok"""
        response = app.test_client().post(
            '/',
            headers={
                'Authorization': f'BASIC {VALID_CREDENTIALS}',
                'Content-Type': 'application/json'
            },
            data=json.dumps({
                'data': [
                    {
                        "country": "US",
                        "city": "Boston",
                        "currency": "USD",
                        "amount": 100
                    },
                    {
                        "country": "FR",
                        "city": "Paris",
                        "currency": "EUR",
                        "amount": 20
                    },
                    {
                        "country": "FR",
                        "city": "Lyon",
                        "currency": "EUR",
                        "amount": 11.4
                    }
                ], 'nesting_keys': ['currency', 'country', 'city']
            })
        )
        self.assertEqual(
            response.status_code, 200,
            msg="Failed to get ok response"
        )
        self.assertEqual(json.loads(response.get_data()), {
            "USD": {
                "US": {
                    "Boston": [{
                        "amount": 100
                    }]
                }
            },
            "EUR": {
                "FR": {
                    "Paris": [{
                        "amount": 20
                    }],
                    "Lyon": [{
                        "amount": 11.4
                    }]
                }
            }
        })


if __name__ == "__main__":
    unittest.main()
