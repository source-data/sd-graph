import argparse
from .sdapi import SDAPI
from . import DB


def create_graph(collection_name):
    N = 0
    skipped = {'paper': [], 'figure': [], 'panel': []}
    sdapi = SDAPI(collection_name)
    total = len(sdapi)
    for doi in sdapi.doi_list:
        print(f"Trying paper {doi}")
        a = sdapi.article(doi)
        if a is None:
            print(f"paper with doi={doi} cold not be retrieved")
            skipped['paper'].append(doi)
        else:
            article_node = DB.node(a)
            N+=1
            for fig_id in a.children:
                print(f"    Trying figure {fig_id}")
                f = sdapi.figure(doi, fig_id)
                if f is None:
                    print(f"figure {fig_id} from doi={doi} cold not be retrieved")
                    skipped['figure'].append(f"{doi}: {fig_id}")
                else:
                    figure_node = DB.node(f)
                    N+=1
                    DB.relationship(article_node, figure_node, "has_figure")
                    for panel_id in f.children:
                        print(f"        Trying panel {panel_id}")
                        p = sdapi.panel(panel_id)
                        if p is None:
                            print(f"panel {panel_id} cold not be retrieved")
                            skipped['panel'].append(panel_id)
                        else:
                            p_node = DB.node(p)
                            N+=1
                            DB.relationship(figure_node, p_node, 'has_panel')
                            print(f"            Trying {len(p.children)} tags.")
                            for tag_data in p.children:
                                tag = sdapi.tag(tag_data)
                                tag_node = DB.node(tag)
                                DB.relationship(p_node, tag_node, 'has_tag')
                                N+=1
    return total, skipped, N
    
if __name__ == "__main__":

    parser = argparse.ArgumentParser( description="Uploads collection to neo4j datatbase" )
    parser.add_argument('collections', nargs='+', help="Name(s) of the collection(s) to download")
    args = parser.parse_args()
    collections = args.collections

    print("Importing: "+", ".join(collections))
    for collection in collections:
        collection = collection.strip()
        total, skipped, N = create_graph(collection)
        print(f"created: {N} nodes from {total} papers for collection {collection}")
        print("skipped items:")
        print(skipped)
