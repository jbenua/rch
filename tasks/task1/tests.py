import unittest

from copy import deepcopy

from .nest import group_by_key


ITEMS = [
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
]


def pop_random_keys(items):
    safe_items = deepcopy(items)
    for index, item in enumerate(safe_items):
        item.pop(list(item.keys())[index])
    return safe_items


class TestNest(unittest.TestCase):

    def test_empty_nesting_keys(self):
        """Return data as is when passed empty array of nesting keys"""
        self.assertEqual(
            ITEMS, group_by_key(ITEMS, []),
            msg="Somehow items changed"
        )

    def test_missing_keys(self):
        """Fails whe passed the unknown key"""
        with self.assertRaises(KeyError):
            group_by_key(
                ITEMS,
                ["currency", "language"]
            )

    def test_quantum_keys(self):
        """
        Fails, when passed an array of items without constant set of keys:
        some keys will be missing
        """
        items = pop_random_keys(ITEMS)
        with self.assertRaises(KeyError):
            group_by_key(
                items,
                ["currency", "country", "city"]
            )

    def test_duplicated_keys(self):
        """
        Works ok when passed duplicated nested keys:
        after first appearance one can still group items by this key
        (strange case, but why not?)
        """

        self.assertEqual({
            "USD": {
                "US": {
                    "USD": [{
                        "city": "Boston",
                        "amount": 100
                    }]
                }
            },
            "EUR": {
                "FR": {
                    "EUR": [{
                        "city": "Paris",
                        "amount": 20
                    }, {
                        "city": "Lyon",
                        "amount": 11.4
                    }]
                }
            }
        }, group_by_key(
            ITEMS,
            ["currency", "country", "currency"]
        ), msg="Failed to group by the same key twice"
        )

    def test_all_the_keys(self):
        """Return data as is when passed empty array of nesting keys"""
        self.assertEqual({
            "USD": {
                "US": {
                    "Boston": 100
                }
            },
            "EUR": {
                "FR": {
                    "Paris": 20,
                    "Lyon": 11.4,
                }
            }
        }, group_by_key(
            ITEMS, ['currency', 'country', 'city', 'amount']),
            msg="Didnt unnest properly"
        )


if __name__ == "__main__":
    unittest.main()
