import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import argparse
from framework.engine.test_engine import TestEngine
from framework.core.parser import ParseUserInput

if __name__ == "__main__":
    
    user_input = ParseUserInput()
    print("Loaded Config:")
    print(user_input.config)

    print("\nTest Files:")
    for test in user_input.test_files:
        print(" -", test)
        
    metadata= user_input.get_test_metadata()
    for item in metadata:
        module_path=item["module_path"]
        class_name = item["class_name"]
        print(f"module_path is {module_path} and class_name is {class_name}")

    engine = TestEngine(user_input)
    engine.pre_test()
    engine.do_test()
    engine.post_test()