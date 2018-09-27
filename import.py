#!/usr/bin/env python

import argparse
import logging
import os
import re
import shutil
import sys
import tempfile
import zipfile


VERBOSITY_LEVELS = [
    logging.INFO,
    logging.DEBUG,
]


logging.basicConfig()
logger = logging.getLogger(__name__)


def extract_archive(source, dest_path):
    """
    Extract a zip archive to a destination path.
    """
    with zipfile.ZipFile(source) as archive:
        archive.extractall(dest_path)
        logger.debug("Extracted archive to '%s'", dest_path)


def main():
    """
    Entry point into the script.

    The general process is we extract the archive, process the files
    we're interested in, then repack the archive.
    """
    args = parse_args(sys.argv[1:])

    logger.setLevel(
        VERBOSITY_LEVELS[max(0, min(len(VERBOSITY_LEVELS) - 1, args.verbose))],
    )

    # Extract the archive
    tempdir = tempfile.mkdtemp()
    logger.debug("Create temporary directory: %s", tempdir)
    extract_archive(args.infile, tempdir)

    # Process the files to insert our dynamic imports.
    interaction_rules = os.path.join(tempdir, 'Basic rules', 'interaction_rules.js')
    process_file(interaction_rules, args.import_root)

    # Pack the new archive and remove the extracted copy
    shutil.make_archive(args.outfile, 'zip', tempdir)
    shutil.rmtree(tempdir)


def parse_args(args):
    """
    Parse the arguments provided to the program.

    Args:
        args:
            The arguments to parse. Typically some portion of
            ``sys.argv``.
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

    parser.add_argument(
        '-v',
        '--verbose',
        action='count',
        help=("A flag to increase the verbosity of the script's output. "
              "Including the flag multiple times will increase the "
              "verbosity."),
    )

    return parser.parse_args(args)


def process_file(path, import_root):
    """
    Process the imports in a single file.

    Args:
        path:
            The path of the file to process.
        import_root:
            The root directory to search for imports from. The file path
            referenced in each ``// import <file>`` directive will be
            appended to the import root when opening the file to import.
    """
    pattern = re.compile(
        r'^// import ([a-zA-Z0-9_\-\.]*)$.*?^// end ([a-zA-Z0-9_\-\.]*)$',
        re.MULTILINE | re.DOTALL,
    )

    with open(path, 'r') as f:
        content = f.read()
    logger.debug("Read contents of %s", path)

    def replace_func(match):
        logger.debug("Processing chunk:\n%s", match.group(0))
        filename = match.group(1)

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

    logger.info("Successfully processed imports in %s", path)


if __name__ == '__main__':
    main()
