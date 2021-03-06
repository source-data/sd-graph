from lxml import etree as ET
import datetime


BASE_URL = "https://eeb.embo.org"


def add_url(root, loc, **kwargs):
    doc = ET.SubElement(root, "url")
    ET.SubElement(doc, "loc").text = loc
    for (key, value) in kwargs.items():
        ET.SubElement(doc, key).text = value


def create_sitemap(dois):
    root = ET.Element('urlset')
    # root.attrib['xmlns:xsi']="http://www.w3.org/2001/XMLSchema-instance"
    # root.attrib['xsi:schemaLocation']="http://www.sitemaps.org/schemas/sitemap/0.9 http://www.sitemaps.org/schemas/sitemap/0.9/sitemap.xsd"
    root.attrib['xmlns'] = "http://www.sitemaps.org/schemas/sitemap/0.9"

    dt = datetime.datetime.now().strftime("%Y-%m-%d")

    add_url(root, loc=BASE_URL, lastmod=dt, changefreq="weekly", priority="1.0")
    add_url(root, loc=f"{BASE_URL}/about", lastmod=dt, changefreq="monthly", priority="1.0")
    add_url(root, loc=f"{BASE_URL}/contact", lastmod=dt, changefreq="monthly", priority="1.0")
    add_url(root, loc=f"{BASE_URL}/for-developers", lastmod=dt, changefreq="monthly", priority="1.0")
    add_url(root, loc=f"{BASE_URL}/refereed-preprints/review-commons", lastmod=dt, changefreq="monthly", priority="1.0")
    add_url(root, loc=f"{BASE_URL}/refereed-preprints/peerage-of-science", lastmod=dt, changefreq="monthly", priority="1.0")
    add_url(root, loc=f"{BASE_URL}/refereed-preprints/embo-press", lastmod=dt, changefreq="monthly", priority="1.0")
    add_url(root, loc=f"{BASE_URL}/refereed-preprints/elife", lastmod=dt, changefreq="monthly", priority="1.0")
    add_url(root, loc=f"{BASE_URL}/refereed-preprints/rrc19", lastmod=dt, changefreq="monthly", priority="1.0")
    add_url(root, loc=f"{BASE_URL}/refereed-preprints/peer-community-in", lastmod=dt, changefreq="monthly", priority="1.0")
    add_url(root, loc=f"{BASE_URL}/all/auto-topics", lastmod=dt, changefreq="monthly", priority="1.0")
    add_url(root, loc=f"{BASE_URL}/all/automagic", lastmod=dt, changefreq="monthly", priority="1.0")

    for doi in dois:
        add_url(root, loc=f"{BASE_URL}/doi/{doi}", priority="0.9")
    xml_document = ET.tostring(root, xml_declaration=True, encoding='utf-8').decode("utf-8")
    return xml_document
