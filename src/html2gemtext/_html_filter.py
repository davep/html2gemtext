"""Provides a HTML filter for converting HTML to Gemtext."""

##############################################################################
# Python imports.
from html.parser import HTMLParser
from re import sub
from typing import Final, Self

##############################################################################
# Local imports.
from .options import Options


##############################################################################
class ContentCapture:
    """A simple class to capture content."""

    def __init__(self, options: Options) -> None:
        """Initialise the object.

        Args:
            options: The options for the converter.
        """
        self._options = options
        """The options for the converter."""
        self._content: list[str] = []
        """List that holds the captured content."""

    def add(self, content: str) -> Self:
        """Add content to the captured content.

        Args:
            content: The content to add.

        Returns:
            Self.
        """
        self._content.append(sub(r"\s\s+", " ", content).strip())
        return self

    def __str__(self) -> str:
        """Return the captured content as a string."""
        return " ".join(self._content)

    def __bool__(self) -> bool:
        """Return whether the captured content is non-empty."""
        return bool(self._content)


##############################################################################
class SoloLink(ContentCapture):
    """A simple class to capture a solo link."""

    def __init__(self, link: str, options: Options) -> None:
        """Initialise the object.

        Args:
            link: The link to add.
            options: The options for the converter.
        """
        super().__init__(options)
        self._link = link
        """The link to add."""

    def __str__(self) -> str:
        """Return the solo link as a string."""
        return f"=> {self._link} {super().__str__()}"


##############################################################################
class Heading(ContentCapture):
    """A simple class to capture a heading."""

    def __init__(self, level: int, options: Options) -> None:
        """Initialise the object.

        Args:
            level: The level of the heading.
            options: The options for the converter.
        """
        super().__init__(options)
        self._level = min(level, 3)
        """The level of the heading."""

    def __str__(self) -> str:
        """Return the heading as a string."""
        return f"{'#' * self._level} {super().__str__()}"


##############################################################################
class ListItem(ContentCapture):
    """A simple class to capture a list item."""

    def __str__(self) -> str:
        """Return the list item as a string."""
        return f"* {super().__str__()}"


##############################################################################
class Quote(ContentCapture):
    """A simple class to capture a quote."""

    def __str__(self) -> str:
        """Return the quote as a string."""
        return f"> {super().__str__()}"


##############################################################################
class Paragraph(ContentCapture):
    """A simple class to capture a paragraph."""

    def __init__(self, options: Options) -> None:
        """Initialise the object.

        Args:
            final_newline: Whether to add a final newline to the paragraph.
        """
        super().__init__(options)
        self._final_newline = options.space_after_paragraphs
        """Whether to add a final newline to the paragraph."""
        self._links: list[str] = []
        """List that holds the links in the paragraph."""
        self._link_id: int | None = None
        """The to associated with the next body of text to add."""

    def add_link(self, link: str) -> Self:
        """Add a link to the paragraph.

        Args:
            link: The link to add.

        Returns:
            Self.
        """
        self._links.append(link)
        self._link_id = len(self._links)
        return self

    def add(self, content: str) -> Self:
        """Add content to the paragraph.

        Args:
            content: The content to add.

        Returns:
            Self.
        """
        super().add(
            f"{content}[{self._link_id}]" if self._link_id is not None else content
        )
        self._link_id = None
        return self

    def cancel_final_newline(self) -> Self:
        """Cancel any request to use a final newline.

        Returns:
            Self.
        """
        self._final_newline = False
        return self

    def __str__(self) -> str:
        """Return the paragraph as a string."""
        return "\n".join(
            [
                # The main content of the paragraph.
                super().__str__(),
                # Add a final newline if requested.
                *([""] if self._final_newline else []),
                # Add any links that were captured in the paragraph.
                *(
                    f"=> {link} {link_id}: {link}"
                    for link_id, link in enumerate(self._links, 1)
                ),
                # Add a final newline if requested and there are links.
                *([""] if self._final_newline and self._links else []),
            ]
        )


##############################################################################
class Preformatted(Paragraph):
    """A simple class to capture preformatted text."""

    def __str__(self) -> str:
        """Return the preformatted text as a string."""
        return "\n".join(
            [
                "```",
                super().__str__().rstrip(),
                "```",
                *([""] if self._final_newline else []),
            ]
        )


