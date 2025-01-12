import unittest
from unittest.mock import patch, MagicMock
import json
from app import app

class TestRestaurantAPI(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_health_check_success(self):
        with patch('endpoints.check_database_connection'):
            response = self.app.get('/health')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.data.decode(), "Service is healthy")

    def test_health_check_failure(self):
        with patch('endpoints.check_database_connection', side_effect=Exception("DB Error")):
            response = self.app.get('/health')
            self.assertEqual(response.status_code, 500)
            self.assertEqual(response.data.decode(), "Service is unhealthy")

    @patch('endpoints.make_connection')
    @patch('endpoints.insert_order')
    @patch('endpoints.get_current_date')
    def test_new_order_success(self, mock_date, mock_insert, mock_connect):
        # Mock database connection
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = (mock_conn, mock_cursor)
        
        # Mock date and order insertion
        mock_date.return_value = "01/01/2024 12:00:00"
        mock_insert.return_value = 123

        test_data = {
            "customer_id": 1,
            "total_amount": 50.0,
            "items": "[]",
            "restaurant_id": 1,
            "delivery_address": {
                "parse": False,
                "value": "123 Test St"
            }
        }

        response = self.app.post('/new_order',
                               data=json.dumps(test_data),
                               content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertEqual(response_data["message"], "success, order '123' saved")
        self.assertEqual(response_data["status"], 200)

    @patch('endpoints.make_connection')
    @patch('endpoints.insert_order')
    @patch('requests.get')
    def test_new_order_with_address_parsing(self, mock_get, mock_insert, mock_connect):
        # Mock database connection
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = (mock_conn, mock_cursor)
        
        # Mock address parsing response
        mock_get.return_value.json.return_value = {
            "latitude": 40.7128,
            "longitude": -74.0060
        }
        
        # Mock order insertion
        mock_insert.return_value = 124

        test_data = {
            "customer_id": 1,
            "total_amount": 50.0,
            "items": "[]",
            "restaurant_id": 1,
            "delivery_address": {
                "parse": True,
                "value": "192.168.1.1"
            }
        }

        response = self.app.post('/new_order',
                               data=json.dumps(test_data),
                               content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertEqual(response_data["status"], 200)

    @patch('endpoints.make_connection')
    @patch('endpoints.get_user_orders')
    def test_get_user_orders_success(self, mock_get_orders, mock_connect):
        # Mock database connection
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = (mock_conn, mock_cursor)
        
        # Mock orders data
        mock_orders = [(1, "01/01/2024", 50.0, "[]", 1, 1, "123 Test St")]
        mock_get_orders.return_value = mock_orders

        response = self.app.get('/get_user_orders?customer_id=1')
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertEqual(response_data["status"], 200)
        self.assertEqual(response_data["message"], "orders for customer '1'")
        self.assertEqual(response_data["data"], mock_orders)

    def test_get_user_orders_invalid_id(self):
        response = self.app.get('/get_user_orders?customer_id=invalid')
        
        self.assertEqual(response.status_code, 200)  # API returns 200 even for invalid IDs
        response_data = json.loads(response.data)
        self.assertEqual(response_data["status"], 400)
        self.assertEqual(response_data["message"], "invalid customer id")

    @patch('endpoints.make_connection')
    @patch('endpoints.get_restaurant_orders')
    def test_get_restaurant_orders_success(self, mock_get_orders, mock_connect):
        # Mock database connection
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = (mock_conn, mock_cursor)
        
        # Mock orders data
        mock_orders = [(1, "01/01/2024", 50.0, "[]", 1, 1, "123 Test St")]
        mock_get_orders.return_value = mock_orders

        response = self.app.get('/get_restaurant_orders?restaurant_id=1')
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertEqual(response_data["status"], 200)
        self.assertEqual(response_data["message"], "orders for restaurant '1'")
        self.assertEqual(response_data["data"], mock_orders)

    def test_get_restaurant_orders_invalid_id(self):
        response = self.app.get('/get_restaurant_orders?restaurant_id=invalid')
        
        self.assertEqual(response.status_code, 200)  # API returns 200 even for invalid IDs
        response_data = json.loads(response.data)
        self.assertEqual(response_data["status"], 400)
        self.assertEqual(response_data["message"], "invalid restaurant id")

if __name__ == '__main__':
    unittest.main()