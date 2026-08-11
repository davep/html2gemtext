"""Tests for the HTML to Gemtext converter."""

##############################################################################
# Pytest imports.
from pytest import mark

##############################################################################
# Local imports.
from html2gemtext import Options, html_to_gemtext


##############################################################################
@mark.parametrize(
    "html, gemtext",
    [
        ("", ""),
        ("         ", ""),
        ("<p>Hello, world!</p>", "Hello, world!\n"),
        ("<p>Hello, world!<p>Again!</p>", "Hello, world!\n\nAgain!\n"),
        ("<h1>Heading 1</h1>", "# Heading 1"),
        ("<h2>Heading 2</h2>", "## Heading 2"),
        ("<h3>Heading 3</h3>", "### Heading 3"),
        ("<h4>Heading 4</h4>", "### Heading 4"),
        ("<a href='https://example.com'>Example</a>", "=> https://example.com Example"),
        (
            "<p>Has <a href='example.com'>a link</a> inside.</p>",
            "Has a link[1] inside.\n\n=> example.com 1: example.com\n",
        ),
        ("<ul><li>Item 1</li><li>Item 2</li></ul>", "* Item 1\n* Item 2"),
        ("<ol><li>Item 1</li><li>Item 2</li></ol>", "* Item 1\n* Item 2"),
        ("<pre>Preformatted text</pre>", "```\nPreformatted text\n```\n"),
        ("<blockquote>Quote</blockquote>", "> Quote"),
        ("<p>Line 1.<br>Line 2.</p>", "Line 1.\nLine 2.\n"),
        ("<blockquote>Line 1.<br>Line 2.</blockquote>", "> Line 1.\n> Line 2."),
        ("<blockquote>Quote.<p>More quote.</p></blockquote>", "> Quote. More quote."),
        ("<p>Paragraph</p><h1>Heading</h1>", "Paragraph\n\n# Heading"),
        ("<p>Paragraph<h1>Heading</h1>", "Paragraph\n\n# Heading"),
        ("<p><pre>Paragraph</pre></p>", "Paragraph\n"),
    ],
)
def test_basic_conversion(html: str, gemtext: str) -> None:
    """Test the basic HTML to Gemtext conversion.

    Args:
        html: The HTML to convert.
        gemtext: The expected Gemtext output.
    """
    assert html_to_gemtext(html) == gemtext


##############################################################################
@mark.parametrize(
    "html, space, gemtext",
    [
        ("<p>Hello, world!</p>", True, "Hello, world!\n"),
        ("<p>Hello, world!</p>", False, "Hello, world!"),
        ("<p>Hello, world!<p>Again!</p>", True, "Hello, world!\n\nAgain!\n"),
        ("<p>Hello, world!<p>Again!</p>", False, "Hello, world!\nAgain!"),
    ],
)
def test_paragraph_space_option(html: str, space: bool, gemtext: str) -> None:
    """Test the paragraph space option."""
    assert html_to_gemtext(html, Options(space_after_paragraphs=space)) == gemtext


### test_html_to_gemtext.py ends here