##############################################################################
class HTMLToGemtextFilter(HTMLParser):
    """A simple HTML to Gemtext converter."""

    def __init__(self, options: Options | None = None) -> None:
        """Initialise the object."""
        super().__init__()
        self._options = options or Options()
        """The options for the converter."""
        self._current_capture: ContentCapture | None = None
        """The current content capture object."""
        self._document: list[ContentCapture] = []
        """The list of content capture objects for the entire document."""
        self._ignore_next: list[str] = []
        """The stack of tags to ignore the next end tag for."""

    def _maybe_end_last_capture(self) -> Self:
        """End the last capture if there is one.

        Returns:
            Self.
        """
        if self._current_capture is not None:
            self._document.append(self._current_capture)
            self._current_capture = None
        return self

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        """Handle the start of an HTML tag.

        Args:
            tag: The name of the tag.
            attrs: A list of (name, value) pairs containing the attributes found inside the tag
        """
        match tag:
            # A link within a paragraph.
            case "a" if isinstance(self._current_capture, Paragraph):
                if href := dict(attrs).get("href"):
                    self._current_capture.add_link(href)

            # A link outwith a paragraph.
            case "a" if self._current_capture is None:
                if href := dict(attrs).get("href"):
                    self._current_capture = SoloLink(href, self._options)

            # A quote while there is no current capture.
            case "blockquote" if self._current_capture is None:
                self._maybe_end_last_capture()._current_capture = Quote(self._options)

            # A break within a blockquote.
            case "br" if isinstance(self._current_capture, Quote):
                self._document.append(self._current_capture)
                self._current_capture = Quote(self._options)

            # A break within a paragraph.
            case "br" if isinstance(self._current_capture, Paragraph):
                self._document.append(self._current_capture.cancel_final_newline())
                self._current_capture = Paragraph(self._options)

            # A heading while there is no current capture.
            case "h1" | "h2" | "h3" | "h4" | "h5" | "h6":
                self._maybe_end_last_capture()._current_capture = Heading(
                    int(tag.removeprefix("h")), self._options
                )

            # Any kind of list item.
            case "li":
                self._maybe_end_last_capture()._current_capture = ListItem(
                    self._options
                )

            # A paragraph while there is no current capture.
            case "p" if self._current_capture is None:
                self._current_capture = Paragraph(self._options)

            # A paragraph within a paragraph.
            case "p" if isinstance(self._current_capture, Paragraph):
                self._document.append(self._current_capture)
                self._current_capture = Paragraph(self._options)

            # A paragraph within something else.
            case "p" if self._current_capture is not None:
                self._ignore_next.append(tag)

            # A pre tag not inside anything else.
            case "pre" if self._current_capture is None:
                self._maybe_end_last_capture()._current_capture = Preformatted(
                    self._options
                )

            # A pre tag inside something else.
            case "pre" if self._current_capture is not None:
                self._ignore_next.append(tag)

    _END_TAGS_TO_HANDLE: Final[frozenset[str]] = frozenset(
        {
            "blockquote",
            "h1",
            "h2",
            "h3",
            "h4",
            "h5",
            "h6",
            "li",
            "p",
            "pre",
        }
    )
    """The tags to handle the end of."""

    def handle_endtag(self, tag: str) -> None:
        """Handle the end of an HTML tag.

        Args:
            tag: The name of the tag.
        """
        if self._current_capture and tag in self._END_TAGS_TO_HANDLE:
            if self._ignore_next and self._ignore_next[-1] == tag:
                self._ignore_next.pop()
                return
            self._document.append(self._current_capture)
            self._current_capture = None

    def handle_data(self, data: str) -> None:
        """Handle the data inside an HTML tag.

        Args:
            data: The data inside the tag.
        """
        if self._current_capture is not None and (data := data.strip()):
            self._current_capture.add(data)

    def close(self) -> None:
        """Close the parser and flush any remaining content."""
        self._maybe_end_last_capture()
        super().close()

    def __str__(self) -> str:
        """Return the Gemtext representation of the parsed HTML."""
        return "\n".join(str(capture) for capture in self._document)


### _html_filter.py ends here
