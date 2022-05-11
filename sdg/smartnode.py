from enum import auto
import os
import pdb
import re
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List, Union
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from lxml.etree import (
    Element, ElementTree,
    XMLParser, parse, XMLSyntaxError,
    fromstring, tostring
)
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from tqdm.autonotebook import tqdm

load_dotenv()
SD_API_URL = os.getenv("SD_API_URL")
SD_API_USERNAME = os.getenv("SD_API_USERNAME")
SD_API_PASSWORD = os.getenv("SD_API_PASSWORD")

try:
    # central logging facility in sd-graph
    import common.logging
    common.logging.configure_logging()
    logger = common.logging.get_logger(__name__)
except ImportError:
    import logging
    logging.basicConfig()
    logger = logging.getLogger(__name__)
    logger.setLevel("INFO")


class ResilientRequests:

    def __init__(self, user=None, password=None):
        self.session_retry = self.requests_retry_session()
        if user is not None and password is not None:
            self.session_retry.auth = (user, password)
        self.session_retry.headers.update({
            "Accept": "application/json",
            "From": "thomas.lemberger@embo.org"
        })

    @staticmethod
    def requests_retry_session(
        retries=4,
        backoff_factor=0.3,
        status_forcelist=(500, 502, 504),
        session=None,
    ):
        # from  https://www.peterbe.com/plog/best-practice-with-retries-with-requests
        session = session if session is not None else requests.Session()
        retry = Retry(
            total=retries,
            read=retries,
            connect=retries,
            backoff_factor=backoff_factor,
            status_forcelist=status_forcelist,
        )
        adapter = HTTPAdapter(max_retries=retry)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        return session

    def request(self, url: str, params: Dict = None) -> Dict:
        data = {}
        try:
            response = self.session_retry.get(url, params=params, timeout=30)
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, str):
                    logger.error(f"skipping {url}: response is string and not json data: '''{data}'''")
                    data = {}
            else:
                logger.debug(f"failed loading json object with {url} ({response.status_code})")
        except Exception as e:
            logger.error("server query failed")
            logger.error(e)
        finally:
            if not data:
                logger.debug(f"data from {url} remains empty")
            return data


def doi2filename(doi: str) -> str:
    return doi.replace("/", "_").replace(".", "-")


def inner_text(xml_element: Element) -> str:
    if xml_element is not None:
        return "".join([t for t in xml_element.itertext()])
    else:
        return ""


@dataclass
class Properties:
    """Maps the SourceData REST API response fields to the properties of a SmartNode"""
    source: str = "sdapi"


@dataclass
class CollectionProperties:
    collection_name: str = ""
    collection_id: str = None

    def __str__(self):
        return f'"{self.collection_name}"'


@dataclass
class ArticleProperties(Properties):
    doi: str = ""
    title: str = ""
    journal_name: str =""
    pub_date: str = ""
    pmid: str = ""
    pmcid: str = ""
    import_id: str = ""
    pub_year: str = "" # unfortunately SD has no pub_date properties
    nb_figures: int = 0

    def __str__(self):
        return f"\"{self.title}\" ({self.doi})"


@dataclass
class FigureProperties(Properties):
    paper_doi: str = ""
    figure_label: str = ""
    figure_id: str = ""
    figure_title: str = ""
    # caption: str = ""
    href: str = ""

    def __str__(self):
        return f"\"{self.figure_label}\" ({self.figure_id})"


@dataclass
class PanelProperties(Properties):
    paper_doi: str = ""
    figure_label: str = ""
    figure_id: str = ""
    panel_id: str = ""
    panel_label: str = ""
    panel_number: str = ""
    caption: str = ""
    formatted_caption: str = ""
    href: str = ""
    coords: str = ""

    def __str__(self):
        return f"\"{self.panel_number}\" ({self.panel_id})"


@dataclass
class TaggedEntityProperties(Properties):
    tag_id: str = ""
    category: str = ""
    entity_type: str = ""
    role: str = ""
    text: str = ""
    ext_ids: str = ""
    ext_dbs: str = ""
    in_caption: str = ""
    ext_names: str = ""
    ext_tax_ids: str = ""
    ext_tax_names: str = ""
    ext_urls: str = ""

    def __str__(self):
        return f"\"{self.text}\" ({', '.join(filter(lambda x: x is not None, [self.category, self.entity_type, self.role]))})"


