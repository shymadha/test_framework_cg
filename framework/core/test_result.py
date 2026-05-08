class TestResult:
    """
    Represents the outcome of a single test case.

    This class stores the test name, pass/fail status, and an optional
    descriptive message. It acts as a simple container to communicate
    test execution results back to the test engine or reporting layer.

    Attributes
    ----------
    name : str
        Name or identifier of the test.
    passed : bool
        Indicates whether the test succeeded (True) or failed (False).
    message : str
        Detailed message describing the result, error reason, or extra info.
    """

    def __init__(self, name):
        """
        Initialize a new TestResult object.

        Parameters
        ----------
        name : str
            The unique name or identifier for the test.
        """
        self.name = name
        self.passed = False
        self.message = ""

    def set_result(self, passed, message=""):
        """
        Set the final verdict and optional message for the test.

        Parameters
        ----------
        passed : bool
            True if the test passed, False if it failed.
        message : str, optional
            Additional descriptive information about the result.
            Defaults to an empty string.
        """
        self.passed = passed
        self.message = message