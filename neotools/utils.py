from lxml.etree import Element


def inner_text(xml_element: Element) -> str:
    if xml_element is not None:
        return "".join([t for t in xml_element.itertext()])
    else:
        return ""
