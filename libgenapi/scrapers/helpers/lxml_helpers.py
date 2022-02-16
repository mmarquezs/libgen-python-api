from lxml.etree import _Element


def get_all_text_in_element(element: _Element, strip=True) -> str | None:
    text = element.xpath("string()")
    if text:
        return text.strip() if strip else text
    return None
