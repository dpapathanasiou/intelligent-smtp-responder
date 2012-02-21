#!/usr/bin/python

"""

StateMachine class
Based on David Mertz's article "Charming Python: Using state machines" (http://www.ibm.com/developerworks/library/l-python-state/index.html)

Updated to include two variables useful in exception reporting: the current state and the current cargo

"""

class StateMachine:
    def __init__(self):
        self.handlers = {}
        self.startState = None
        self.endStates = []
        self.current_state = None
        self.current_cargo = None

    def add_state(self, name, handler, end_state=0):
        self.handlers[name] = handler
        if end_state:
            self.endStates.append(name)

    def set_start(self, name):
        self.startState = name

    def run(self, cargo):
        try:
            handler = self.handlers[self.startState]
        except:
            raise Exception("StateMachine Initialization Error: you must call .set_start() before .run()")
        if not self.endStates:
            raise Exception("StateMachine Initialization Error: at least one state must be an end_state")

        while 1:
            (newState, cargo) = handler(cargo)
            self.current_state = newState
            self.current_cargo = cargo
            if newState in self.endStates:
                break
            else:
                handler = self.handlers[newState]

