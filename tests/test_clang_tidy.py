import pytest
import subprocess
from pathlib import Path

from cpp_linter_hooks.clang_tidy import run_clang_tidy


@pytest.fixture(scope="function")
def generate_compilation_database():
    subprocess.run(["mkdir", "-p", "build"])
    subprocess.run(["cmake", "-Bbuild", "testing/"])
    subprocess.run(["cmake", "-Bbuild", "testing/"])


@pytest.mark.benchmark
@pytest.mark.parametrize(
    ("args", "expected_retval"),
    (
        (['--checks="boost-*"'], 1),
        (['--checks="boost-*"', "--version=16"], 1),
        (['--checks="boost-*"', "--version=17"], 1),
        (['--checks="boost-*"', "--version=18"], 1),
        (['--checks="boost-*"', "--version=19"], 1),
        (['--checks="boost-*"', "--version=20"], 1),
        (['--checks="boost-*"', "--version=21"], 1),
    ),
)
def test_run_clang_tidy_valid(args, expected_retval):
    # copy test file to tmp_path to prevent modifying repo data
    test_file = Path("testing/main.c")
    test_file.write_bytes(Path("testing/main.c").read_bytes())
    ret, output = run_clang_tidy(args + [str(test_file)])
    assert ret == expected_retval
    print(output)


@pytest.mark.benchmark
@pytest.mark.parametrize(
    ("args", "expected_retval"),
    (
        (['--checks="boost-*"'], 1),
        (['--checks="boost-*"', "--version=16"], 1),
        (['--checks="boost-*"', "--version=17"], 1),
        (['--checks="boost-*"', "--version=18"], 1),
        (['--checks="boost-*"', "--version=19"], 1),
        (['--checks="boost-*"', "--version=20"], 1),
        (['--checks="boost-*"', "--version=21"], 1),
    ),
)
def test_run_clang_tidy_invalid(args, expected_retval, tmp_path):
    # non existent file
    test_file = tmp_path / "main.c"

    ret, _ = run_clang_tidy(args + [str(test_file)])
    assert ret == expected_retval


# This test covers proper handling of prefixes.
# Note that the prefixes I use here are not valid.
# The whole point of the test is to see if the prefixes
# are caught.
@pytest.mark.benchmark
@pytest.mark.parametrize(
    ("args", "expected_retval"),
    (
        # Should give the usual warnings
        (['--checks="boost-*"'], 1),
        # Should use testclang-tidy -> FileNotFoundError
        (['--checks="-*"', "--clang-tool-prefix", "test", "--prefix-regex", r".*"], 1),
        # Should use testclang-tidy -> FileNotFoundError
        (
            [
                '--checks="-*"',
                "--clang-tool-prefix",
                "test",
                "--prefix-regex",
                r".*main\.(c|cpp|h|hpp)",
            ],
            1,
        ),
        # Should use testclang-tidy -> FileNotFoundError
        (
            [
                '--checks="-*"',
                "--clang-tool-prefix",
                "test",
                "--prefix-regex",
                r".*\.c",
            ],
            1,
        ),
        # Should use clang-tidy -> usual warnings
        (
            [
                '--checks="-*"',
                "--clang-tool-prefix",
                "test",
                "--prefix-regex",
                r"shouldnotmatch",
            ],
            1,
        ),
        # Should use testclang-tidy -> FileNotFoundError
        (
            [
                '--checks="-*"',
                "--clang-tool-prefix",
                "test",
                "--prefix-regex",
                r".*\.c",
                "--clang-tool-prefix",
                "test2",
                "--prefix-regex",
                "main",
            ],
            1,
        ),
    ),
)
def test_run_clang_tidy_prefixes_valid(args, expected_retval):
    # copy test file to tmp_path to prevent modifying repo data
    test_file = Path("testing/main.c")
    test_file.write_bytes(Path("testing/main.c").read_bytes())
    ret, output = run_clang_tidy(args + [str(test_file)])
    assert ret == expected_retval
    print(output)


# This test covers cases where the user has either specified
# too many prefixes or regexes.
@pytest.mark.benchmark
@pytest.mark.parametrize(
    ("args", "expected_retval"),
    (
        # More regexes than prefixes is invalid.
        # For this type of filtering, I strongly
        # suggest the user to use the files arg.
        (['--checks="boost-*"', "--prefix-regex", r".*"], 3),
        # Two or more prefixes than there are
        # regexes is confusing
        (
            [
                '--checks="boost-*"',
                "--clang-tool-prefix",
                "test",
                "--clang-tool-prefix",
                "test2",
            ],
            2,
        ),
    ),
)
def test_run_clang_tidy_prefixes_invalid(args, expected_retval):
    # copy test file to tmp_path to prevent modifying repo data
    test_file = Path("testing/main.c")
    test_file.write_bytes(Path("testing/main.c").read_bytes())
    ret, output = run_clang_tidy(args + [str(test_file)])
    assert ret == expected_retval
    print(output)
