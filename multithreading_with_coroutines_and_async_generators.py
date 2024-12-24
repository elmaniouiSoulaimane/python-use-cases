import asyncio
import threading
from typing import Coroutine, AsyncGenerator
from queue import Queue

class Test:
    def __init__(self):
        self.result_queue = Queue()  # Shared queue to collect results

    def run_coro_in_thread(self, async_gen: AsyncGenerator, item: dict) -> threading.Thread:
        def run_coro_in_event_loop() -> None: 
            # Create a dedicated event loop
            new_event_loop = asyncio.new_event_loop()

            # Run the new event loop
            asyncio.set_event_loop(new_event_loop)

            try:
                # Coroutine
                async def handle_gen(item: dict) -> None:
                    async for result in async_gen(item):
                        self.result_queue.put(result)

                # Run the coroutine that will handle the async generator in the new event loop
                new_event_loop.run_until_complete(handle_gen(item))

            finally:
                # Close the event loop
                new_event_loop.close()

        # Start the thread with the event loop
        thread = threading.Thread(target=run_coro_in_event_loop, daemon=True)
        thread.start()
        return thread

    async def run(self):
        data: list = [
            {'a': 1, 'b': 2},
            {'a': 3, 'b': 4},
            {'a': 5, 'b': 6},
            {'a': 7, 'b': 8},
        ]

        async def my_async_generator(item: dict) -> AsyncGenerator:
            # Example of yielding results
            for key, value in item.items():
                await asyncio.sleep(1)  # Simulate async work
                yield {key: value * 2}  # Yield transformed data

        threads = []
        for item in data:
            thread = self.run_coro_in_thread(async_gen=my_async_generator, item=item)
            threads.append(thread)
            
        # Wait for all threads to finish
        for thread in threads:
            thread.join()
        
        # Collect results from the queue
        results = []
        while not self.result_queue.empty():
            results.append(self.result_queue.get())

        print("All results:", results)

if __name__ == '__main__':
    obj = Test()
    asyncio.run(obj.run())