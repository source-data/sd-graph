
from .eebapi import EEBAPI
from . import DB


def create_graph():
    N = 0
    skipped = {'paper': [], 'figure': [], 'panel': []}
    eebapi = EEBAPI()
    total = len(eebapi)
    for doi in eebapi.doi_list:
        print(f"Trying paper {doi}")
        a = eebapi.article(doi)
        if a is None:
            print(f"paper with doi={doi} cold not be retrieved")
            skipped['paper'].append(doi)
        else:
            article_node = DB.node(a)
            N += 1
            for fig_idx in a.children:
                print(f"    Trying figure {fig_idx}")
                f = eebapi.figure(doi, fig_idx)
                if f is None:
                    print(f"figure {fig_idx} from doi={doi} cold not be retrieved")
                    skipped['figure'].append(f"{doi}: {fig_idx}")
                else:
                    figure_node = DB.node(f)
                    N += 1
                    DB.relationship(article_node, figure_node, "has_figure")
                    # commenting request out until we have automateed panelization
                    # for panel_id in f.children:
                    #     print(f"        Trying panel {panel_id}")
                    #     p = sdapi.panel(panel_id)
                    for p in f.children:
                        if p is None:
                            print(f"panel {p.panel_id} could not be retrieved")
                            skipped['panel'].append(p.panel_id)
                        else:
                            p_node = DB.node(p)
                            N += 1
                            DB.relationship(figure_node, p_node, 'has_panel')
                            print(f"            Trying {len(p.children)} tags.")
                            for tag_data in p.children:
                                tag = eebapi.tag(tag_data)
                                tag_node = DB.node(tag)
                                DB.relationship(p_node, tag_node, 'has_tag')
                                N += 1
    return total, skipped, N


if __name__ == "__main__":

    print("Importing COVID19 preprints")
    total, skipped, N = create_graph()
    print(f"created: {N} nodes from {total} papers")
    print("skipped items:")
    print(skipped)
