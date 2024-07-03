import threading
import random
import time

import pynput


def thread_print(*arg, **kwargs):
    """Print with thread id"""

    print(f"[T:{threading.get_ident():6}]", *arg, **kwargs)


def func_for_thread(event: threading.Event):
    """Function to be run on thread"""

    thread_print("Thread started")

    while not event.is_set():
        time.sleep(1)
        thread_print(random.randint(1, 10))

    thread_print("Thread finished")


def main():
    thread_event = threading.Event()

    # Create 5 threads, but don't start yet
    threads = [
        threading.Thread(target=func_for_thread, args=(thread_event,)) for _ in range(5)
    ]
    threads_started = False

    # main thread will start listening for key press
    with pynput.keyboard.Events() as events:

        # for each incoming keyboard event:
        for event in events:

            # change match-case to if-elif-else for python < 3.10
            match event.key:

                case pynput.keyboard.Key.esc:
                    print("ESC pressed! Stopping all threads!")
                    thread_event.set()

                    # wait for thread to stop gracefully
                    for thread in threads:
                        thread.join()

                    break

                case pynput.keyboard.Key.space:
                    if threads_started:
                        continue

                    threads_started = True

                    print(f"SPACE pressed! Starting all threads!")

                    # start threads
                    for thread in threads:
                        thread.start()


if __name__ == "__main__":
    main()
