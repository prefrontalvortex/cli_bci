import argparse
import math

from pythonosc import dispatcher
from pythonosc import osc_server


def eeg_handler(unused_addr, args, ch1, ch2, ch3, ch4, ch5):
    print("EEG (uV) per channel: ", ch1, ch2, ch3, ch4, ch5)


if __name__ == "__main__":
    ## based on http://forum.choosemuse.com/t/using-muse-with-python-on-windows/477
    # which is in turn based on   https://github.com/attwad/python-osc
    IP='192.168.1.103'
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip",
                        default=IP, help="The ip to listen on")
    parser.add_argument("--port",
                        type=int, default=5000, help="The port to listen on")
    args = parser.parse_args()

    # set up the dispatcher to handle the osc
    dispatcher = dispatcher.Dispatcher()
    # Send the address and data of an osc message to a function
    #  of your choice. You can use the same function for multiple addresses.
    #  Check out the examples at https://github.com/attwad/python-osc
    #  for more info on what you can do with the dispatchers
    dispatcher.map("/debug", print)
    dispatcher.map("/muse/eeg", eeg_handler, "EEG")

    # Start the server to recieve osc and serve indefinitely
    server = osc_server.ThreadingOSCUDPServer(
        (args.ip, args.port), dispatcher)
    print("Serving on {}".format(server.server_address))
    server.serve_forever()
