def redline():
    var = input("Do you want to initialize a new project? (y/n)")
    return var


class Console:
    def __init__(self, program):
        self.program = program.run()

    def run(self):
        if redline() == 'y':
            self.program.run()
