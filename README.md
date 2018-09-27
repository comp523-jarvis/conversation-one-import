# Conversation.one Import

This is a script to dynamically insert code into an archive from conversation.one and repack the archive. The repacked archive can then be imported back into the conversation.one project.

## Features

### Custom Intent Code

Custom code for handling an intent can be included using the following syntax:

```js
// import yourCustomCodeFile.js
// end yourCustomCodeFile.js
```

The script will insert the contents of `yourCustomCodeFile.js` between the tags. Because of the ending and closing tags, this feature is idempotent.

## Usage

```
usage: import.py [-h] [--import-root IMPORT_ROOT] infile outfile

Insert dynamic imports into an export archive from conversation.one

positional arguments:
  infile                The exported archive to process.
  outfile               The name of the archive to output to.

optional arguments:
  -h, --help            show this help message and exit
  --import-root IMPORT_ROOT
                        The root directory to search for imports from.
```
