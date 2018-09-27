#!/usr/bin/env python

import argparse
import os
import re
import shutil
import sys
import tempfile
import zipfile


def extract_archive(source, dest_path):
    """
    Extract a zip archive to a destination path.
    """
    with zipfile.ZipFile(source) as archive:
        archive.extractall(dest_path)


def main():
    args = parse_args(sys.argv[1:])

    tempdir = tempfile.mkdtemp()
    extract_archive(args.infile, tempdir)

    interaction_rules = os.path.join(tempdir, 'Basic rules', 'interaction_rules.js')
    process_file(interaction_rules, args.import_root)

    shutil.make_archive(args.outfile, 'zip', tempdir)


def parse_args(args):
    """
    Parse the arguments provided to the program.

    Args:
        args:
            The arguments to parse. Typically ``sys.argv``.
    """
    parser = argparse.ArgumentParser(
        description=("Insert dynamic imports into an export archive from "
                     "conversation.one"),
    )

    parser.add_argument(
        'infile',
        help="The exported archive to process.",
        type=argparse.FileType(),
    )
    parser.add_argument(
        'outfile',
        help="The name of the archive to output to.",
        type=str,
    )

    parser.add_argument(
        '--import-root',
        default=os.getcwd(),
        help="The root directory to search for imports from.",
        type=str,
    )

    return parser.parse_args(args)


def process_file(path, import_root):
    """
    Process the imports in a single file.
    """
    pattern = re.compile(
        r'^(// import )([a-zA-Z0-9_\-\.]*)$(.*?)^(// end )([a-zA-Z0-9_\-\.]*)$',
        re.MULTILINE | re.DOTALL,
    )

    with open(path, 'r') as f:
        content = f.read()

    def replace_func(match):
        filename = match.group(2)

        path = os.path.join(import_root, filename)
        with open(path, 'r') as f:
            code = f.read()

        return '// import {filename}\n{content}\n// end {filename}'.format(
            content=code,
            filename=filename,
        )

    new_content = re.sub(pattern, replace_func, content)
    with open(path, 'w') as f:
        f.write(new_content)


if __name__ == '__main__':
    main()
