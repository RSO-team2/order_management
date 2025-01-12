import unittest
from unittest.mock import patch, MagicMock
import json
from app import app

class TestOrderAPI(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    @patch('endpoints.check_database_connection')
    def test_health_check_healthy(self, mock_check_db):
        # Test when database is healthy
        mock_check_db.return_value = None
        response = self.app.get('/health')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.decode(), "Service is healthy")

    @patch('endpoints.check_database_connection')
    def test_health_check_unhealthy(self, mock_check_db):
        # Test when database is unhealthy
        mock_check_db.side_effect = Exception("Database error")
        response = self.app.get('/health')
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.data.decode(), "Service is unhealthy")

    
    @patch('endpoints.make_connection')
    def test_get_user_orders_success(self, mock_conn):
        # Mock database connection
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [
            (1, 1, "01/01/2024", 25.50, "[{}]", 1, 1, "Test Address")
        ]
        mock_conn.return_value = (MagicMock(), mock_cursor)

        response = self.app.get('/get_user_orders?customer_id=1')
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertEqual(response_data["status"], 200)
        self.assertEqual(len(response_data["data"]), 1)

    @patch('endpoints.make_connection')
    def test_get_user_orders_invalid_id(self, mock_conn):
        # Mock database connection
        mock_conn.return_value = (MagicMock(), MagicMock())

        response = self.app.get('/get_user_orders?customer_id=invalid')
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertEqual(response_data["status"], 400)
        self.assertEqual(response_data["message"], "invalid customer id")

    @patch('endpoints.make_connection')
    def test_get_restaurant_orders_success(self, mock_conn):
        # Mock database connection
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [
            (1, 1, "01/01/2024", 25.50, "[{}]", 1, 1, "Test Address")
        ]
        mock_conn.return_value = (MagicMock(), mock_cursor)

        response = self.app.get('/get_restaurant_orders?restaurant_id=1')
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertEqual(response_data["status"], 200)
        self.assertEqual(len(response_data["data"]), 1)

    @patch('endpoints.make_connection')
    @patch('endpoints.send_update_email')
    def test_update_order_status_success(self, mock_send_email, mock_conn):
        # Mock database connection
        mock_cursor = MagicMock()
        mock_conn.return_value = (MagicMock(), mock_cursor)

        test_data = {
            "order_id": 1,
            "status": 2
        }

        response = self.app.post('/update_order_status',
                               json=test_data,
                               content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertEqual(response_data["message"], "order '1' updated to '2'")

    @patch('endpoints.make_connection')
    def test_update_order_status_invalid_data(self, mock_conn):
        # Mock database connection
        mock_conn.return_value = (MagicMock(), MagicMock())

        test_data = {
            "order_id": None,
            "status": None
        }

        response = self.app.post('/update_order_status',
                               json=test_data,
                               content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertEqual(response_data["message"], "invalid order id")
        self.assertEqual(response_data["status"], 400)

if __name__ == '__main__':
    unittest.main()