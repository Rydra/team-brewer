class Match:
    def __init__(self, person1, person2, date=None):
        self.date = date
        self.person1 = person1
        self.person2 = person2

    def is_present(self, person):
        return self.person1 == person or self.person2 == person