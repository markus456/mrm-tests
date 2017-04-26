#!/usr/bin/env python3

from transitions import Machine
import subprocess
import sys
import time

class Test():
    def on_enter_MX(self):
        self.start(0)
        self.kill(1)

    def on_enter_XM(self):
        self.kill(0)
        self.start(1)

    def on_enter_MS(self):
        self.start(1)
        self.start(0)

    def on_enter_SM(self):
        self.start(1)
        self.start(0)

    def on_enter_XX(self):
        self.kill(1)
        self.kill(0)

    def start(self, node):
        subprocess.run(["start.sh", str(node)])

    def kill(self, node):
        subprocess.run(["stop.sh", str(node)])


def check_status():
    return subprocess.run(["check.sh"], stdout=subprocess.PIPE).stdout.decode()

# Possible node states
states = [ "M", "S", "X" ]

# These aren't cases we want to happen
invalid_states = ["MM", "SS", "SX", "XS"]

# Create list of all allowed permutations of the three node states
statelist = [x + y for x in states for y in states if x + y not in invalid_states]
initial_state = "MS"

transitions = [
    {"trigger": "mx", "source": ["MS", "SM", "XX"], "dest": "MX"},
    {"trigger": "xm", "source": ["MS", "SM", "XX"], "dest": "XM"},
    {"trigger": "xx", "source": ["MX", "XM"], "dest": "XX"},
    {"trigger": "ms", "source": ["MX", "XM", "MS"], "dest": "MS"},
    {"trigger": "sm", "source": ["MX", "XM"], "dest": "SM"},
]

for t in sys.argv[1:]:
    test = Test()
    machine = Machine(model=test, states=statelist, initial=initial_state, transitions=transitions)

    f = open(t)

    for x in f:
        x = x.strip()

        before = check_status()
        input("Press Enter to transition from " + test.state + " to " + x)

        if x == "MS":
            test.ms()
        elif x == "MX":
            test.mx()
        elif x == "SM":
            test.sm()
        elif x == "XM":
            test.xm()
        elif x == "XX":
            test.xx()
        else:
            print("ERROR:", x)

        for i in range(0, 10):
            after = check_status()
            if before != after:
                print(after)
                break
            else:
                time.sleep(1)

    f.close()
