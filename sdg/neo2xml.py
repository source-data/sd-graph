import re
import os
import argparse
from io import open as iopen
from lxml.etree import parse, fromstring, Element, ElementTree, tostring, XMLSyntaxError, XMLParser, indent
from xml.sax.saxutils import escape, unescape
from random import shuffle
from math import floor
from copy import deepcopy
from pathlib import Path
from typing import Dict
from neotools.utils import inner_text
from .queries import ALL_ARTICLES, FIGURES_BY_PAPER_ID, PANEL_BY_FIG_ID
from . import DB, logger


xml_parser = XMLParser(recover=True)

def XMLArticle(d: Dict):
    e = Element('article')
    e.attrib['doi'] = d['doi']
    e.attrib['id'] = str(d['id'])
    return e


def XMLFigure(d: Dict):

    def first_sentence_as_title(xml_str: str):
        pseudo_title = ""
        # strip caption of any HTML/XML tags
        # from O'Reilly's Regular Expressions Cookbook
        xml_tag_regexp = r'''</?([A-Za-z][^\s>/]*)(?:[^>"']|"[^"]*"|'[^']*')*>'''
        fig_caption = re.sub(xml_tag_regexp, '', xml_str)
        first_sentence = re.match(r"\W*([^\n\r]*?)[\.\r\n]", fig_caption)
        if first_sentence:
            pseudo_title = first_sentence.group(1)
            pseudo_title = pseudo_title + "." # adds a dot just in case it is missing
            pseudo_title = pseudo_title.replace("..", ".") # makes sure that title finishes with a single . 
        return pseudo_title

    e = Element('fig')
    e.attrib['id'] = str(d['id'])
    figure_label_element = XMLLabel(text=d['fig_label'], tail=". ")
    e.append(figure_label_element)
    graphic_element = XMLGraphic(d={'href': d['href']})
    e.append(graphic_element)
    # title was not captured systematically in source data db; using first sentence as replacement
    pseudo_title = first_sentence_as_title(d['caption'])
    if pseudo_title:
        title_element = XMLTitle(text=pseudo_title)
        e.append(title_element)
    return e


def XMLLabel(d: Dict = None, text: str = None, tail: str = None):
    e = Element('label')
    if text is not None:
        e.text = text
    if tail is not None:
        e.tail = tail
    return e


def XMLGraphic(d: Dict = None, text: str = None, tail: str = None):
    e = Element('graphic')
    e.attrib['href'] = d['href']
    return e


def XMLTitle(attr: Dict = None, text: str = None, tail: str = None):
    e = Element('title')
    if text:
        e.text = text
    if tail:
        e.tail = tail
    return e


def XMLCaption(d: Dict = None, text: str = None, tail: str = None):
    e = Element('caption')
    return e


def XMLPanel(d: Dict = None, text: str = None, tail: str = None):
    caption = cleanup(d['caption'])
    try:
        e = fromstring(caption, parser=xml_parser)
        e.attrib['panel_id'] =  str(d['panel_id'])
        graphic_element = XMLGraphic(d={'href': d['href']})
        e.append(graphic_element)
        update_tags(e, d['tags'])
    except XMLSyntaxError as err:
        n = int(re.search(r'column (\d+)', str(err)).group(1))
        logger.error(f"XMLSyntaxError: ```{caption[n-10:n]+'!!!'+caption[n]+'!!!'+caption[n+1:n+10]}```")
        print(f"XMLSyntaxError: ```{caption[n-10:n]+'!!!'+caption[n]+'!!!'+caption[n+1:n+10]}```")
        e = None
    return e

def cleanup(panel_caption: str):
    # need protection agains missing spaces after parenthesis, typically in figure or panel labels
    parenthesis = re.search(r'(\(.*?\))(\w)', panel_caption)
    if parenthesis:
        logger.warning("adding space after closing parenthesis {}".format(re.findall(r'(\(.*?\))(\w)', panel_caption)))
        panel_caption = re.sub(r'(\(.*?\))(\w)',r'\1 \2', panel_caption)
    # protection against carriage return
    if re.search('[\r\n]', panel_caption):
        logger.warning(f"removing return characters in {panel_caption}")
        panel_caption = re.sub('[\r\n]', '', panel_caption)
    # protection against <br> instead of <br/>
    panel_caption = re.sub(r'<br>', r'<br/>', panel_caption)
    # protection against badly formed link elements
    panel_caption = re.sub(r'<link href="(.*)">', r'<link href="\1"/>', panel_caption)
    panel_caption = re.sub(r'<link href="(.*)"/>(\n|.)*</link>', r'<link href="\1">\2</link>', panel_caption)
    # protection against missing <sd-panel> tags
    if re.search(r'^<sd-panel>(\n|.)*</sd-panel>$', panel_caption) is None:
        logger.warning(f"correcting missing <sd-panel> </sd-panel> tags in {panel_caption}")
        panel_caption = '<sd-panel>' + panel_caption + '</sd-panel>'
    # protection against nested or empty sd-panel
    panel_caption = re.sub(r'<sd-panel><sd-panel>', r'<sd-panel>', panel_caption)
    panel_caption = re.sub(r'</sd-panel></sd-panel>', r'</sd-panel>', panel_caption)
    panel_caption = re.sub(r'<sd-panel/>', '', panel_caption)
    # We may loose a space that separates panels in the actual figure legend...
    panel_caption = re.sub('</sd-panel>$', ' </sd-panel>', panel_caption)
    # and then remove possible runs of spaces
    panel_caption = re.sub(r' +', r' ', panel_caption)
    return panel_caption


