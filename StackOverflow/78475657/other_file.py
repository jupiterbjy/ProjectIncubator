import multiprocessing as mp
import logging
import queue
import time

logging.root.setLevel(logging.NOTSET)


class WorkerProcess(mp.Process):
    def __init__(self, task_queue: mp.JoinableQueue, result_queue: mp.Queue, timeout_sec=2):
        super().__init__()

        self.task_queue = task_queue
        self.result_queue = result_queue
        self.timeout = timeout_sec

    def run(self):
        logging.info(f"[{self.pid:10}] Started")

        while True:
            try:
                task_id, task = self.task_queue.get(timeout=self.timeout)
            except queue.Empty:
                break

            try:
                logging.info(f"[{self.pid:10}] Processing {task_id}")
                time.sleep(1)
                logging.info(f"[{self.pid:10}] Processing {task_id} done")

                self.result_queue.put(task)
            finally:
                # signal JoinableQueue that task we took is done
                self.task_queue.task_done()

        logging.info(f"[{self.pid:10}] Done")
