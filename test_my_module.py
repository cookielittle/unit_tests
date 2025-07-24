import unittest
import asyncio
import logging
from unittest import IsolatedAsyncioTestCase
from unittest.mock import patch, AsyncMock, MagicMock

# Assuming MyClass is in a module named 'my_module'
from my_module import MyClass 

class TestMyClass(IsolatedAsyncioTestCase):

    def setUp(self):
        # Initialize MyClass for each test
        self.my_instance = MyClass(flag=True, time_sec=5) # Set time_sec for consistency
        self.stop_event = asyncio.Event()

    @patch('my_module.MyClass.get_item_list', return_value=[10, 20, 30])
    @patch('my_module.MyClass.dummy_func', side_effect=lambda item: f"Mocked return for {item}")
    @patch('my_module.logger') # Patch the logger
    @patch('asyncio.sleep', new_callable=AsyncMock)
    async def test_my_func_with_items_list(
        self, 
        mock_sleep: AsyncMock, 
        mock_logger: MagicMock, 
        mock_dummy_func: MagicMock, 
        mock_get_item_list: MagicMock
    ):
        # Allow the loop to run a few times for testing, then cancel it
        mock_sleep.side_effect = [asyncio.CancelledError]

        task = asyncio.create_task(self.my_instance.my_func(self.stop_event))

        try:
            await asyncio.wait_for(task, timeout=1) 
        except asyncio.TimeoutError:
            pass # Expected if CancellationError doesn't stop it
        except asyncio.CancelledError:
            pass # Expected when mock_sleep raises it

        # Assert get_item_list was called
        mock_get_item_list.assert_called_once() 

        # Assert logger.info calls
        mock_logger.info.assert_any_call(" item list 10,20,30")
        mock_logger.info.assert_any_call("calling dummy_func(10) return message: Mocked return for 10")
        mock_logger.info.assert_any_call("calling dummy_func(20) return message: Mocked return for 20")
        mock_logger.info.assert_any_call("calling dummy_func(30) return message: Mocked return for 30")
        
        # Assert dummy_func calls
        mock_dummy_func.assert_any_call(10)
        mock_dummy_func.assert_any_call(20)
        mock_dummy_func.assert_any_call(30)

        # Verify asyncio.sleep was called with the correct time_sec
        mock_sleep.assert_awaited_with(self.my_instance.time_sec)
        
        # Stop the event for graceful shutdown if the loop is still active (unlikely due to sleep mock)
        self.stop_event.set() 

    @patch('my_module.MyClass.get_item_list', return_value=[])
    @patch('my_module.MyClass.dummy_func')
    @patch('my_module.logger')
    @patch('asyncio.sleep', new_callable=AsyncMock)
    async def test_my_func_with_empty_item_list(
        self, 
        mock_sleep: AsyncMock, 
        mock_logger: MagicMock, 
        mock_dummy_func: MagicMock, 
        mock_get_item_list: MagicMock
    ):
        mock_sleep.side_effect = [asyncio.CancelledError] # Allow one full loop iteration

        task = asyncio.create_task(self.my_instance.my_func(self.stop_event))
        try:
            await asyncio.wait_for(task, timeout=1)
        except asyncio.CancelledError:
            pass

        mock_get_item_list.assert_called_once()
        mock_dummy_func.assert_not_called() # dummy_func should NOT be called

        # Verify the "no items in list" message
        mock_logger.info.assert_any_call(" no items in list. ")
        
        mock_sleep.assert_awaited_with(self.my_instance.time_sec)
        self.stop_event.set()


    @patch('my_module.MyClass.get_item_list') 
    @patch('my_module.MyClass.dummy_func')
    @patch('my_module.logger')
    @patch('asyncio.sleep', new_callable=AsyncMock)
    async def test_my_func_status_false(
        self, 
        mock_sleep: AsyncMock, 
        mock_logger: MagicMock, 
        mock_dummy_func: MagicMock, 
        mock_get_item_list: MagicMock
    ):
        self.my_instance.status = False # Set status to false
        self.my_instance.flag = True

        mock_sleep.side_effect = [asyncio.CancelledError] # Allow a loop iteration

        task = asyncio.create_task(self.my_instance.my_func(self.stop_event))
        try:
            await asyncio.wait_for(task, timeout=1)
        except asyncio.CancelledError:
            pass

        mock_get_item_list.assert_not_called() # get_item_list should NOT be called
        mock_dummy_func.assert_not_called()
        mock_logger.info.assert_not_called() # Nothing should be logged in this branch
        
        mock_sleep.assert_awaited_with(self.my_instance.time_sec)
        self.stop_event.set()

    # Test the get_item_list method directly
    
    def test_get_item_list_returns_expected_list(self):
        expected_list = [1, 2, 3, 4]
        actual_list = self.my_instance.get_item_list()
        self.assertEqual(actual_list, expected_list)

    # Test the dummy_func method directly
    def test_dummy_func_returns_correct_message(self):
        item_id = 5
        expected_message = "Calling Dummy Function (5)"
        actual_message = self.my_instance.dummy_func(item_id)
        self.assertEqual(actual_message, expected_message)
    

if __name__ == '__main__':
    unittest.main()
