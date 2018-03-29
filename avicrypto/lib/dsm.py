import pdb

class StateMachine(object):
    def __init__(self, user):
        self.handlers = {}
        self.handler = None
        self.user = user
        self.start_state = None
        self.end_states = []
        self.results = {}

    def add_state(self, investment_type, investment_dict, end_state=0):
        self.handlers[investment_type] = investment_dict[investment_type]
        self.add_end_state(end_state)
        
    def add_end_state(self, end_state):
        if end_state:
            self.end_states.append(end_state)

    def set_start(self, investment_type):
        self.start_state = investment_type
    
    def handle(self, *args, **kw):
        if not self.handler:
            raise Exception("No Function handler called")
        return self.handler(self.user, *args, **kw)
        
    
    def run(self, *args, **kw):
        state = self.start_state
        # print("starting state ", state)
        try:
            self.handler = self.handlers[state]
            # print "new handler is ", handler
        except:
            raise Exception("must call .set_start() before .run()")
        if not self.end_states:
            raise Exception("at least one state must be an end_state")

        while True:
            # (returns, new_state) = handler(self.user, last_date, next_date)
            (returns, new_state) = self.handle(*args, **kw)
            print "Running state"
            pdb.pprint.pprint(self.handler.__name__, depth=2)
            self.results[state] = returns
            state = new_state
            if state in self.end_states:
                # print("reached ", new_state)
                break
            else:
                try:
                    self.handler = self.handlers[state]
                except KeyError as e:
                    print "got {}. Switching to {}'s wet state".format(e.message, state)
                    handler_state = "{}_wet".format(state)
                    print "switched to %s" %handler_state
                    self.handler = self.handlers[handler_state]
