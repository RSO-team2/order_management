import endpoints as ep
from flask import Flask, jsonify, request

app = Flask(__name__)


@app.route("/new_order", methods=["POST"])
def new_order():
    """
    Create a new order in the order management system.
    This function establishes a connection to the database, retrieves order data from the request,
    validates the data, and if valid, inserts the order into the database with the current date and
    a status of 1. The connection is then committed and closed.
    Returns:
        Response: A JSON response indicating the success or failure of the operation.
        - On success: {"message": "success, order '<order_id>' saved", "status": 200}
        - On failure: {"message": "invalid data - <error_message>", "status": 400}
    """
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
    """
    Retrieve orders for a specific customer.
    This function establishes a database connection, retrieves the customer ID from the request arguments,
    validates the customer ID, fetches the orders for the customer from the database, and returns the orders
    in a JSON response.
    Returns:
        Response: A JSON response containing the message, status, and data (orders) if the customer ID is valid.
                  If the customer ID is invalid, returns a JSON response with an error message and status 400.
    """
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
    print("Starting app...")
    app.run(host='0.0.0.0', port=5000)