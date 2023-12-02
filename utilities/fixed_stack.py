class FixedStack(list):
    def __init__(self, max_size):
        self.max_size = max_size
        self.stack = []

    def push(self, item):
        self.stack.append(item)
        if len(self.stack) > self.max_size:
            self.stack.pop(0)  # Remove the oldest element at the bottom

    def get_stack(self):
        return self.stack