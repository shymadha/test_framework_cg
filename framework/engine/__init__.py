import json


class TestEngine:
    def __init__(self, testbed_file):
        self.testbed_file = testbed_file
        self.user_input = {}
        self.platform = None
        self.interface = None
        self.verdict = None

    # 1️⃣ INIT
    def init(self):
        with open(self.testbed_file, 'r') as f:
            self.user_input = json.load(f)

        print("Testbed loaded successfully")
        return self.user_input

    # 2️⃣ EXECUTION WRAPPER
    def execute(self):
        try:
            self.pre_test()
            self.do_test()
            self.post_test(success=True)
        except Exception as e:
            print(f"Test failed with error: {e}")
            self.post_test(success=False)

    # 2.1️⃣ PRE TEST
    def pre_test(self):
        print("Checking preconditions...")
        self.validate_input()

        print("Creating platform object...")
        self.platform = Platform(self.user_input)

        print("Creating test interface...")
        self.interface = self.platform.create_interface()

    # 2.2️⃣ DO TEST
    def do_test(self):
        print("Executing test...")
        self.interface.run_test()
        self.verdict = "PASS"

    # 2.3️⃣ POST TEST
    def post_test(self, success):
        print("Cleaning up...")
        if self.interface:
            self.interface.close()

        self.verdict = "PASS" if success else "FAIL"
        print(f"Final Verdict: {self.verdict}")

    def validate_input(self):
        required_keys = ["platform", "interface"]
        for key in required_keys:
            if key not in self.user_input:
                raise ValueError(f"Missing required field: {key}")