import argparse
from typing import List
from .queries import SDARTICLE_LOADING_STATUS, DELETE_TREE, SET_STATUS, COLLECTION_NAMES
from . import DB, logger


class SDNeo:

    def __init__(self, api, db):
        self.db = db
        self.api = api

    def create_graph(self, collection_names: List[str]):
        collection_node = self.create_collection(collection_names)
        return collection_node

    def create_collection(self, collection_names: List[str]):
        # there can be only 1 single collection that serves as root to the graph
        # even if several collection_names are provided, a single collection_node is returned 
        # that includes unique children aggregated over the several collections
        # collection, collection_node, skipped_collection_ids = self.create_nodes(self.api.collection, collection_names)
        collection = self.api.collection(collection_names)
        collection_node = self.db.node(collection)
        logger.info(f"collections {collection.name} with {len(collection.children)} children")
        article_nodes = self.create_articles(collection.children)
        self.create_relationships(collection_node, article_nodes, 'has_article')
        return collection_node

    def create_articles(self, doi_list: List[str]):
        def filter_existing_complete_articles(doi_list: List[str]):
            filtered_list = []
            for doi in doi_list:
                results = self.db.query(SDARTICLE_LOADING_STATUS(params={'doi': doi}))  # 'complete' | 'partial' | 'absent'
                if results:
                    if results[0]['status'] == 'partial':
                        self.db.query(DELETE_TREE(params={'doi': doi}))
                        print(f"deleted tree for {doi}")
                        filtered_list.append(doi)
                else:
                    filtered_list.append(doi)
            return filtered_list

        filtered_doi_list = filter_existing_complete_articles(doi_list)
        articles, article_nodes, skipped_articles = self.create_nodes(self.api.article, filtered_doi_list)
        for a in articles:
            self.db.query(SET_STATUS(params={'doi': a.doi, 'status': 'partial'}))
        if skipped_articles:
            logger.warning(f"Skipped articles: {', '.join([a.doi for a in skipped_articles])}")
        for a, a_node in zip(articles, article_nodes):
            if not a.doi:
                logger.warning(f"!!!! Article '{a.title}'' has no doi.")
                print(f"!!!! Article '{a.title}'' has no doi.")
            else:
                logger.info(f"article {a.doi}")
                print(f"article {a.doi}")
                figure_nodes = self.create_figures(a.children, a.doi)
                self.create_relationships(a_node, figure_nodes, 'has_fig')
                self.db.query(SET_STATUS(params={'doi': a.doi, 'status': 'complete'}))
        return article_nodes

    def create_figures(self, figure_list, doi):
        figures, figure_nodes, skipped_figures = self.create_nodes(self.api.figure, figure_list, doi)
        if skipped_figures:
            logger.warning(f"Skipped figures: {', '.join([f.fig_label for f in skipped_figures])}")
        if not (figures and figure_nodes):
            logger.warning(f"!!!! skipped creating any figure for {doi}")
            print(f"!!!! skipped creating any figure for {doi}")
        else:
            for f, f_nodes in zip(figures, figure_nodes):
                logger.info(f"    figure {f.fig_label}")
                print(f"    figure {f.fig_label}")
                panel_nodes = self.create_panels(f.children)
                self.create_relationships(f_nodes, panel_nodes, 'has_panel')
        return figure_nodes

    def create_panels(self, panel_list):
        panels, panel_nodes, skipped_panels = self.create_nodes(self.api.panel, panel_list)
        if skipped_panels:
            logger.warning(f"Skipped panels: {', '.join([p.panel_label for p in skipped_panels])}")
        if not (panels and panel_nodes):
            logger.warning(f"!!!! skipped creating any panels.")
            print(f"!!!! skipped creating any panels.")
        else:
            for p, p_node in zip(panels, panel_nodes):
                logger.info(f"        panel {p.panel_label}")
                print(f"        panel {p.panel_label}")
                tag_nodes = self.create_tags(p.children)
                self.create_relationships(p_node, tag_nodes, 'has_tag')
        return panel_nodes

    def create_tags(self, tag_list):
        tags, tag_nodes, skipped_tags = self.create_nodes(self.api.tag, tag_list)
        return tag_nodes

    def create_nodes(self, api_method, item_list, *args):
        items = []
        skipped = []
        nodes = []
        for item in item_list:
            a = api_method(item, *args)
            if a is not None:
                items.append(a)
            else:
                skipped.append(item)
        if items:
            label = items[0].label
            batch = [n.properties for n in items]
            nodes = self.db.batch_of_nodes(label, batch)
        return items, nodes, skipped

    def create_relationships(self, source, targets, rel_label):
        rel = None
        if targets:
            rel_batch = [{'source': source.id, 'target': target.id} for target in targets]
            rel = self.db.batch_of_relationships(rel_batch, rel_label, clause='CREATE')
        return rel


def import_as_one_collection(collections, api_name, db):
    if api_name == 'eebapi':
        from .eebapi import EEBAPI
        sdneo = SDNeo(api=EEBAPI(), db=DB)
    else:
        from .sdapi import SDAPI
        sdneo = SDNeo(api=SDAPI(), db=DB)
    print(f"Importing: {', '.join(collections)} with api={api_name}")
    sdneo.create_graph(collection_names=collections)
    print(f"Imported {', '.join(collections)} papers.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Uploads collections to neo4j datatbase")
    parser.add_argument('collections', nargs="+", help="Name(s) of the collection(s) to download (multiple collections separated by space)")
    parser.add_argument('--api', choices=['sdapi', 'eebapi'], default='sdapi', help="Name of the REST api to use.")
    args = parser.parse_args()
    api_name = args.api
    collections = args.collections

    if collections == ['subject_collections']:
        # subject collections are each imported separately
        subject_names = DB.query(COLLECTION_NAMES())
        for subject in subject_names:
            import_as_one_collection(subject, api_name, db=DB)
    else:
        # multiple collections are aggregated into one
        import_as_one_collection(collections, api_name, db=DB)
