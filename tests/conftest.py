import os
import pytest

def pytest_addoption(parser):
    parser.addoption(
        "--classify-n",
        action="store",
        type=int,
        default=int(os.getenv("CLASSIFY_SMOKE_N", "1")),
        help="Number of term+context items to classify in the API smoke test.",
    )

@pytest.fixture
def classify_n(request) -> int:
    return int(request.config.getoption("--classify-n"))