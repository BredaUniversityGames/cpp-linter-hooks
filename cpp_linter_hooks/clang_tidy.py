import subprocess
from argparse import ArgumentParser
from typing import Tuple
import re

from cpp_linter_hooks.util import resolve_install, DEFAULT_CLANG_TIDY_VERSION


parser = ArgumentParser()
parser.add_argument("--version", default=DEFAULT_CLANG_TIDY_VERSION)

# [Optional] Used for adding a prefix to the clang executable
# You can call this multiple times if relevant.
#
# This is useful when using platform-specific versions or 
# cross-compilation toolchains where the tools are named 
# with a prefix, such as 'x86_64-linux-gnu-clang-tidy' or
# 'aarch64-linux-gnu-clang-format'.
#
# Leave empty to just use 'clang-tidy'.
parser.add_argument("--clang-tool-prefix", action='append', type=str, default=[])

# [Optional] Specifies regex for '--clang-tool-prefix'
# You can call this multiple times if relevant.
#
# This is useful for when you have a project with multiple
# platforms that need a specific clang-tidy executable
# to perform linting.
#
# Since the regex is applied to the clang-tidy arguments, 
# be careful with the regex string.
#
# Any prefix that does not have a regex linked will use '.*'
parser.add_argument("--prefix-regex", action='append', type=str, default=[])


def run_clang_tidy(args=None) -> Tuple[int, str]:
    hook_args, other_args = parser.parse_known_args(args)
    if hook_args.version:
        resolve_install("clang-tidy", hook_args.version)

    clang_args = ' '.join(other_args)

    prefix = ''

    num_prefixes = len(hook_args.clang_tool_prefix)
    num_regexes = len(hook_args.prefix_regex)
    if num_prefixes > 0 \
        or num_regexes > 0:
        # If there are two or more prefixes than there are regexes, I throw an error
        # since I have no clue which one is meant
        if num_prefixes - num_regexes >= 2:
            return 2, "Too many prefixes provided. Please provide no more than two more prefixes than regexes."
        if num_regexes > num_prefixes:
            return 3, "More regexes than prefixes provided. Please use the 'files' argument in the hook for filtering instead of this argument."

        # This loops over all the specified prefixes and tests the regex on the file name
        for i, ct_prefix in enumerate(hook_args.clang_tool_prefix):
            regex_string = ''

            try:
                regex_string = hook_args.prefix_regex[i]
            except IndexError:
                regex_string = '.*'

            if re.search(regex_string, clang_args) is not None:
                prefix = ct_prefix

    command = [prefix + "clang-tidy"] + other_args

    retval = 0
    output = ""
    try:
        sp = subprocess.run(command, stdout=subprocess.PIPE, encoding="utf-8")
        retval = sp.returncode
        output = sp.stdout
        if "warning:" in output or "error:" in output:
            retval = 1
        return retval, output
    except FileNotFoundError as stderr:
        retval = 1
        return retval, str(stderr)


def main() -> int:
    retval, output = run_clang_tidy()
    if retval != 0:
        print(output)
    return retval


if __name__ == "__main__":
    raise SystemExit(main())
