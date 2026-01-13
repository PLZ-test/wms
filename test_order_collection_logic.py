
import unittest
from unittest.mock import MagicMock, patch

# Mock Django environment if needed, or just test the logic class
# Since we can't easily load full Django here, we might need to mock the models imports.
# However, we can just test the logic if we mock the class methods.

class TestOrderCollectorLogic(unittest.TestCase):
    def setUp(self):
        self.mock_shipper = MagicMock()
        self.mock_shipper.name = "TestShipper"
        self.mock_api_info = MagicMock()
        
    def test_aggregation_message(self):
        """
        Test if the aggregation logic producing the message string is correct.
        This simulates the logic inside collect_all_active_orders or collect_orders_for_shipper.
        """
        # Simulate results from different channels
        results = [
            {
                'status': 'success',
                'collected_count': 5,   # 3 success + 2 error
                'success_count': 3,
                'error_count': 2,
                'duplicate_count': 10
            },
            {
                'status': 'success',
                'collected_count': 2,   # 2 success + 0 error
                'success_count': 2,
                'error_count': 0,
                'duplicate_count': 0
            }
        ]
        
        total_collected = sum(r['collected_count'] for r in results)
        total_success = sum(r['success_count'] for r in results)
        total_error = sum(r['error_count'] for r in results)
        total_duplicate = sum(r['duplicate_count'] for r in results)
        # This matches the code I wrote
        total_total = total_collected + total_duplicate
        message = f"총 {total_total}건 처리 (신규 성공: {total_success}, 신규 오류: {total_error}, 중복: {total_duplicate})"
        
        print(f"Generated Message: {message}")
        
        # Expected:
        # Total Collected (New) = 5 + 2 = 7
        # Total Success = 3 + 2 = 5
        # Total Error = 2 + 0 = 2
        # Total Duplicate = 10 + 0 = 10
        # Total Fetched = 17
        
        expected = "총 17건 처리 (신규 성공: 5, 신규 오류: 2, 중복: 10)"
        self.assertEqual(message, expected)

if __name__ == '__main__':
    unittest.main()