class SourceDataAPIParser:
    """Parses the response of the SourceData REST API and maps the fields to the internal set of properties of SmartNodes"""

    @staticmethod
    def collection_props(response: List) -> CollectionProperties:
        if response:
            response = response[0]
        else:
            response = {}
        props = {
            "collection_name": response.get("name", ""),
            "collection_id": response.get("collection_id", ""),
        }
        return CollectionProperties(**props)

    @staticmethod
    def children_of_collection(response: List, collection_id: str) -> List["Article"]:
        article_ids = []
        logger.debug(f"collection {collection_id} has {len(response)} elements.")
        for article_summary in response:
            doi = article_summary.get("doi", "")
            sdid = article_summary.get("id", "")
            title = article_summary.get("title", "")
            collections = article_summary.get("collections", [])
            collection_names = [c["name"] for c in collections]
            # try to find an acceptable identifier
            if doi:
                article_ids.append(doi)
            elif sdid:
                logger.debug(f"using sdid {sdid} instead of doi for: \n{title}.")
                article_ids.append(sdid)
            else:
                logger.error(f"no doi and no sd id for {title} in collection {collection_names}.")
        # remove duplicates
        article_ids = list(set(article_ids))
        return article_ids

    @staticmethod
    def article_props(response: Dict) -> ArticleProperties:
        # {"title":"A non-death function of the mitochondrial apoptosis apparatus in immunity","year":"2019","pmcid":"SD4730","pmid":null,"doi":"10.15252/embj.2018100907","authors":"Dominik Brokatzky, Benedikt Dörflinger, Aladin Haimovici, Arnim Weber, Susanne Kirschnek, Juliane Vier, Arlena Metz, Julia Henschel, Tobias Steinfeldt, Ian, E. Gentle, Georg Häcker","journal":"A non-death function of the mitochondrial apoptosis apparatus in immunity","nbFigures":"4","tax_id":null,"taxon":null}
        nb_figures = int(response.get("nbFigures", 0))
        props = {
            "doi": response.get("doi", ""),
            "title": response.get("title", ""),
            "journal_name": response.get("journal", ""),
            "pub_date": response.get("pub_date", ""),
            "pmid": response.get("pmid", ""),
            "pmcid": response.get("pmcid", ""),
            "pub_year": response.get("year", ""),
            "nb_figures": nb_figures
        }
        return ArticleProperties(**props)

    def children_of_article(self, response: List, collection_id: str, doi: str) -> List["Figure"]:
        nb_figures = int(response.get("nbFigures", 0))
        fig_indices = range(1, nb_figures + 1)  # figures are 1-indexed
        return fig_indices

    @staticmethod
    def figure_props(response: Dict, doi: str) -> FigureProperties:
        # {"figure_id":"26788","label":"Figure 1","caption":"<p><strong>Figure 1</strong> ...</p>\n","panels":["72266","72258","72259","72260","72261","72262","72263","72264","72265"],"href":"https://api.sourcedata.io/file.php?figure_id=26788"}
        fig_title = response.get("fig_title", "")
        fig_caption = response.get("caption", "")
        if not fig_title and fig_caption:
            # strip caption of any HTML/XML tags
            cleaned_fig_caption = BeautifulSoup(fig_caption, 'html.parser').get_text()
            # from O'Reilly's Regular Expressions Cookbook
            # cleaned_fig_caption = re.sub(r'''</?([A-Za-z][^\s>/]*)(?:[^>"']|"[^"]*"|'[^']*')*>''', fig_caption, '')
            first_sentence = re.match(r"\W*([^\n\r]*?)[\.\r\n]", cleaned_fig_caption)
            if first_sentence:
                fig_title = first_sentence.group(1)
                fig_title = re.sub(r"fig[.\w\s]+\d", "", fig_title, flags=re.IGNORECASE)
                fig_title += "." # adds a dot just in case it is missing
                fig_title = fig_title.replace("..", ".") # makes sure that title finishes with a single . 
        props = {
            "paper_doi": doi,
            "figure_label": response.get("label", ""),
            "figure_id": response.get("figure_id", ""),
            "figure_title": fig_title,
            # "caption": fig_caption,
            "href": response.get("href", ""),
        }
        return FigureProperties(**props)

    def children_of_figures(self, response: List) -> List["Panel"]:
        # find the panel ids
        panel_ids = response.get("panels",[])
        return panel_ids

    @staticmethod
    def panel_props(response: Dict) -> PanelProperties:
        def cleanup(panel_caption: str):
            # need protection agains missing spaces after parenthesis, typically in figure or panel labels
            parenthesis = re.search(r'(\(.*?\))(\w)', panel_caption)
            if parenthesis:
                logger.debug("adding space after closing parenthesis {}".format(re.findall(r'(\(.*?\))(\w)', panel_caption)))
                panel_caption = re.sub(r'(\(.*?\))(\w)',r'\1 \2', panel_caption)
            # protection against carriage return
            if re.search('[\r\n]', panel_caption):
                logger.debug(f"removing return characters in {panel_caption}")
                panel_caption = re.sub('[\r\n]', '', panel_caption)
            # protection against <br> instead of <br/>
            panel_caption = re.sub(r'<br>', r'<br/>', panel_caption)
            # protection against badly formed link elements
            panel_caption = re.sub(r'<link href="(.*)">', r'<link href="\1"/>', panel_caption)
            panel_caption = re.sub(r'<link href="(.*)"/>(\n|.)*</link>', r'<link href="\1">\2</link>', panel_caption)
            # protection against spurious xml declarations
            # needs to be removed before next steps
            panel_caption = re.sub(r'<\?xml.*?\?>', '', panel_caption)
            # protection against missing <sd-panel> tags
            if re.search(r'^<sd-panel>(\n|.)*</sd-panel>$', panel_caption) is None:
                logger.debug(f"correcting missing <sd-panel> </sd-panel> tags in {panel_caption}")
                panel_caption = '<sd-panel>' + panel_caption + '</sd-panel>'
            # protection against nested or empty sd-panel
            panel_caption = re.sub(r'<sd-panel> *(<p>)* *<sd-panel>', r'<sd-panel>', panel_caption)
            panel_caption = re.sub(r'</sd-panel> *(</p>)* *</sd-panel>', r'</sd-panel>', panel_caption)
            panel_caption = re.sub(r'<sd-panel/>', '', panel_caption)
            # We may loose a space that separates panels in the actual figure legend...
            panel_caption = re.sub(r'</sd-panel>$', r' </sd-panel>', panel_caption)
            # and then remove possible runs of spaces
            panel_caption = re.sub(r' +', r' ', panel_caption)
            return panel_caption

        panel_id = response.get("current_panel_id", "") or ""
        # the SD API panel method includes "reverse" info on source paper, figures, and all the other panels
        # take the portion of the data returned by the REST API that concerns panels
        paper_info = response.get("paper") or {}
        figure_info = response.get("figure") or {}
        panels = figure_info.get("panels") or []
        # transform into dict
        panels = {p["panel_id"]: p for p in panels}
        panel_info = panels.get(panel_id) or {}
        paper_doi = paper_info.get("doi") or ""
        figure_label = figure_info.get("label") or ""
        figure_id = figure_info.get("figure_id") or ""
        panel_id = panel_info.get("panel_id") or ""  # "panel_id":"72258",
        panel_label = panel_info.get("label") or ""  # "label":"Figure 1-B",
        panel_number = panel_info.get("panel_number") or ""  # "panel_number":"1-B",
        caption = panel_info.get("caption") or ""
        caption = cleanup(caption)
        formatted_caption = panel_info.get("formatted_caption", "")
        href = panel_info.get("href") or ""  # "href":"https:\/\/api.sourcedata.io\/file.php?panel_id=72258",
        coords = panel_info.get("coords", {}) or {}  # "coords":{"topleft_x":346,"topleft_y":95,"bottomright_x":632,"bottomright_y":478}
        coords = ", ".join([f"{k}={v}" for k, v in coords.items()])
        props = {
            "paper_doi": paper_doi,
            "figure_label": figure_label,
            "figure_id": figure_id,
            "panel_id": panel_id,
            "panel_label": panel_label,
            "panel_number": panel_number,
            "caption": caption,
            "formatted_caption": formatted_caption,
            "href": href,
            "coords": coords,
        }
        return PanelProperties(**props)

    def children_of_panels(self, response: List) -> List["TaggedEntity"]:
        panel_id = response.get("current_panel_id")
        panels = response.get("figure", {}).get("panels", [])
        # transform into dict
        panels = {p["panel_id"]: p for p in panels}
        current_panel = panels[panel_id]
        tags_data = current_panel.get("tags", [])
        return tags_data

    def tagged_entity_props(self, response: List) -> TaggedEntityProperties:
        tag_id = response.get("id", "")
        category = response.get("category", "entity")
        entity_type = response.get("type", "")
        role = response.get("role", "")
        text = response.get("text", "")
        ext_ids = "///".join(response.get("external_ids", []))
        ext_dbs = "///".join(response.get("externalresponsebases", []))
        in_caption = response.get("in_caption", "") == "Y"
        ext_names = "///".join(response.get("external_names", []))
        ext_tax_ids = "///".join(response.get("external_tax_ids", []))
        ext_tax_names = "///".join(response.get("external_tax_names", []))
        ext_urls = "///".join(response.get("external_urls", []))
        props = {
            "tag_id": tag_id,
            "category": category,
            "entity_type": entity_type,
            "role": role,
            "text": text,
            "ext_ids": ext_ids,
            "ext_dbs": ext_dbs,
            "in_caption": in_caption,
            "ext_names": ext_names,
            "ext_tax_ids": ext_tax_ids,
            "ext_tax_names": ext_tax_names,
            "ext_urls": ext_urls,
        }
        return TaggedEntityProperties(**props)


