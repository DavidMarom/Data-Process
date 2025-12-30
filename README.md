# Anti-Semitism Analysis

## Run Instructions
Note: run main.py

# Tests
pyproject.toml file is a pytest configuration file that defines how pytest should behave when running tests in your project.

testpaths = ["tests"] - Look for tests in the tests directory
python_files = ["test_*.py"] - Consider files that start with test_ as test files
python_classes = ["Test*"] - Consider classes that start with Test as test classes
python_functions = ["test_*"] - Consider functions that start with test_ as test functions

The file makes pytest automatically find your tests in the tests directory following the naming conventions.

Run Instructions:
run on terminal:
pytest -v