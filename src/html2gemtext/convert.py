"""Provides a simple HTML to Gemtext converter."""

##############################################################################
# Local imports.
from ._html_filter import HTMLToGemtextFilter
from .options import Options


##############################################################################
def html_to_gemtext(html_content: str, options: Options | None = None) -> str:
    """Convert HTML content to Gemtext.

    Args:
        html_content: The HTML content to convert.
        options: Optional conversion options.

    Returns:
        The converted Gemtext content.
    """

    (html_filter := HTMLToGemtextFilter(options)).feed(html_content)
    html_filter.close()
    return str(html_filter)


### convert.py ends here
