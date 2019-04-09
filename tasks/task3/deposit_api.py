import json

from flask import Blueprint, request
from flask.views import MethodView

from flask_mysqldb import MySQL

from ..task1.nest import group_by_key
deposit_api = Blueprint('deposit_api', __name__)
db = MySQL()


# TODO: it is a better practice to set a `deleted` flag
# instead of actually deleting rows
# with model we should also filter out `deleted=1` rows in queries


@deposit_api.route('', methods=["GET"])
def list_deposits():
    """List all depostis"""
    data = []
    with db.connection.cursor() as cursor:
        cursor.execute('''
            SELECT currency, country, city, amount
            FROM deposits
        ''')
        res = cursor.fetchall()
        if res:
            data = [
                dict(zip(
                    ['currency', 'country', 'city', 'amount'],
                    item
                )) for item in res]
    return json.dumps({
        "status": "OK",
        "data": data
    })


@deposit_api.route('', methods=["POST"])
def create():
    """Create a deposit"""
    # TODO validate post data
    with db.connection.cursor() as cursor:
        try:
            cursor.execute('''
                INSERT INTO deposits
                (currency, country, city)
                VALUES (%s, %s, %s)
            ''', (
                request.json['currency'],
                request.json['country'],
                request.json['city'],)
            )
        except Exception as e:
            return (json.dumps({"status": "Error", "message": str(e)}), 400,)
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
    try:
        data = group_by_key(request.json['data'], request.json['nesting_keys'])
    except KeyError as e:
        return (json.dumps({"status": "Error", "message": str(e)}), 400)
    return json.dumps({"status": "OK", "data": data})


class DepositAPI(MethodView):
    def get(self, deposit_id):
        """Get deposit by id"""
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
        return (json.dumps({
            "status": "Error",
            "message": "No such deposit"
        }), 404,)

    def post(self, deposit_id):
        """Change deposit amount"""
        new_amount = request.json.get('amount')
        if new_amount is None:
            return (json.dumps({
                "status": "Error",
                "message": "`amount` expected in post body"
            }), 400,)
        if not isinstance(new_amount, int):
            return (json.dumps({
                "status": "Error",
                "message": "`amount should be integer"
            }), 400,)

        with db.connection.cursor() as cursor:
            updated = cursor.execute('''
                UPDATE deposits
                SET amount=%s
                WHERE id=%s
            ''', (new_amount, deposit_id,))
            if not updated:
                return (json.dumps({
                    "status": "Error",
                    "message": "No deposits to update"
                }), 400,)
        db.connection.commit()
        return json.dumps({"status": "OK"})

    def delete(self, deposit_id):
        """Delete deposit"""
        with db.connection.cursor() as cursor:
            updated = cursor.execute('''
                DELETE FROM deposits
                WHERE id=%s
            ''', (deposit_id,))
            if not updated:
                return (json.dumps({
                    "status": "Error",
                    "message": "No deposits to delete"
                }), 400,)
        db.connection.commit()
        return json.dumps({"status": "OK"})


deposit_api.add_url_rule(
    '/<int:deposit_id>', view_func=DepositAPI.as_view('deposit')
)
