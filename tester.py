#!/usr/bin/env python3

from transitions import Machine
import subprocess
import sys
import time
import argparse

# Test line number
current_line = 0

# Parse command line arguments
parser = argparse.ArgumentParser(description = "MaxScale + replication-manager tester", conflict_handler="resolve")
parser.add_argument("-b", "--bin", dest="bin", help="MaxAdmin binady", default="/usr/bin/maxadmin")
parser.add_argument("-h", "--host", dest="host", help="MaxAdmin network address", default="localhost")
parser.add_argument("-u", "--user", dest="user", help="MaxAdmin user", default="admin")
parser.add_argument("-p", "--password", dest="password", help="MaxAdmin password", default="mariadb")
parser.add_argument("-P", "--port", dest="port", help="MaxAdmin listener port", default="6603")
parser.add_argument("-i", "--interactive", dest="interactive", help="Run test in interactive mode", default=True)
parser.add_argument("-s", "--bootstrap", dest="bootstrap", help="Script used to bootstrap the test environment")
parser.add_argument("-c", "--client", dest="client", help="Client script used to add load to the test environment")
parser.add_argument("-v", "--verbose", dest="verbose", help="Verbose output", default=False)
parser.add_argument("TEST", help="Test to run", nargs="+")
options = parser.parse_args(sys.argv[1:])

class Test():
    def on_enter_MX(self):
        self.start(0)
        self.kill(1)
        time.sleep(10)

    def on_enter_XM(self):
        self.kill(0)
        self.start(1)
        time.sleep(10)

    def on_enter_MS(self):
        self.start(1)
        self.start(0)
        time.sleep(10)

    def on_enter_SM(self):
        self.start(1)
        self.start(0)
        time.sleep(10)

    def on_enter_XX(self):
        self.kill(1)
        self.kill(0)
        time.sleep(10)

    def start(self, node):
        subprocess.run(["start.sh", str(node)])

    def kill(self, node):
        subprocess.run(["stop.sh", str(node)])


def get_output():
    output = subprocess.run([options.bin, "-u", options.user,
                             "-p" + options.password, "-h", options.host,
                             "-P", options.port, "list", "servers"],
                            stdout=subprocess.PIPE).stdout.decode().split('\n')
    return output[4:len(output) - 2]


def check_status(name, status):
    global current_line
    output = get_output()
    i = [z.strip() for a in output for z in a.split('|') if name == a.split('|')[0].strip()]

    for x in status:
        states = [st.strip() for st in i[4].split(',')]
        if x not in states:
            print("In test '" + test_name + "' at line " + str(current_line) + ":")
            print("Expected", status, "got", i[4])
            print(get_output())
            return False
    return True


def check_no_status(name, status):
    global current_line
    output = get_output()
    i = [z.strip() for a in output for z in a.split('|') if name == a.split('|')[0].strip()]

    for x in status:
        states = [st.strip() for st in i[4].split(',')]
        if x in states:
            print("In test '" + test_name + "' at line " + str(current_line) + ":")
            print("Unexpected", status)
            print(get_output())
            return False
    return True


def get_statelist():
    states = [ "M", "S", "X" ]
    invalid_states = ["MM", "SS", "SX", "XS"]
    return [x + y for x in states for y in states if x + y not in invalid_states]


def do_bootstrap(script):
    subprocess.run([script], shell=True)


def run_test(tname):
    global current_line
    current_line = 0

    with open(tname) as f:
        print("Running test:", tname)

        for x in f:
            current_line += 1
            x = x.strip()

            if options.interactive == True:
                input("Press Enter to transition from " + test.state + " to " + x)

            if x == "MS":
                test.ms()
                check_status("server1", ["Master", "Running"])
                check_status("server2", ["Slave", "Running"])
            elif x == "MX":
                test.mx()
                check_status("server1", ["Master", "Running"])
                check_no_status("server2", ["Running"])
            elif x == "SM":
                test.sm()
                check_status("server1", ["Slave", "Running"])
                check_status("server2", ["Master", "Running"])
            elif x == "XM":
                test.xm()
                check_no_status("server1", ["Running"])
                check_status("server2", ["Master", "Running"])
            elif x == "XX":
                test.xx()
                check_no_status("server1", ["Running"])
                check_no_status("server2", ["Running"])
            else:
                print("ERROR:", x)

            if options.verbose:
                print("Expecting:", x)

                for l in get_output():
                    print([a.strip() for a in l.split('|')])


# Create list of all allowed permutations of the three node states
statelist = get_statelist()
initial_state = "MS"

transitions = [
    {"trigger": "mx", "source": ["MS", "SM", "XX"], "dest": "MX"},
    {"trigger": "xm", "source": ["MS", "SM", "XX"], "dest": "XM"},
    {"trigger": "xx", "source": ["MX", "XM"], "dest": "XX"},
    {"trigger": "ms", "source": ["MX", "XM", "MS"], "dest": "MS"},
    {"trigger": "sm", "source": ["MX", "XM"], "dest": "SM"},
]

client = None

try:
    for test_name in options.TEST:
        test = Test()
        test.start(0)
        test.start(1)

        if options.bootstrap != None:
            do_bootstrap(options.bootstrap)

        if options.client != None:
            client = subprocess.Popen([options.client], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        machine = Machine(model=test, states=statelist, initial=initial_state, transitions=transitions)
        run_test(test_name)

        if client != None:
            client.kill()
            client.communicate()


except Exception as e:
    print(e)
    if client != None:
        client.kill()
        client.communicate()
