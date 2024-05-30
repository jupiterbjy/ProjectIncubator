"""
Restartable Thread demo

answer for: https://stackoverflow.com/q/78552374/10909029
"""

import threading
import random
import time

import pynput


class RestartableThread:
    def __init__(self, target, *args, **kwargs):
        """Create a tiny thread manager that can be restarted.

        Args:
            target (Callable): A function/method to run on thread.
                Must accept `threading.Event` as first argument.

            args (tuple, optional): Argument for target. Defaults to ().
            kwargs (dict, optional): Argument for target. Defaults to {}.
        """

        self.target = target
        self.thread = None
        self.event = threading.Event()
        self.args = (self.event, *args)
        self.kwargs = kwargs

    @property
    def is_running(self):
        return self.thread is not None and self.thread.is_alive()

    @property
    def is_stopping(self):
        return self.event.is_set()

    def run(self):
        # make sure thread is stopped before starting new one
        self.join()

        # create new thread & start
        self.thread = threading.Thread(
            target=self.target, args=self.args, kwargs=self.kwargs
        )
        self.thread.start()

    def join(self):
        """Wait for thread to stop gracefully"""

        if self.thread is None:
            return

        self.thread.join()
        self.event.clear()
        # ^ also clear event so we can restart thread

    def stop(self):
        """Signal thread to stop"""
        self.event.set()


def thread_print(*arg, **kwargs):
    """Print with thread id"""

    print(f"[T:{threading.get_ident():6}]", *arg, **kwargs)


def func_a_for_thread(event: threading.Event, *args, **kwargs):
    """Function to be ran on thread"""

    thread_print("Thread started")

    while not event.is_set():
        time.sleep(random.randint(1, 3))
        thread_print("Func A running with args:", args, kwargs)

    thread_print("Thread finished")


class SomeClass:
    def func_b_for_thread(self, event: threading.Event, *args, **kwargs):
        """Function to be ran on thread"""

        thread_print("Thread started")

        while not event.is_set():
            time.sleep(random.randint(1, 3))
            thread_print("Func B running with args:", args, kwargs)

        thread_print("Thread finished")


def main():
    # create threads
    thread_a = RestartableThread(func_a_for_thread, args=("arg1", "arg2"))

    some_instance = SomeClass()
    thread_b = RestartableThread(some_instance.func_b_for_thread, args=("arg3", "arg4"))

    # main thread will start listening for key press
    with pynput.keyboard.Events() as events:

        # for each incoming keyboard event:
        for event in events:

            if event.key == pynput.keyboard.Key.esc:
                print("ESC pressed! Stopping all threads!")
                thread_a.stop()
                thread_b.stop()

                # wait for thread to stop gracefully
                thread_a.join()
                thread_b.join()

                break

            # some keys don't have char attribute
            if not hasattr(event.key, "char"):
                continue

            match event.key.char:
                case "a":
                    if not thread_a.is_running:
                        print("Starting thread A")
                        thread_a.run()

                case "b":
                    if not thread_b.is_running:
                        print("Starting thread B")
                        thread_b.run()

                case "c":
                    if thread_a.is_running and not thread_a.is_stopping:
                        print("Stopping thread A!")
                        thread_a.stop()

                case "d":
                    if thread_b.is_running and not thread_b.is_stopping:
                        print("Stopping thread B!")
                        thread_b.stop()


if __name__ == "__main__":
    main()
