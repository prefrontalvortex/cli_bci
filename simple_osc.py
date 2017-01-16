import argparse
import time
import socket


from pythonosc import dispatcher as osc_dispatcher
from pythonosc import osc_server

class EEGHandler(object):
    def __init__(self):
        self.__current_data = {}
        self.__buffer_flag = 0

    def handle(self, unused_addr, args, *channels):
        data = {'time':time.time()}
        for i, ch in enumerate(channels):
            data.update({'ch{}'.format(i): ch}) # probably needless but we will make extensible later
        self.current_data = data
        # print(data)

    def read_data_blocking(self):
        pass

    def pop_data(self):
        flag = self.__buffer_flag
        if flag:
            self.__buffer_flag = 0 ## oh my, race conditions possible. YOLO!
            return self.current_data
        else:
            return None

    @property
    def buffer_flag(self):
        return self.__buffer_flag

    @property
    def current_data(self):
        return self.__current_data

    @current_data.setter
    def current_data(self, val):
        self.__current_data = val
        self.__buffer_flag = 1

    def sim_run_forever(self):
        data = (1.11, 2.22, 3.33, 4.44, 5.55)
        while True:
            t = time.time()
            # put test function here
            self.handle(None, None, *data)
            time.sleep(0.01)


class PollingOSCHandler(object):
    def __init__(self, eegHandler, ip='auto', port=5336, verbose=False):
        ## based on http://forum.choosemuse.com/t/using-muse-with-python-on-windows/477
        # which is in turn based on   https://github.com/attwad/python-osc

        if ip == 'auto':
            ip = get_lan_ip()

        self.eegHandler = eegHandler
        # For simplicity's sake, for starters we will just use pipes to handle program processing

        # set up the dispatcher to handle the osc
        self.dispatcher = osc_dispatcher.Dispatcher()
        # Send the address and data of an osc message to a function
        #  of your choice. You can use the same function for multiple addresses.
        #  Check out the examples at https://github.com/attwad/python-osc
        #  for more info on what you can do with the dispatchers
        self.dispatcher.map("/debug", print)
        self.dispatcher.map("/muse/eeg", eegHandler.handle, "EEG")

        # Start the server to recieve osc and serve indefinitely
        self.server = osc_server.ThreadingOSCUDPServer(
            (ip, port), self.dispatcher)
        print("Serving on {}".format(self.server.server_address))
        # server.serve_forever()

    def handle_request(self, verbose=False):
        self.server.handle_request()
        data = self.eegHandler.pop_data()
        if verbose:
            # print("FOO")
            if data is not None:
                print(data)

        return data



    def handle_forever(self, verbose=False):
        while True:
            self.handle_request(verbose=verbose)

def main2(eegHandler):
    IP = get_lan_ip()
    print("Current IP (make sure to set device streaming IP accordingly): {}".format(IP))
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", default='auto', help="The ip to listen on")
    parser.add_argument("--port", type=int, default=5336, help="The port to listen on")
    parser.add_argument("--sim", action='store_true', default=False, help="Simulate the stream")
    parser.add_argument("--verbose", action='store_true', default=False, help="print the stream")
    args = parser.parse_args()

    if args.sim:
        eegHandler.sim_run_forever()

    pollingHandler = PollingOSCHandler(eegHandler, ip=args.ip, port=args.port)
    pollingHandler.handle_forever(verbose=args.verbose)

def setup_polling(eegHandlder):
    pass

def get_lan_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("gmail.com", 80))
    ip = s.getsockname()[0]
    print(ip)
    s.close()
    return ip

# def eeg_handler(unused_addr, args, ch1, ch2, ch3, ch4, ch5):
#     print("{},{},{},{},{}".format(ch1, ch2, ch3, ch4, ch5))

def eeg_handler(unused_addr, args, *channels):
    for ch in channels:
        print(ch, end=',')
    print('')

def sim_eeg_handler():
    ch1, ch2, ch3, ch4, ch5 = 1.11, 2.22, 3.33, 4.44, 5.55
    print("{},{},{},{},{}".format(ch1, ch2, ch3, ch4, ch5))


def sim_run_forever():
    while True:
        sim_eeg_handler()
        time.sleep(0.01)





def main(eegHandler):
    ## based on http://forum.choosemuse.com/t/using-muse-with-python-on-windows/477
    # which is in turn based on   https://github.com/attwad/python-osc
    IP = get_lan_ip()
    print("Current IP (make sure to set device streaming IP accordingly): {}".format(IP))
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip",
                        default=IP, help="The ip to listen on")
    parser.add_argument("--port",
                        type=int, default=5000, help="The port to listen on")
    parser.add_argument("--sim", action='store_true', default=False, help="Simulate the stream")
    args = parser.parse_args()


    if args.sim:
        eegHandler.sim_run_forever()

    # For simplicity's sake, for starters we will just use pipes to handle program processing

    # set up the dispatcher to handle the osc
    dispatcher = osc_dispatcher.Dispatcher()
    # Send the address and data of an osc message to a function
    #  of your choice. You can use the same function for multiple addresses.
    #  Check out the examples at https://github.com/attwad/python-osc
    #  for more info on what you can do with the dispatchers
    dispatcher.map("/debug", print)
    dispatcher.map("/muse/eeg", eegHandler.handle, "EEG")

    # Start the server to recieve osc and serve indefinitely
    server = osc_server.ThreadingOSCUDPServer(
        (args.ip, args.port), dispatcher)
    print("Serving on {}".format(server.server_address))
    # server.serve_forever()
    while True:
        server.handle_request()


if __name__ == "__main__":
    eegHandler = EEGHandler()
    main2(eegHandler)