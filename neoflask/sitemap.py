import xml.etree.ElementTree as ET
import datetime


BASE_URL="https://eeb.sourcedata.io"

def add_url(root, loc, **kwargs):
    doc = ET.SubElement(root, "url")
    ET.SubElement(doc, "loc").text = loc
    for (key, value) in kwargs.items():
        ET.SubElement(doc, key).text = value


def create_sitemap(dois):
    root = ET.Element('urlset')
    # root.attrib['xmlns:xsi']="http://www.w3.org/2001/XMLSchema-instance"
    # root.attrib['xsi:schemaLocation']="http://www.sitemaps.org/schemas/sitemap/0.9 http://www.sitemaps.org/schemas/sitemap/0.9/sitemap.xsd"
    root.attrib['xmlns']="http://www.sitemaps.org/schemas/sitemap/0.9"

    dt = datetime.datetime.now().strftime("%Y-%m-%d")

    add_url(root, loc=BASE_URL, lastmod=dt, changefreq="weekly", priority="1.0")

    for doi in dois:
        add_url(root, loc=f"{BASE_URL}/doi/{doi}", priority="0.9")

    # tree = ET(root)

    xml_declaration = "<?xml version='1.0' encoding='utf-8'?>"
    xml_document = ET.tostring(root, encoding='utf-8').decode("utf-8")
    return f"{xml_declaration}\n{xml_document}"


# from .engine import Engine
# from . import DB, app, cache
# ASKNEO = Engine(DB)
# refereed_preprints = ASKNEO.refereed_preprints()
# import pdb;pdb.set_trace()