
class Member:
    def __init__(self):
        self.name = "tester"
        self.id = "tester"

class Guild:
    def __init__(self):
        self.id = "tester"

    @property
    def members(self):
        m = Member()
        return [m]
    
class Client:
    @property
    def guilds(self):
        g = Guild()
        return [g]
