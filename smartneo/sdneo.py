import time
from .eebapi import EEBAPI
from . import DB


API = EEBAPI()


def create_graph():
    skipped = {'article': [], 'figure': [], 'panel': [], 'tags': []}
    total = len(API)
    articles, article_nodes, articles_skipped = create_nodes(API.article, API.doi_list)
    skipped['article'] = articles_skipped
    N = len(articles)
    for a, a_node in zip(articles, article_nodes):
        print(f"trying article {a.doi}")
        figures, figure_nodes, skipped_figures = create_nodes(API.figure, a.children, a.doi)
        create_relationships(a_node, figure_nodes, 'has_fig')
        skipped['figure'].append(skipped_figures)
        N += len(figures)
        for f, f_nodes in zip(figures, figure_nodes):
            print(f"    trying figure {f.fig_label}")
            panels, panel_nodes, skipped_panels = create_nodes(API.panel, f.children)
            create_relationships(f_nodes, panel_nodes, 'has_panel')
            skipped['panel'].append(skipped_panels)
            N += len(panels)
            for p, p_node in zip(panels, panel_nodes):
                print(f"        trying panel {p.panel_label}")
                tags, tag_nodes, skipped_tags = create_nodes(API.tag, p.children)
                create_relationships(p_node, tag_nodes, 'has_tag')
                skipped['tags'].append(skipped_tags)
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

    print("Importing COVID19 preprints")
    total, skipped, N = create_graph()
    print(f"created: {N} nodes from {total} papers")
    print("skipped items:")
    print(skipped)
