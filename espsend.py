#!/usr/bin/python

import serial
import time

class ESPserial:
    def __init__(self, port='/dev/ttyUSB0', baud=115200):
        self._port = serial.Serial(port)
        # setting baud rate in a separate step is a workaround for
        # CH341 driver on some Linux versions (this opens at 9600 then
        # sets), shouldn't matter for other platforms/drivers. See
        # https://github.com/themadinventor/esptool/issues/44#issuecomment-107094446
        self._port.baudrate = baud

    def write(self, packet):
        self._port.write(packet)

    def sendfile(self, file):
        with open(file, 'r') as f:
            lines = f.readlines()

        self.write('\x03') # Send ^C
        esp.write('import webrepl; webrepl.start()\r\n')
        self.write('\x05') # Send ^E
        time.sleep(0.02)
        self.write('with open("%s", "w") as f:\r' % file)
        for l in lines:
           if l[0] == '#':
               print ('Skip comment')
               continue
           l1 = l.strip()
           l2 = l1.split('#', 1)[0]
           self.write(" a='''%s'''\r" % l2)
           self.write(" f.write(a)\r")
           time.sleep(0.02)

        self.write('\x04') # Send ^D

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', action="store", default='/dev/ttyUSB0')
    parser.add_argument('--baud', action="store", default=115200)
    parser.add_argument('--file', action="store", default='')
    parser.add_argument('-c', '--controlc', action="store_true", default=False)
    parser.add_argument('-w', '--webrepl', action="store_true", default=False)
    parser.add_argument('-r', '--reset', action="store_true", default=False)
    parser.add_argument('-l', '--list', action="store_true", default=False)
    parser.add_argument('-m', '--mem', action="store_true", default=False)
    parser.add_argument('-k', '--check', action="store_true", default=False)


    args = parser.parse_args()

    esp = ESPserial(port=args.port, baud=int(args.baud))

    if args.file != '':
        print("Sending File %s" % args.file)
        esp.sendfile(args.file)

    if args.controlc == True:
        print("Sending Control-c")
        esp.write('\x03')

    if args.webrepl == True:
        print("Enabling Webrpl")
        esp.write('import webrepl; webrepl.start()\r\n')

    if args.list == True:
        print("Listing files on machine ")
        esp.write('import os; os.listdir()\r\n')
        esp.write('import os; os.remove("wifi.config")\r\n')

    if args.check == True:
        print("Check FW on machine ")
        esp.write('import esp; esp.check_fw()\r\n')

    if args.mem == True:
        print("Listing mem on machine ")
        esp.write('import esp; esp.meminfo()\r\n')
        esp.write('import micropython; micropython.mem_info()\r\n')
        esp.write('import gc; gc.mem_alloc()\r\n')
        esp.write('import gc; gc.mem_free()\r\n')

    if args.reset == True:
        print("Restarting machine ")
        esp.write('\x03')
        esp.write('import machine; machine.reset()\r\n')

    time.sleep(1)
