class TestResult:
    def __init__(self, name):
        self.name = name
        self.passed = False
        self.message = ""

    def set_result(self, passed, message=""):
        self.passed = passed
        self.message = message