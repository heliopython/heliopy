def pytest_addoption(parser):
    parser.addoption("--no-data", action="store_true",
                     help="Skip tests that involve downloading data")
