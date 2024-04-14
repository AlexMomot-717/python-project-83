from pathlib import Path

TESTS_ROOT = Path(__file__).parent


def resolve_path(file_location: str) -> Path:
    return TESTS_ROOT.joinpath(file_location).resolve(strict=True)
