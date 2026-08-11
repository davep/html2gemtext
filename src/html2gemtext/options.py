"""Configuration options for the converter."""

##############################################################################
# Python imports.
from typing import NamedTuple


##############################################################################
class Options(NamedTuple):
    """Configuration options for the converter."""

    space_after_paragraphs: bool = True
    """Whether to add an empty line after paragraphs."""


### options.py ends here