@dataclass
class Relationship:
    """Specifies the target of a directional typed relationship to another SmartNode """
    rel_type: str = ""
    target: "SmartNode" = None


class XMLSerializer:
    """Recursively serializes the properties of SmartNodes and of their descendents."""

    XML_Parser = XMLParser(recover=True)

    def generate_article(self, article: "Article") -> Element:
        xml_article = Element('article', doi=article.props.doi)
        xml_article = self.add_children_of_article(xml_article, article)
        return xml_article

    def add_children_of_article(self, xml_article: Element, article: "Article") -> Element:
        figures = [rel.target for rel in article.relationships if rel.rel_type == "has_figure"]
        xml_figures = [self.generate_figure(fig) for fig in figures]
        # do this here since there might be cases where several types of relationships have to be combined
        for xml_fig in xml_figures:
            xml_article.append(xml_fig)
        return xml_article

    def generate_figure(self, figure: "Figure") -> Element:
        xml_fig = Element('fig', id=figure.props.figure_id)
        xml_title = Element('title')
        xml_title.text = figure.props.figure_title
        xml_fig.append(xml_title)
        xml_fig_label = Element('label')
        xml_fig_label.text = figure.props.figure_label
        xml_fig.append(xml_fig_label)
        graphic_element = Element('graphic', href=figure.props.href)
        xml_fig.append(graphic_element)
        xml_fig = self.add_children_of_figure(xml_fig, figure)
        return xml_fig

    def add_children_of_figure(self, xml_fig: Element, figure: "Figure") -> Element:
        panels = [rel.target for rel in figure.relationships if rel.rel_type == "has_panel"]
        xml_panels = [self.generate_panel(panel) for panel in panels]
        for xml_panel in xml_panels:
            xml_fig.append(xml_panel)
        return xml_fig

    def generate_panel(self, panel: "Panel") -> Element:
        caption = panel.props.caption
        try:
            if caption:
                xml_panel = fromstring(caption, parser=self.XML_Parser)
                # does this include a declaration?? check with 107853
            else:
                xml_panel = Element("sd-panel")
            xml_panel.attrib['panel_id'] = str(panel.props.panel_id)
            if panel.props.href:
                graphic_element = Element('graphic', href=panel.props.href)
                xml_panel.append(graphic_element)
            xml_panel = self.add_children_of_panels(xml_panel, panel)
        except XMLSyntaxError as err:
            n = int(re.search(r'column (\d+)', str(err)).group(1))
            start = max(0, n - 20)
            logger.error(f"XMLSyntaxError: ```{caption[start:n]+'!!!'+caption[n]+'!!!'}```")
            xml_panel = None
        return xml_panel

    def add_children_of_panels(self, xml_panel: Element, panel: "Panel") -> Element:
        # smart_tags are SmartNode tags
        smart_tags = [rel.target for rel in panel.relationships if rel.rel_type == "has_entity"]
        # in principle all of that can be removed if using panel's formatted_caption, but unsure how reliabe it is
        # tags_xml are the incomplete tags extracted from the panel caption
        # tags_xml have only a tag_id attribute and we need to update them to add the attributes from the SmartNode tags
        tags_xml = xml_panel.xpath('.//sd-tag')
        # smarttags_dict is a dict by tag_id
        smarttags_dict = {}
        for t in smart_tags:
            # in the xml, the tag id have the format sdTag<nnn>
            tag_id = "sdTag" + t.props.tag_id
            smarttags_dict[tag_id] = t

        # warn about fantom tags: tags that are returned by sd api but are NOT in the xml
        smarttags_dict_id = set(smarttags_dict.keys())
        tags_xml_id = set([t.attrib['id'] for t in tags_xml])
        tags_not_found_in_xml = smarttags_dict_id - tags_xml_id
        if tags_not_found_in_xml:
            logger.warning(f"tag(s) not found: {tags_not_found_in_xml} in {tostring(xml_panel)}")

        # protection against nasty nested tags
        for tag in tags_xml:
            nested_tags = tag.xpath('.//sd-tag')
            if nested_tags:
                nested_tag = nested_tags[0]  # only 1?
                logger.warning(f"removing nested tags {tostring(tag)}")
                text_from_parent = tag.text or ''
                innertext = inner_text(nested_tag)
                tail = nested_tag.tail or ''
                text_to_recover = text_from_parent + innertext + tail
                for k in nested_tag.attrib:  # in fact, sometimes more levels of nesting... :-(
                    if k not in tag.attrib:
                        tag.attrib[k] = nested_tag.attrib[k]
                tag.text = text_to_recover
                for e in tag:  # tag.remove(nested_tag) would not always work if some <i> are flanking it for example
                    tag.remove(e)
                logger.info(f"cleaned tag: {tostring(tag)}")

        # transfer attributes from smarttags_dict into the panel_xml Element
        for tag in tags_xml:
            tag_id = tag.get('id', '')
            smarttag = smarttags_dict.get(tag_id)
            if smarttag is not None:
                # SmartNode.props is a Properties dataclass, hence asdict()
                for attr, val in asdict(smarttag.props).items():
                    if attr != 'tag_id':
                        tag.attrib[attr] = str(val)
        # xml_panel has been modified in place but nevertheless return it for consistency
        return xml_panel


