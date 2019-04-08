import json

from flask import Blueprint, request, current_app
from flask.views import MethodView

from ..task1.nest import group_by_key


deposit_api = Blueprint('deposit_api', __name__)
db = current_app.config.db


@deposit_api.route('', methods=["GET"])
def list_deposits():
    """List all depostis"""
    # when using a `deleted` flag model,
    # we should also filter deposits to check it is not deleted
    with db.connection.cursor() as cursor:
        cursor.execute('''
            SELECT currency, country, city, amount
            FROM deposits
        ''')
        res = cursor.fetchall()
        if res:
            return json.dumps({
                "status": "OK",
                "data": [
                    dict(zip(
                        ['currency', 'country', 'city', 'amount'],
                        item
                    )) for item in res]
            })


@deposit_api.route('', methods=["POST"])
def create():
    """Create a deposit"""
    # when using a `deleted` flag model, unique key should also contain it
    # TODO validate post data
    with db.connection.cursor() as cursor:
        try:
            cursor.execute('''
                INSERT INTO deposits
                (currency, country, city)
                VALUES (%(currency)s, %(country)s, %(city)s)
            ''', request.json)
        except Exception as e:
            return json.dumps({"status": "Error", "message": str(e)})
        inserted_id = cursor.lastrowid
    db.connection.commit()
    return json.dumps({"status": "OK", "data": {"id": inserted_id}})


@deposit_api.route('/nest', methods=["POST"])
def nest():
    """
    Receive data via post, nest object according to passed keys, e.g.
    {
        "data": [{..}, {...}, ...],  # items
        "nesting_keys": ["key1", "key2", ...]
    } ->  {...}  # nested obj
    """
    data = group_by_key(request.json['data'], request.json['nesting_keys'])
    return json.dumps({"status": "OK", "data": data})


class DepositAPI(MethodView):
    def get(self, deposit_id):
        """Get deposit by id"""
        # when using a `deleted` flag model,
        # we should also filter deposits to check it is not deleted
        with db.connection.cursor() as cursor:
            cursor.execute('''
                SELECT currency, country, city, amount
                FROM deposits
                WHERE id=%s
            ''', (deposit_id,))
            res = cursor.fetchone()
            if res:
                return json.dumps({
                    "status": "OK",
                    "data": dict(zip(
                        ['currency', 'country', 'city', 'amount'],
                        res
                    ))
                })
        # TODO catch no such row

    def post(self, deposit_id):
        """Change deposit amount"""
        # when using a `deleted` flag model,
        # we should also filter deposits to check it is not deleted
        new_amount = request.json.get('amount')
        if not new_amount or not isinstance(new_amount, int):
            raise Exception
            # todo return err

        with db.connection.cursor() as cursor:
            updated = cursor.execute('''
                UPDATE deposits
                SET amount=%s
                WHERE id=%s
            ''', (new_amount, deposit_id,))
            if not updated:
                # todo catch no such item
                raise Exception
        db.connection.commit()
        return json.dumps({"status": "OK"})

    def delete(self, deposit_id):
        """Delete deposit"""
        # when using a `deleted` flag model,
        # we should also filter deposits to check it is not deleted
        db = current_app.config.db
        with db.connection.cursor() as cursor:
            # it is much better practice to set a `deleted` flag but whatever
            updated = cursor.execute('''
                DELETE FROM deposits
                WHERE id=%s
            ''', (deposit_id,))
            if not updated:
                # todo catch no such item
                raise Exception
        db.connection.commit()
        return json.dumps({"status": "OK"})


deposit_api.add_url_rule(
    '/<int:deposit_id>', view_func=DepositAPI.as_view('deposit')
)
