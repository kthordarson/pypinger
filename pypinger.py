# pypinger.py
from threading import Thread
from multiprocessing import Process, Queue, JoinableQueue
from pinglib import Ping
import sys, time
from colors import Color
from os import system, name

class PingWorker(Thread):
    def __init__ (self, name, host, *args, **kwargs):
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

def clear_scren():
    if name == 'nt':
        _ = system('cls')
    else:
        _ = system('clear')
    
def clean_exit(threads):   
    for t in threads:
        t.join()

def check_threads(threads):
    return True in [t.isAlive() for t in threads]


def main_program():
    if len(sys.argv) < 2:
        hosts = ['192.168.10.1', '8.8.8.8','google.com', '192.168.11.234', '1.1.1.1', 'internetbeacon.msedge.net']
    else:
        hosts = sys.argv[1:]
    threads = list()
    #threads = []
    for host in hosts:
        pinger = PingWorker(name=host, host=host)
        pinger.setDaemon(True)
        threads.append(pinger)
        pinger.start()
    
    while check_threads(threads):
        clear_scren()
        try:
            print(f'\033[95m{"Hostname":<20}{"IP address":<15}{"C":^3} {"min":<10s} {"max":<10s} {"avg":<10s} {"PL":<10s} {"seq":<10s} \x1b[0m')
            for t in threads:
                if t.pinger.response.ret_code == 1:
                    textbg = Color.B_Red
                else:
                    textbg = Color.B_Default                
                print(f''+textbg+f'{t.host[:19]:<20}{t.pinger.dest_ip:<15}{t.pinger.response.ret_code:^3} {t.pinger.response.min_rtt:<10.2f} {t.pinger.response.max_rtt:<10.2f} {t.pinger.response.avg_rtt:<10.2f} {t.pinger.response.packet_lost:<10} {t.pinger.seq_number:<10}\x1b[49m')
            time.sleep(1) # catch keyboardinterrupt and clean exit
        except KeyboardInterrupt:
            clean_exit(threads)

if __name__ == '__main__':
    # host_queue = Queue()
    main_program()