class SmartNode:

    # NEO4J: Instance = DB
    SD_REST_API: str = "https://api.sourcedata.io/"
    REST_API_PARSER = SourceDataAPIParser()
    # SOURCE_XML_DIR: str = "xml_source_files/"
    DEST_XML_DIR: str = "xml_destination_files/"
    XML_SERIALIZER = XMLSerializer()

    def __init__(self, ephemeral: bool = False):
        self._props: Properties = None
        self._relationships: List[Relationship] = []
        self.ephemeral = ephemeral

    def to_xml(self, *args) -> Element:
        """Serializes the object and its descendents as xml file"""
        raise NotImplementedError

    def from_sd_REST_API(self, *args) -> "SmartNode":
        """Instantiates properties and children from the SourceData REST API"""
        raise NotImplementedError

    @property
    def relationships(self) -> List[Relationship]:
        return self._relationships

    @relationships.setter
    def relationships(self, rel: List[Relationship]):
        self._relationships = rel

    @staticmethod
    def _request(url: str) -> Dict:
        response = ResilientRequests(SD_API_USERNAME, SD_API_PASSWORD).request(url)
        return response

    def _filepath(self, sub_dir: str, basename: str) -> Path:
        dest_dir = Path(self.DEST_XML_DIR)
        dest_dir.mkdir(exist_ok=True)
        dest_dir = dest_dir / sub_dir if sub_dir else dest_dir
        filename = basename + ".xml"
        filepath = dest_dir / filename
        return filepath

    def _save_xml(self, xml_element: Element, filepath: Path) -> str:
        if self.ephemeral and self.auto_save and not self.relationships:
            logger.warning(f"There are no relationships left in an ephermeral auto-saved object. Attempt to save to {str(filepath)} is likely to be a mistake.")
        if filepath.exists():
            logger.error(f"{filepath} already exists, not overwriting.")
        else:
            try:
                # xml validation before written file.
                fromstring(tostring(xml_element))
                filepath = str(filepath)
                logger.info(f"writing to {filepath}")
                ElementTree(xml_element).write(filepath, encoding='utf-8', xml_declaration=True)
            except XMLSyntaxError as err:
                logger.error(f"XMLSyntaxError in {filepath}: {str(err)}. File was NOT written.")
        return str(filepath)

    def _add_relationships(self, rel_type: str, targets: List["SmartNode"]):
        # keep _relationships as a list rather than a Dict[rel_type, nodes] in case staggered order is important
        self.relationships = self.relationships + [Relationship(rel_type=rel_type, target=target) for target in targets]

    def _finish(self) -> "SmartNode":
        if self.ephemeral:
            # reset relationships to free memory from descendants
            self.relationships = []
        return self

    def _to_str(self, level=0):
        indentation = "  " * level
        s = ""
        s += indentation + f"{self.__class__.__name__} {self.props}\n"
        for rel in self.relationships:
            s += indentation + f"-[{rel.rel_type}]->\n"
            s += rel.target._to_str(level + 1) + "\n"
        return s

    def __str__(self):
        return self._to_str()


