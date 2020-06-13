import argparse
from . import DB, logger


class SDNeo:

    def __init__(self, api):
        self.api = api

    def create_graph(self, collection_name):
        collection = self.api.collection(collection_name)
        self.create_articles(collection.children)
        return collection

    def create_articles(self, article_list):
        articles, article_nodes, skipped_articles = self.create_nodes(self.api.article, article_list)
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

    @staticmethod
    def create_nodes(api_method, item_list, *args):
        items = []
        skipped = []
        nodes = None
        for item in item_list:
            a = api_method(item, *args)
            if a is not None:
                items.append(a)
            else:
                skipped.append(item)
        # time.sleep(0.1)
        if items:
            label = items[0].label
            batch = [n.properties for n in items]
            nodes = DB.batch_of_nodes(label, batch)
        return items, nodes, skipped

    @staticmethod
    def create_relationships(source, targets, rel_label):
        rel = None
        if targets:
            rel_batch = [{'source': source.id, 'target': target.id} for target in targets]
            rel = DB.batch_of_relationships(rel_batch, rel_label, clause='CREATE')
        return rel


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Uploads collections to neo4j database")
    parser.add_argument('collection', nargs="?", help="Name(s) of the collection(s) to download")
    parser.add_argument('--api', choices=['sdapi', 'eebapi'], default='sdapi', help="Name of the REST api to use.")
    args = parser.parse_args()
    collection = args.collection
    api_name = args.api
    if api_name == 'eebapi':
        from .eebapi import EEBAPI
        sdneo = SDNeo(api=EEBAPI())
    else:
        from .sdapi import SDAPI
        sdneo = SDNeo(api=SDAPI())
    print(f"Importing: {collection} with api={api_name}")
    collection = sdneo.create_graph(collection_name=collection)
    print(f"Imported {len(collection)} papers.")
