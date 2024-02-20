from lxml import etree as ET
import datetime


BASE_URL = "https://eeb.embo.org"


def add_url(root, loc, **kwargs):
    doc = ET.SubElement(root, "url")
    ET.SubElement(doc, "loc").text = loc
    for (key, value) in kwargs.items():
        ET.SubElement(doc, key).text = value


def create_sitemap(n_pages):
    root = ET.Element('urlset')
    # root.attrib['xmlns:xsi']="http://www.w3.org/2001/XMLSchema-instance"
    # root.attrib['xsi:schemaLocation']="http://www.sitemaps.org/schemas/sitemap/0.9 http://www.sitemaps.org/schemas/sitemap/0.9/sitemap.xsd"
    root.attrib['xmlns'] = "http://www.sitemaps.org/schemas/sitemap/0.9"

    dt = datetime.datetime.now().strftime("%Y-%m-%d")

    add_url(root, loc=BASE_URL)
    add_url(root, loc=f"{BASE_URL}/about")
    add_url(root, loc=f"{BASE_URL}/contact")
    add_url(root, loc=f"{BASE_URL}/refereed-preprints")
    for page in range(2, n_pages + 1):
        add_url(root, loc=f"{BASE_URL}/refereed-preprints?page={page}")

    xml_document = ET.tostring(root, xml_declaration=True, encoding='utf-8').decode("utf-8")
    return xml_document
