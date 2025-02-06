#from threading import Thread, lock
import threading
import time
import sys

def get_input():
    while True:
        user_input = input('Type in some text: ')
        print(user_input)

def other_task():
    current = time.time()
    while True:
        if time.time() - current >= 3:
            print('3 seconds have passed')
            current = time.time()


#threading.Thread(target=other_task).start()
#get_input()

class Test:
    count = 0
    max = 15
    lock = threading.Lock()

    def thread1(self):
        while True:
            with Test.lock:
                Test.count += 1
                print("Thread 1:", Test.count)
            if (Test.count > Test.max):
                break

    def thread2(self):
        while True:
            with Test.lock:
                Test.count += 1
                print("Thread 2:", Test.count)
            if (Test.count > Test.max):
                break

    def start(self):
        threading.Thread(target=self.thread1).start()
        self.thread2()

test = Test()
test.start()
