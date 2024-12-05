import endpoints as ep
from flask import Flask, jsonify, request

app = Flask(__name__)


@app.route("/new_order", methods=["POST"])
def new_order():
    conn, cursor = ep.make_connection()
    data = request.get_json()

    valid_data = ep.vaildate_order_data(data)
    if not valid_data["result"]:
        return jsonify(
            {"message": f"invalid data - {valid_data['error']}", "status": 400}
        )
    
    data["order_date"] = ep.get_current_date()
    data["status"] = 1
    order_id = ep.insert_order(cursor, data)
    ep.commit_and_close(conn, cursor)

    return jsonify({"message": f"success, order '{order_id}' saved", "status": 200})


@app.route("/get_user_orders", methods=["GET"])
def get_user_orders():
    conn, cursor = ep.make_connection()
    customer_id = request.args.get("customer_id")

    if not customer_id or not customer_id.isdigit():
        return jsonify({"message": "invalid customer id", "status": 400})

    orders = ep.get_user_orders(cursor, int(customer_id))
    ep.commit_and_close(conn, cursor)

    return jsonify(
        {
            "message": f"orders for customer '{customer_id}'",
            "status": 200,
            "data": orders,
        }
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
