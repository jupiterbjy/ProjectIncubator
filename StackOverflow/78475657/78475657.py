import multiprocessing as mp
import asyncio
import logging

from other_file import WorkerProcess

logging.root.setLevel(logging.NOTSET)


class Manager:
    def __init__(self):
        self.task_queue = mp.JoinableQueue()
        self.result_queue = mp.Queue()

    async def _monitor(self):
        """Periodically reports queue sizes.
        Automatically cancelled after all processes are killed."""
        while True:
            await asyncio.sleep(1.0)

            logging.info(f"[   Manager]   Task queue size: {self.task_queue.qsize()}")
            logging.info(f"[   Manager] Result queue size: {self.result_queue.qsize()}")

    async def _process(self):
        """Do whatever you want here for results"""

        while (val := await asyncio.to_thread(self.result_queue.get)) is not None:
            logging.info(f"[   Manager] Got result {val}")

    async def start(self):
        """Wait for all tasks to be done"""

        # Populate the task queue
        for task_idx, task in enumerate(range(10)):
            self.task_queue.put((task_idx, task))

        # create loop, monitoring task & result process task
        monitor_task = asyncio.create_task(self._monitor())
        result_proc_task = asyncio.create_task(self._process())

        # Start the child processes
        processes = [
            WorkerProcess(self.task_queue, self.result_queue)
            for _ in range(3)
        ]
        for process in processes:
            process.start()

        logging.info("[   Manager] Started")

        # wait for all tasks to be done. If so, cancel monitor task
        await asyncio.to_thread(self.task_queue.join)
        monitor_task.cancel()

        # since .task_done() emit is AFTER putting to result queue,
        # there's no race condition here. Send sentinel to result queue
        # to signal end of processing. for self._process()
        self.result_queue.put(None)

        # wait for process & self._process task
        await result_proc_task
        for process in processes:
            process.join()

        logging.info("[   Manager] Done")


if __name__ == '__main__':
    manager = Manager()

    # if running normally:
    asyncio.run(manager.start())

    # in notebook (already in async context)
    # await manager.start()
