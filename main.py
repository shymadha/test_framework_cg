import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import argparse
from framework.engine.test_engine import TestEngine

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)

    args = parser.parse_args()

    engine = TestEngine(args.config)
    engine.pre_test()
    engine.do_test()
    engine.post_test()