class Collection(SmartNode):

    GET_COLLECTION = "collection/"
    GET_LIST = "/papers"

    def __init__(self, *args, auto_save: bool = True, overwrite: bool = False, sub_dir: str = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.sub_dir = sub_dir
        self.auto_save = auto_save
        self.overwrite = overwrite
        self.props = CollectionProperties()

    def from_sd_REST_API(self, collection_name: str) -> SmartNode:
        logger.debug(f"from sd API collection {collection_name}")
        url_get_collection = self.SD_REST_API + self.GET_COLLECTION + collection_name
        response_1 = self._request(url_get_collection)
        if response_1:
            self.props = self.REST_API_PARSER.collection_props(response_1)
            url_get_list_of_papers = self.SD_REST_API + self.GET_COLLECTION + self.props.collection_id + self.GET_LIST
            response_2 = self._request(url_get_list_of_papers)
            article_ids = self.REST_API_PARSER.children_of_collection(response_2, self.props.collection_id)
            articles = []
            for article_id in tqdm(article_ids, desc="articles"):
                # if collection auto save is on, each article is saved as we go
                # if the collection is ephemeral, no point in keeping relationships in article after saving and article are ephemeral too
                article = Article(
                    auto_save=self.auto_save,
                    ephemeral=self.auto_save,
                    overwrite=self.overwrite,
                    sub_dir=self.sub_dir
                )
                article.from_sd_REST_API(self.props.collection_id, article_id)
                if article is not None:
                    articles.append(article)
            self._add_relationships("has_article", articles)
        return self._finish()

    def to_xml(self, sub_dir: str = None) -> List[str]:
        filepaths = []
        # in auto save mode, the articles are saved as soon as they are created
        if self.auto_save:
            logger.warning(f"articles were saved already since auto_save mode is {self.auto_save}")
        else:
            sub_dir = sub_dir if sub_dir is not None else self.sub_dir
            for rel in self.relationships:
                if rel.rel_type == "has_article":
                    article = rel.target
                    filepath = article.to_xml(sub_dir)
                    filepaths.append(filepath)
        return filepaths


class Article(SmartNode):

    GET_COLLECTION = "collection/"
    GET_ARTICLE = "paper/"

    def __init__(self, *args, auto_save: bool = True, overwrite: bool = False, sub_dir: str = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.auto_save = auto_save
        self.overwrite = overwrite
        self.sub_dir = sub_dir
        self.props = ArticleProperties()

    def from_sd_REST_API(self, collection_id: str, doi: str) -> SmartNode:
        if collection_id and doi:
            logger.debug(f"  from sd API article {doi}")
            filepath = self._filepath(self.sub_dir, self._basename(doi))
            if self.auto_save and not self.overwrite and filepath.exists():
                logger.warning(f"{filepath} already exists, not overwriting.")
                return None
            else:
                url = self.SD_REST_API + self.GET_COLLECTION + collection_id + "/" + self.GET_ARTICLE + doi
                response = self._request(url)
                if response:
                    self.props = self.REST_API_PARSER.article_props(response)
                    fig_indices = self.REST_API_PARSER.children_of_article(response, collection_id, doi)
                    figures = []
                    for idx in tqdm(fig_indices, desc="figures ", leave=False):
                        fig = Figure().from_sd_REST_API(collection_id, doi, idx)
                        figures.append(fig)
                    self._add_relationships("has_figure", figures)
                else:
                    logger.warning(f"API response was empty, no props set for doi='{doi}'.")
                return self._finish()
        else:
            logger.error(f"Cannot create Article with empty params supplied: ('{collection_id}, {doi}')!")
            return None

    def _finish(self) -> "SmartNode":
        if self.auto_save:
            logger.info("auto saving")
            self.to_xml()
        return super()._finish()

    @staticmethod
    def _basename(doi: str) -> str:
        return doi.replace("/", "_").replace(".", "-")

    def to_xml(self, sub_dir: str = None) -> str:
        sub_dir = sub_dir if sub_dir is not None else self.sub_dir
        basename = self._basename(self.props.doi)
        filepath = self._filepath(sub_dir, basename)
        if filepath.exists() and not self.overwrite:
            logger.warning(f"{filepath} already exists, not overwriting.")
        else:
            xml = self.XML_SERIALIZER.generate_article(self)
            self._save_xml(xml, filepath)
        return filepath


class Figure(SmartNode):

    GET_COLLECTION = "collection/"
    GET_ARTICLE = "paper/"
    GET_FIGURE = "figure/"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.props = FigureProperties()

    def from_sd_REST_API(self, collection_id: str, doi: str, figure_index: str) -> SmartNode:
        if collection_id and doi and figure_index:
            logger.debug(f"    from sd API figure {figure_index}")
            url = self.SD_REST_API + self.GET_COLLECTION + collection_id + "/" + self.GET_ARTICLE + doi + "/" + self.GET_FIGURE + str(figure_index)
            response = self._request(url)
            if response:
                self.props = self.REST_API_PARSER.figure_props(response, doi)
                panel_ids = self.REST_API_PARSER.children_of_figures(response)
                panels = []
                for panel_id in tqdm(panel_ids, desc="panels  ", leave=False):
                    panel = Panel().from_sd_REST_API(panel_id)
                    panels.append(panel)
                self._add_relationships("has_panel", panels)
            return self._finish()
        else:
            logger.error(f"Cannot create Figure with empty params supplied: ('{collection_id}, {doi}')!")
            return None


class Panel(SmartNode):

    GET_PANEL = "panel/"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.props = PanelProperties()

    def from_sd_REST_API(self, panel_id: str) -> SmartNode:
        if panel_id:
            logger.debug(f"      from sd API panel {panel_id}")
            url = self.SD_REST_API + self.GET_PANEL + panel_id
            response = self._request(url)
            if response:
                self.props = self.REST_API_PARSER.panel_props(response)
                tags_data = self.REST_API_PARSER.children_of_panels(response)
                tagged_entities = [TaggedEntity().from_sd_REST_API(tag)for tag in tags_data]
                self._add_relationships("has_entity", tagged_entities)
            return self._finish()
        else:
            logger.error(f"Cannot create Panel with empty params supplied: ('{panel_id}')!")
            return None


class TaggedEntity(SmartNode):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.props = TaggedEntityProperties()

    def from_sd_REST_API(self, tag_data: List) -> SmartNode:
        logger.debug(f"        from sd tags {tag_data.get('text')}")
        self.props = self.REST_API_PARSER.tagged_entity_props(tag_data)
        return self._finish()
