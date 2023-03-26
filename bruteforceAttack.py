import crypt
import time

class BruteForceAttack:
    def __init__(self, pwList, limit, group):
        self.charset = 'abcdefghijklmnopqrstuvwxyz'
        self.limit = limit
        self.pwList = pwList
        self.group = group
        self.section = []
        self.counter = 0

    def initiateAttack(self):
        for i in range(1, len(self.charset) + 1):
            results = self.bruteForceRecursive("", i)
            if results:
                break

    def bruteForceRecursive(self, current, length):
        self.counter += 1
        # Gets Correct String Length
        if len(current) == length:
            self.section.append(current)
            if self.counter > self.limit:
                self.pwList.append(self.section)
                return True
            elif self.counter % self.group == 0:
                self.pwList.append(self.section)
                self.section = []
        # Recusive Function Call For Next Guess
        else:
            for char in self.charset:
                result = self.bruteForceRecursive(current + char, length)
                if result:
                    return True

if __name__ == '__main__':
    BA = BruteForceAttack(20)
    BA.initiateAttack()
