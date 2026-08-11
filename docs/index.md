## Introduction

`html2gemtext` is a small and simple library that provides code for
converting HTML into [the hypertext markup language of the Gemini
project](https://geminiprotocol.net/docs/gemtext-specification.gmi).

## Installation

`html2gemtext` is [available from
pypi](https://pypi.org/project/html2gemtext/) and can be installed with your
package installer of choice.

With `pip`:

```shell
pip install html2gemtext
```

With `uv`:

```shell
uv add html2gemtext
```

## Quick start

The library provides a single main conversion function called
`html_to_gemtext`. It is passed a string that is the HTML you wish to
convert, and the result is a string that is the resulting Gemtext.

A very minimal converter might look like:

```python
import fileinput
from html2gemtext import html_to_gemtext

def convert() -> None:
    with fileinput.input() as html:
        print(html_to_gemtext("".join(html)))
```

While it is primarily intended as a library to be used from other Python
code, it does contain a simple test command line tool, which can be accessed
either via the Python `-m` switch, or depending on your environment, via the
`html2gemtext` command. For example, given this content of a file called
`test.html`:

```html
<!doctype html>
<html lang="en">
  <head>
    <title>Test page</title>
  </head>

  <body>
    <p>
      Hello World! This is a test of the converter.
    </p>
    <p>
      <a href="https://www.example.com">This is a link</a> to an external website.
    </p>
  </body>
</html>
```

The `html2gemtext` command (or `python -m html2gemtext`) would produce:

```gemtext
Hello World! This is a test of the converter.

This is a link[1] to an external website.

=> https://www.example.com 1: https://www.example.com
```

[//]: # (index.md ends here)
