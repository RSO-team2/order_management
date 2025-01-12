import endpoints as ep
from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin
import requests
from prometheus_flask_exporter import PrometheusMetrics

app = Flask(__name__)
cors = CORS(app)

# Attach Prometheus metrics to the Flask app
metrics = PrometheusMetrics(app)

# Automatically collect standard metrics like request count, response duration, and more
metrics.info('app_info', 'Restaurant Management API Info', version='1.0.0')

@app.route("/health")
def health_check():
    try:
        ep.check_database_connection()
        return "Service is healthy", 200
    except:
        return "Service is unhealthy", 500


@app.post("/new_order")
@cross_origin()
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

    data["order_date"] = ep.get_current_date()
    data["status"] = 1
    if data["delivery_address"]["parse"]:
        user_address_data = requests.get(
            f"https://faas-nyc1-2ef2e6cc.doserverless.co/api/v1/web/fn-3c231b12-5667-4f1f-b506-1603f4fce4a5/sample/hello?ip={data['delivery_address']['value']}"
        ).json()
        data["delivery_address"] = (
            f"lat: {user_address_data['latitude']}, long: {user_address_data['longitude']}"
        )
    else:
        data["delivery_address"] = data["delivery_address"]["value"]
    order_id = ep.insert_order(cursor, data)
    ep.commit_and_close(conn, cursor)
    return jsonify({"message": f"success, order '{order_id}' saved", "status": 200})


@app.get("/get_user_orders")
@cross_origin()
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


@app.get("/get_restaurant_orders")
@cross_origin()
def get_restaurant_orders():
    conn, cursor = ep.make_connection()
    restaurant_id = request.args.get("restaurant_id")

    if not restaurant_id or not restaurant_id.isdigit():
        return jsonify({"message": "invalid restaurant id", "status": 400})

    orders = ep.get_restaurant_orders(cursor, int(restaurant_id))
    ep.commit_and_close(conn, cursor)

    return jsonify(
        {
            "message": f"orders for restaurant '{restaurant_id}'",
            "status": 200,
            "data": orders,
        }
    )


@app.post("/update_order_status")
@cross_origin()
def update_order_status():
    conn, cursor = ep.make_connection()
    data = request.get_json()
    order_id = data["order_id"]
    status = data["status"]

    if not order_id or not order_id.isdigit():
        return jsonify({"message": "invalid order id", "status": 400})
    
    ep.update_order_status(cursor, int(order_id), int(status))
    ep.commit_and_close(conn, cursor)

    return jsonify({"message": f"order '{order_id}' updated to '{status}'"})


if __name__ == "__main__":
    print("Starting app...")
    app.run(host="0.0.0.0", port=5001)
