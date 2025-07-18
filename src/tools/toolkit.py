import random, string

class toolkit():
    def __init__(self, database, config, debug: bool = False):
        self.databaseObj = database
        self.configObj = config
        self.debug = debug

    def _password_gen(self, count: int = 16):
        return ''.join(random.choices(string.ascii_letters + string.digits + r"!$%&*", k=count))
    