def update_tags(panel_xml, tags):
    # in principle all of that can be removed if using panel's formatted_caption, but unsure how reliabe it is
    tags_xml = panel_xml.xpath('.//sd-tag')
    tags_neo = {}
    for t in tags:
        # in the xml, the tag id have the format sdTag<nnn>
        tag_id = "sdTag" + t['tag_id']
        tags_neo[tag_id] = t

    # check for fantom tags: tags that are returned by sd api but are NOT in the xml
    tags_neo_id = set(tags_neo.keys())
    tags_xml_id = set([t.attrib['id'] for t in tags_xml])
    tags_not_found_in_xml = tags_neo_id - tags_xml_id
    if tags_not_found_in_xml:
        logger.warning(f"tag(s) not found: {tags_not_found_in_xml} in {tostring(panel_xml)}")

    # protection against nested tags
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

    # transfer attributes from tags_neo into the xml
    for tag in tags_xml:
        tag_id = tag.get('id', '')
        neo = tags_neo.get(tag_id, None)
        if neo is not None:
            for attr, val in neo.items():
                if attr != 'id':
                    tag.attrib[attr] = str(val)


class Compendium:

    def __init__(self, db, options):
        self.db = db
        self.options = options
        self.articles = {}
        self.fetch_articles()

    def fetch_articles(self):
        results_articles = self.db.query(ALL_ARTICLES)
        for a in results_articles:
            print(f"Article {a['doi']}")
            a_id = a['id']
            doi = a['doi']
            if doi == '':
                doi = str(a_id)
            if doi in self.articles:
                logger.warning(f'Attempt to process {doi} multiple times.')
            else:
                article_element = XMLArticle(a)
                self.fetch_figures(article_element, a_id)
                self.articles[doi] = article_element

    def fetch_figures(self, article_element, id: int):
        figure_query = FIGURES_BY_PAPER_ID
        figure_query.params = {'id': id}
        results_figures = self.db.query(figure_query)
        for f in results_figures:
            print(f"    Figure {f['fig_label']}")
            figure_element = XMLFigure(f)
            fig_id = figure_element.attrib['id']
            self.fetch_caption(figure_element, int(fig_id))
            article_element.append(figure_element)

    def fetch_caption(self, figure_element, id: int):
        caption_element = XMLCaption()
        self.fetch_panels(caption_element, id)
        figure_element.append(caption_element)

    def fetch_panels(self, caption_element, id: int):
        PANEL_BY_FIG_ID.params = {'id': id}
        results_panels = self.db.query(PANEL_BY_FIG_ID)
        for p in results_panels:
            print(f"        Panel {p['panel_label']}")
            panel_element = XMLPanel(p)
            if panel_element is not None:
                caption_element.append(panel_element)

    def split_dataset(self):
        validfract = self.options['validfract']
        testfract = self.options['testfract']
        dois = list(self.articles.keys())
        N = len(dois)
        shuffle(dois)
        train_end = floor(N * (1 - validfract - testfract))
        valid_end = floor(N * (1 - testfract))
        trainset =   {doi: self.articles[doi] for doi in dois[:train_end]}
        validation = {doi: self.articles[doi] for doi in dois[train_end:valid_end]}
        testset =    {doi: self.articles[doi] for doi in dois[valid_end:]}
        return {'train': trainset, 'valid': validation, 'test': testset}

    def save(self, path):
        datasets = self.split_dataset()
        path.mkdir()
        for subdir, dataset in datasets.items():
            subpath = path / subdir
            subpath.mkdir()
            for doi, article in dataset.items():
                doi = doi.replace(".", "_").replace("/", "-")
                filename = doi + '.xml'
                file_path = subpath / filename
                print('writing to {}'.format(str(file_path)))
                indent(article, space="    ")
                ElementTree(article).write(str(file_path), encoding='utf-8', xml_declaration=True)


def main():
    parser = argparse.ArgumentParser(description='Generating xml compendium from sd-graph neo4j database.')
    parser.add_argument('path', help='Path to the new dataset.')
    parser.add_argument('-T', '--testfract', default=0.2, type=float, help='fraction of papers in testset')
    parser.add_argument('-V', '--validfract', default=0.2, type=float, help='fraction of papers in validation set')

    args = parser.parse_args()
    path = Path(args.path)
    if path.exists():
        print(f"data {path} already exists! Aborting.")
    else:
        options = {}
        options['testfract'] = args.testfract
        options['validfract'] = args.validfract
        print(options)
        compendium = Compendium(DB, options)
        compendium.save(path)


if __name__ == "__main__":
    main()
