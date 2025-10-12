"""
Utility functions for cleaning and formatting AI responses.
"""

import re
from bs4 import BeautifulSoup


def clean_xml_response(xml_content: str) -> str:
    """
    Clean XML response by removing markdown code blocks and HTML tags.

    This function removes common HTML tags that AI models might incorrectly include,
    while preserving the XML structure and text content.

    Args:
        xml_content: Raw XML content from AI

    Returns:
        Cleaned XML string with HTML tags removed
    """
    cleaned = xml_content.strip()

    # Remove markdown code blocks
    if cleaned.startswith("```xml"):
        cleaned = cleaned[6:]  # Remove ```xml
    if cleaned.startswith("```"):
        cleaned = cleaned[3:]  # Remove ```
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]  # Remove trailing ```

    # Define HTML tags to remove (keeping text content)
    # These are common HTML tags that should not appear in our XML structure.
    # Some models might put content inside these HTML tags.
    html_tags_to_remove = [
        "p",
        "div",
        "span",
        "br",
        "strong",
        "em",
        "b",
        "i",
        "u",
        "s",
        "ul",
        "ol",
        "li",
        "dl",
        "dt",
        "dd",
        "h1",
        "h2",
        "h3",
        "h4",
        "h5",
        "h6",
        "table",
        "tr",
        "td",
        "th",
        "thead",
        "tbody",
        "tfoot",
        "a",
        "button",
        "form",
        "input",
        "label",
        "header",
        "footer",
        "nav",
        "main",
        "aside",
        "blockquote",
        "pre",
        "code",
        "hr",
        "img",
        "figure",
        "figcaption",
    ]

    # Parse with BeautifulSoup using 'html.parser' to avoid XML parsing issues
    soup = BeautifulSoup(cleaned, "html.parser")

    # Remove HTML tags while keeping their text content
    for tag_name in html_tags_to_remove:
        for tag in soup.find_all(tag_name):
            tag.unwrap()  # Removes the tag but keeps its contents

    # Convert back to string
    cleaned = str(soup)

    # BeautifulSoup might add extra whitespace, clean it up
    cleaned = re.sub(r"\n\s*\n", "\n\n", cleaned)  # Remove excessive blank lines

    return cleaned.strip()
