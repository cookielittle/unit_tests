import asyncio
import logging

from config_reader import A

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

a_instance = A('config.json')

def check_status():
    return "activated"

class MyClass:
    def __init__(self, flag: bool, time_sec: int) -> None:
        self.status = check_status()
        self.flag = flag
        self.time_sec = time_sec

    async def my_func(self, stop_event: asyncio.Event):
        while not stop_event.is_set():
            # item_list should only be populated if the condition is met
            item_list = [] # Initialize each iteration, if not populated below, it remains empty

            if (self.status == "activated") and (self.flag == True):
                item_list = self.get_item_list() # Call instance method
                
                # Move the processing and logging of item_list INTO this conditional block
                if len(item_list) > 0:
                    logger.info(
                        " item list "
                        + ",".join(f"{item}" for item in item_list)
                    )
                    for item in item_list:
                        ret_msg = self.dummy_func(item)
                        logger.info(
                            f"calling dummy_func({item}) return message: {ret_msg}"
                        )
                else:
                    logger.info(
                        " no items in list. "
                    )
            # ELSE branch (if status and flag are not True) now implicitly does nothing for this iteration
            # before going to sleep.

            await asyncio.sleep(self.time_sec)

    
    def dummy_func(self, item_id: int) -> str:
        ret_msg = f"Calling Dummy Function ({item_id})"
        return ret_msg

    def get_item_list(self) -> list[int]:
        # Example implementation, assuming this would be mocked in tests
        return [1, 2, 3, 4] # Returning a concrete list for the example
    
