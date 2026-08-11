##############################################################################
# Python imports.
import fileinput

##############################################################################
# Local imports.
from .convert import html_to_gemtext


##############################################################################
def convert() -> None:
    """Parse the input from stdin or files and print the parsed Gemtext."""
    with fileinput.input() as html:
        print(html_to_gemtext("".join(html)))


##############################################################################
if __name__ == "__main__":
    convert()


### __main__.py ends here
