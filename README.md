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

### Workflow

First export your conversation.one project using the "Export All Rules" option.

![Export All Rules](/docs/images/Export.png)

Then run the script, passing in the archive you just created.

```
./import.py path/to/exported/archive.zip output.zip
```

Now you can import the archive back in to your project by uploading the `output.zip` file created by the script.

![Import All Rules](/docs/images/Import.png)

### CLI Parameters

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
