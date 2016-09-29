#!/usr/bin/env python

import socket, getopt, sys, os.path

SMTP_PORT = 25
BUFFER_SIZE = 1024
OK_STATUS = 252

APP_NAME = "smtpenum"
VERSION = "1.0.0"
BANNER = """
  _____ __  __ _______ _____    ______ _   _ _    _ __  __
 / ____|  \/  |__   __|  __ \  |  ____| \ | | |  | |  \/  |
| (___ | \  / |  | |  | |__) | | |__  |  \| | |  | | \  / |
 \___ \| |\/| |  | |  |  ___/  |  __| | . ` | |  | | |\/| |
 ____) | |  | |  | |  | |      | |____| |\  | |__| | |  | |
|_____/|_|  |_|  |_|  |_|      |______|_| \_|\____/|_|  |_|

[mr.church] - v%s
"""

HELP_USAGE = """

usage: smtpenum.py [options]
options:

-v  --version   shows the current version
-t  --target    the target host
-l  --list      the word list file
-h  --help      shows the help usage

"""

OPTIONS = "hvt:l:"
LONG_OPTIONS = ["help", "version", "target=", "list="]
CMD = "VRFY {}"

host = None
wordlist = None

"""
Prints the help usage

"""
def usage():
    print(HELP_USAGE)

"""
Prints the current version

"""
def version():
    print("\n%s %s\n" % (APP_NAME, VERSION))

"""
Parse the given args

"""
def parseargs(argv):

    try :
        opts, args = getopt.getopt(argv, OPTIONS, LONG_OPTIONS)
        if len(opts) == 0:
            print("[!] no arguments given. See smtpenum.py --help for help usage")
            sys.exit(0)

        for opt, arg in  opts:
          if opt in ("-v", "--version"):
              version()
              sys.exit(0)

          elif opt in ("-h", "--help"):
              usage()
              sys.exit(0)

          elif opt in ("-t", "--target"):
            global host
            host = arg

          elif opt in ("-l", "--list"):
            global wordlist
            wordlist = arg

        if (host is None or not host):
            print("[!] no host given. See smtpenum.py --help for help usage")
            sys.exit(0)

        if (wordlist is None or not wordlist):
            print("[!] no wordlist file given. See smtpenum.py --help for help usage")
            sys.exit(0)
        else:
            if (not os.path.exists(wordlist)):
               print("[!] file {} not found".format(wordlist))
               sys.exit(0)

    except getopt.GetoptError as error:
        print("\n")
        print(error)
        usage()
        sys.exit(0)


"""
Gets the ip address of the host

"""
def gethostaddr():
    host_addr = None

    try:
        host_addr = socket.gethostbyname(host)
    except:
        pass

    return host_addr

"""
Tests the smtp port

"""
def issmtpalive(ip):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1)
        s.connect((ip, SMTP_PORT))
        s.close()
    except:
        return False

    return True

"""
The main function

"""
def main(args):

    parseargs(args)
    print(BANNER % (VERSION))
    print("[+] Trying to resolve host by name")

    host_addr = gethostaddr()
    if (host_addr is None or not host_addr):
       print("[!] Host not found")
       print("[!] Unable to resolve %s host address" % (host))
       sys.exit(0)

    print("[+] %s has address: %s" % (host, host_addr))
    if (not issmtpalive(host_addr)):
       print("[!] SMTP port is closed on host %s" % (host_addr))
       sys.exit(0)

    print("[+] SMTP port is openned!")
    print("[+] Grabbing SMTP Banner...")

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host_addr, SMTP_PORT))
    smtp_banner = s.recv(BUFFER_SIZE)
    print("[+] %s" % (smtp_banner))

    print("[+] Trying to enumerate users...")

    f = open(wordlist)
    for user in f.readlines():
       s.send(CMD.format(user))
       status = s.recv(BUFFER_SIZE)
       status_arr = status.split()

       if (OK_STATUS == int(status_arr[0])):
          print("[+] Accepted: %s" % (status_arr[2]))

    s.close()
    f.close()

if __name__ == "__main__":
    main(sys.argv[1:])

