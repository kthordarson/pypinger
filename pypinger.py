# pypinger.py
from threading import Thread
from multiprocessing import Process, Queue, JoinableQueue
from pinglib import Ping
import sys
import time
from colors import Color
from os import system, name


class PingWorker(Thread):
    def __init__(self, name, host, *args, **kwargs):
        Thread.__init__(self)
        self.host = host
        self.name = name
        self.kill = False
        self.pinger = Ping(host, timeout=100, packet_size=55, *args, **kwargs)
        self.pingres = None

    def run(self):
        while True:
            if self.kill:
                return
            self.pingres = self.pinger.run(1)

    def join(self):
        self.kill = True
        super().join()


class MainThread(Thread):
    def __init__(self, name, pingers, hosts, *args, **kwargs):
        Thread.__init__(self)
        self.name = name
        self.pingers = list()
        self.hosts = hosts
        self.kill = False

    def run(self):
        self.start_pingers()
        while True:
            if self.kill:
                for t in self.pingers:
                    t.join()
                return
            clear_scren()
            print(f'\033[95m{"Hostname":<20}{"IP address":<15}{"C":^3} {"min":<10s} {"max":<10s} {"avg":<10s} {"S":<10s} {"R":<10s} {"PL":<10s} {"seq":<10s} \x1b[0m')
            for t in self.pingers:
                if t.pinger.response.ret_code == 1:
                    textbg = Color.B_Red
                elif t.pinger.response.ret_code == 2:
                    textbg = Color.B_LightRed
                else:
                    textbg = Color.B_Default
                print(f''+textbg+f'{t.host[:19]:<20}{t.pinger.dest_ip:<15}{t.pinger.response.ret_code:^3} {t.pinger.response.min_rtt:<10.2f} {t.pinger.response.max_rtt:<10.2f} {t.pinger.response.avg_rtt:<10.2f} {t.pinger.send_count:<10} {t.pinger.receive_count:<10} {t.pinger.response.packet_lost:<10} {t.pinger.seq_number:<10}\x1b[49m')
            time.sleep(1)  # catch keyboardinterrupt and clean exit
    def join(self):
        self.kill = True
        for t in self.pingers:
            t.join()
        super().join()
    def reset_pingers(self):
        for t in self.pingers:
            t.join()
        self.pingers = list()
        self.start_pingers()
    def start_pingers(self):
        for host in self.hosts:
            pinger = PingWorker(name=host, host=host)
            pinger.setDaemon(True)
            self.pingers.append(pinger)
            pinger.start()



def clear_scren():
    if name == 'nt':
        _ = system('cls')
    else:
        _ = system('clear')


def clean_exit(threads):
    for t in threads:
        t.join()

def stopmain(maint):
    maint.join()
    exit(0)

def check_threads(threads):
    return True in [t.isAlive() for t in threads]

def check_main_thread(thread):
    return thread.isAlive()

def start_threads(threads, hosts):
    for host in hosts:
        pinger = PingWorker(name=host, host=host)
        pinger.setDaemon(True)
        threads.append(pinger)
        pinger.start()


def reset_threads(threads):
    print(f'RESET')
    for t in threads:
        t.join()


def main_program():
    if len(sys.argv) < 2:
        # 'server02.viralgenvc.local', 'host01.viralgenvc.local'] '172.16.0.51',
        hosts = ['8.8.8.8', 'google.com',
            '1.1.1.1', 'internetbeacon.msedge.net']
    else:
        hosts = sys.argv[1:]
    threads = list()
    # threads = []
    # start_threads(threads, hosts)
    maint = MainThread('MainThread', threads, hosts)
    maint.setDaemon(True)
    maint.start()

    while check_main_thread(maint):
        try:
            cmd = input('> ')
            if cmd[:1] == 'r':
                maint.reset_pingers()
                #reset_threads(maint.pingers)
                # threads = list()
                #start_threads(threads, hosts)
            if cmd[:1] == 'q':
                stopmain(maint)
        except KeyboardInterrupt:
            stopmain(maint)

if __name__ == '__main__':
    # host_queue = Queue()
    main_program()
