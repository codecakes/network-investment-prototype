class StateMachine(object):
    def __init__(self, user):
        self.handlers = {}
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

    def run(self, last_date, next_date):
        state = self.start_state
        # print("starting state ", state)
        try:
            handler = self.handlers[state]
            # print "new handler is ", handler
        except:
            raise Exception("must call .set_start() before .run()")
        if not self.end_states:
            raise Exception("at least one state must be an end_state")

        while True:
            (returns, new_state) = handler(self.user, last_date, next_date)
            self.results[state] = returns
            state = new_state
            if state in self.end_states:
                # print("reached ", new_state)
                break
            else:
                handler = self.handlers[state]
