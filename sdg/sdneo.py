import argparse
import time
from . import DB


def create_graph(API, collection_name):
    skipped = {'article': [], 'figure': [], 'panel': [], 'tags': []}
    collection = API.collection(collection_name)
    total = len(collection)
    articles, article_nodes, articles_skipped = create_nodes(API.article, collection.children)
    skipped['article'] = articles_skipped
    N = len(articles)
    for a, a_node in zip(articles, article_nodes):
        if not a.doi:
            import pdb; pdb.set_trace()
        print(f"article {a.doi}")
        figures, figure_nodes, skipped_figures = create_nodes(API.figure, a.children, a.doi)
        create_relationships(a_node, figure_nodes, 'has_fig')
        skipped['figure'] += skipped_figures
        N += len(figures)
        if not (figures and figure_nodes):
            print(f"!!!! skipped creating any figure for {a.doi}")
        else:
            for f, f_nodes in zip(figures, figure_nodes):
                print(f"    figure {f.fig_label}")
                panels, panel_nodes, skipped_panels = create_nodes(API.panel, f.children)
                create_relationships(f_nodes, panel_nodes, 'has_panel')
                skipped['panel'] += skipped_panels
                N += len(panels)
                if not (panels and panel_nodes):
                    print(f"!!!! skipped creating any panel for {f.fig_label} for {a.doi}")
                else:
                    for p, p_node in zip(panels, panel_nodes):
                        print(f"        panel {p.panel_label}")
                        tags, tag_nodes, skipped_tags = create_nodes(API.tag, p.children)
                        create_relationships(p_node, tag_nodes, 'has_tag')
                        skipped['tags'] += skipped_tags
                        N += len(tags)
    return total, skipped, N


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
    time.sleep(0.1)
    if items:
        label = items[0].label
        batch = [n.properties for n in items]
        nodes = DB.batch_of_nodes(label, batch)
    return items, nodes, skipped


def create_relationships(source, targets, rel_label):
    rel = None
    if targets:
        rel_batch = [{'source': source.id, 'target': target.id} for target in targets]
        rel = DB.batch_of_relationships(rel_batch, rel_label)
    return rel


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Uploads collections to neo4j datatbase")
    parser.add_argument('collection', nargs="?", help="Name(s) of the collection(s) to download")
    parser.add_argument('--api', choices=['sdapi', 'eebapi'], default='sdapi', help="Name of the REST api to use.")
    args = parser.parse_args()
    collection = args.collection
    api_name = args.api
    if api_name == 'eebapi':
        from .eebapi import EEBAPI
        api = EEBAPI()
        collection = 'covid19'  # only collection available in eebapi for the moment
    else:
        from .sdapi import SDAPI
        api = SDAPI()

    print(f"Importing: {collection} with api={api_name}")
    total, skipped, N = create_graph(api, collection_name=collection)
    print(f"created: {N} nodes from {total} papers for collection {collection}")
    print("skipped items:")
    print(skipped)
