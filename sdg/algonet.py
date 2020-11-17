# the joy of X11 
# on local Mac
# # from # https://medium.com/@mreichelt/how-to-show-x11-windows-within-docker-on-mac-50759f4b65cb
# allow access from localhost
# xhost + 127.0.0.1
# docker-compose run --rm -e DISPLAY=host.docker.internal:0 flask python -m sdg.algonet
# https://github.com/moby/moby/issues/8710#issuecomment-366065402
# https://unix.stackexchange.com/questions/12755/how-to-forward-x-over-ssh-to-run-graphics-applications-remotely
#
# on remote unix
# ssh -X <remote>
# on remote: X11Forwarding yes must specified in /etc/ssh/sshd_config.
# in .bashrc
# # X11 forwarding from docker
# SOCK=/tmp/.X11-unix
# export XAUTH=/tmp/.docker.xauth
# xauth nlist $DISPLAY | sed -e 's/^..../ffff/' | xauth -f $XAUTH nmerge -
# chmod 777 $XAUTH
# in docker (not sure it is needed)
# # X11 
#   && apt-get install -y x11-apps \
# in docker-compose.yml
# environment:
#       - XAUTHORITY=$XAUTH # needs to make sure export XAUTH before i.e. in .bashrc
#       - DISPLAY=$DISPLAY # this seems to be exported by default
#     volumes:
#       - .:/app
#       - ./log:/log
#       - /tmp/.X11-unix:/tmp/.X11-unix
#       - /tmp:/tmp


import networkx as nx
import numpy as np
from GraphRicciCurvature.OllivierRicci import OllivierRicci  # https://github.com/saibalmars/GraphRicciCurvature
from GraphRicciCurvature.FormanRicci import FormanRicci
import community as community_louvain  # https://github.com/taynaud/python-louvain
from . import DB
from neotools.db import Query
from sklearn import preprocessing
import matplotlib.pyplot as plt
from collections import OrderedDict
import matplotlib
matplotlib.use('TkAgg')  # supported values are ['GTK3Agg', 'GTK3Cairo', 'MacOSX', 'nbAgg', 'Qt4Agg', 'Qt4Cairo', 'Qt5Agg', 'Qt5Cairo', 'TkAgg', 'TkCairo', 'WebAgg', 'WX', 'WXAgg', 'WXCairo', 'agg', 'cairo', 'pdf', 'pgf', 'ps', 'svg', 'template']#


class HYP_AS_NODE(Query):

    code = '''
MATCH
    (source:Hypothesis)-[:hyp_chain]->(target:Hypothesis),
    (up:H_Entity)-->(source),
    (target:Hypothesis)-->(do),
    (coll:SDCollection),
    (coll)-->(a:SDArticle)-->(source),
    (coll)-->(b:SDArticle)-->(target)
WHERE
    //s a.journalName = 'biorxiv' AND
    // (coll.name = "Cell Biology" OR coll.name = "Molecular Biology" OR coll.name = "Biochemistry" OR col.name = 'Cancer Biology') AND
    //coll.name = "covid19" AND
    coll.name = "PUBLICSEARCH" AND
    source.n_panels >= $threshold AND target.n_panels >= $threshold
    AND (NOT source.self_test) AND (NOT target.self_test)
    AND (NOT up.boring) AND (NOT do.boring)
WITH DISTINCT
    source, target,
    a, b, 
    DATETIME(a.pub_date) < DATETIME($date) AS source_previously_reported,
    DATETIME(b.pub_date) < DATETIME($date) AS target_previously_reported
WITH DISTINCT
    source, target,
    COLLECT(DISTINCT a.doi) AS source_dois,
    COLLECT(DISTINCT b.doi) AS target_dois,
    apoc.convert.toFloat(SUM(apoc.convert.toFloat(source_previously_reported)) > 0) AS source_state,  // percolation state of knolwedge is represented as the fraction of papers considered as not novel
    apoc.convert.toFloat(SUM(apoc.convert.toFloat(target_previously_reported)) > 0) AS target_state  
RETURN DISTINCT {
    source: {id: id(source), description: source.description, dois: source_dois, state: source_state},
    target: {id: id(target), description: target.description, dois: target_dois, state: target_state}
} AS edge
    '''
    returns = ['edge']


class ENTITY_AS_NODE(Query):

    code = '''
MATCH 
    (col:SDCollection)-->(a:SDArticle)-[:HasH]->(h:Hypothesis),
    (source:H_Entity)-[:Is_Intervention_of]->(h:Hypothesis)-[:Has_Assayed]->(target:H_Entity)
WHERE
    // col.name = 'PUBLICSEARCH' AND
    (col.name = 'Cell Biology' OR col.name = 'Molecular Biology' OR col.name = 'Biochemistry' OR col.name = 'Cancer Biology') AND
    h.n_panels >= $threshold
    AND (NOT h.self_test)
    AND (NOT source.boring) AND (NOT target.boring)
WITH DISTINCT source, target
RETURN DISTINCT {
    source: {id: id(source), description: source.name},
    target: {id: id(target), description: target.name}
} AS edge
    '''
    returns = ['edge']


def full_graph(q):
    results = DB.query(q)
    g = nx.DiGraph()
    for r in results:
        source = r['edge']['source']
        target = r['edge']['target']
        g.add_node(source['id'], description=source['description'], dois=source.get('dois', []), state=source.get('state'))
        g.add_node(target['id'], description=target['description'], dois=source.get('dois', []), state=source.get('state'))
        g.add_edge(source['id'], target['id'])
    return g


def wcc_sub_graphs(g):
    wcc_all = nx.weakly_connected_components(g)  # Return type: generator of sets
    # print('size of wcc:', len(list(wcc_all)))
    wcc_sorted = sorted(wcc_all, key=len, reverse=True)
    return [g.subgraph(nbunch) for nbunch in wcc_sorted]


def community_sub_graphs(g, funct=nx.community.girvan_newman):
    communities = funct(g)
    communities_sorted = sorted(communities, key=len, reverse=True)
    return [g.subgraph(nbunch) for nbunch in communities_sorted]


def dict2subgraphs(g, communities):
    nbunches = {}
    for nodeId, communityId in communities.items():
        nbunches.setdefault(communityId, []).append(nodeId)
    nbunches = nbunches.values()
    subgraphs = [g.subgraph(nbunch) for nbunch in nbunches]
    return subgraphs


def louvain(g):
    communities = community_louvain.best_partition(g.to_undirected())
    # best_partition() returns Dict[nodeId, communityId] but we want List[Graph]
    dict2subgraphs(g, communities)
    return subgraphs


def curvature_communities(g):
    curv = OllivierRicci(g.to_undirected(), alpha=0.5, exp_power=1, method="Sinkhorn", verbose="INFO")
    curv.compute_ricci_flow(iterations=20)
    communities = curv.ricci_community()  # the function will return a tuple of (cutpoint, dict_of_community).
    subgraphs = dict2subgraphs(g, communities[1])
    return subgraphs


def central(g, funct, percentile=5, **kwargs):
    centrality = funct(g, **kwargs)
    threshold_value = np.percentile(list(centrality.values()), 100 - percentile)
    centrality = dict(filter(lambda e : e[1] > threshold_value, centrality.items()))
    centrality = OrderedDict(sorted(centrality.items(), key=lambda e : e[1], reverse=True))  # nodeId: centrality_value 
    return centrality


def list_subgraph_bridges(subgraphs, N=10):
    for i, subg in enumerate(subgraphs[:N]):
        print(f"{i}: {len(subg)} nodes with CC={nx.average_clustering(subg)}")
        bridges = nx.bridges(subg.to_undirected())
        for s, t in bridges:
            source = subg.nodes[s]
            target = subg.nodes[t]
            print(f"\t{i}: {source.get('description')} |||||| {target.get('description')}")


def list_subgraph_central(subgraphs, N=10, **kwargs):
    for i, subg in enumerate(subgraphs[:N]):
        print(f"{i}: {len(subg)} nodes with CC={nx.average_clustering(subg)}")
        centrality = central(subg, **kwargs)
        # hist_metric(subg, centrality)
        draw(subg, centrality)
        for node_id, val in centrality.items():
            node = subg.nodes[node_id]
            print(f"\t{i}: {node.get('description')} in {', '.join([doi for doi in node.get('dois')])} ({val})") 


def group_central(g, subgraphs):
    for i, subg in enumerate(subgraphs):
        centrality = nx.group_betweenness_centrality(g, subg)
        print(f"\t{i}: {centrality}")


def viz_curvature(curv, N=5):
    curv.compute_ricci_flow(iterations=100)
    pos_curv = nx.spring_layout(curv.G, weight='weight', seed=10)
    c = nx.get_edge_attributes(curv.G, 'ricciCurvature')
    le = preprocessing.LabelEncoder()
    node_color = le.fit_transform(list(c.values()))
    nx.draw(curv.G, pos_curv, edge_cmap=plt.cm.PuOr, edge_color=node_color, node_size=50, linewidths=0, alpha=0.8)
    plt.show()


def curvature(subgraphs, percentile=10):

    for i, subg in enumerate(subgraphs[:10]):
        print(f"{i}: {len(subg)} nodes with CC={nx.average_clustering(subg)}")
        curv = OllivierRicci(subg.to_undirected(), alpha=0.5, method="Sinkhorn", verbose="INFO")
        # curv = FormanRicci(subg)
        curv.compute_ricci_curvature()
        curvatures = []
        curvatures = nx.get_node_attributes(curv.G, 'ricciCurvature')
        threshold_value = np.percentile([x for x in curvatures.values()], percentile)
        curvatures = [(k, v) for k, v in curvatures.items() if v < threshold_value]
        curvatures_sorted = sorted(curvatures, key=lambda x: x[1], reverse=False)  # negative curvature are in bridges

        for nodeId, val in curvatures_sorted[:10]:
            node = subg.nodes[nodeId]
            print(f"\t{node['description']} ({val})")

        viz_curvature(curv)


def draw(subg, centrality, threshold_value=0):
    # if threshold_value is None:
    #     threshold_value = min(centrality.values())
    labels = {}
    colors = []
    node_size = []
    for id in subg.nodes:
        labels[id] = subg.nodes[id]['description'] if centrality.get(id, 0) > threshold_value else ''
        color = 'red' if centrality.get(id, 0) > threshold_value else 'blue'
        colors.append(color)
        size = 30 if centrality.get(id, 0) > threshold_value else 10
        node_size.append(size)
    pos = nx.spring_layout(subg, weight='weight')
    nx.draw(
        subg,
        pos=pos,
        edge_color='lightgrey',
        linewidths=0.2,
        with_labels=True,
        font_size=12,
        node_size=node_size,
        labels=labels,
        # cmap=plt.cm.get_cmap('Blues'),  # https://matplotlib.org/3.1.0/tutorials/colors/colormaps.html
        node_color=colors,  # centrality_values,
        vmin=0, vmax=0.001)
    plt.show()


def hist_metric(g, metric_name):
    # fromh ttps://graphriccicurvature.readthedocs.io/en/latest/tutorial.html
    # Plot the histogram of Ricci curvatures
    # plt.subplot(2, 1, 1)
    metric_values = nx.get_edge_attributes(g, metric_name).values()
    plt.hist(metric_values, bins=20)
    plt.title("Histogram of Ricci Curvatures")
    plt.show()


def neo2nx():
    # g_entity_as_nodes = full_graph(ENTITY_AS_NODE(params={'threshold': 2}))
    # print("CENTRALITY FULL GRAPH, ENTITIES")
    # print(nx.info(g_entity_as_nodes))

    # print("CENTRALITY SUBGRAPHS, ENTITIES")
    # list_subgraph_central([g_entity_as_nodes], funct=nx.closeness_centrality, percentile=1)

    # print("CURVATURE FULL GRAPH, ENTITIES")
    # curvature([g_entity_as_nodes])

    # print("COMMUNITIES, ENTITIES")
    # subgraphs_entity = community_sub_graphs(g_entity_as_nodes, funct=lambda x: nx.community.greedy_modularity_communities(x.to_undirected()))  # nx.community.girvan_newman
    # print("CENTRALITY ON ENTITY SUBGRAPHS")
    # list_subgraph_central(subgraphs_entity, funct=nx.closeness_centrality)

    # print("BRIDGES ON ENTITY SUBGRAPHS")
    # components = wcc_sub_graphs(g_entity_as_nodes)
    # list_subgraph_bridges(components)

    # print("CURVATURE ON ENTITY SUBGRAPHS")
    # curvature(subgraphs_entity)

    g_hyp_as_nodes = full_graph(HYP_AS_NODE(params={'threshold': 5, 'date': '2020-02-01'}))
    print("COMMUNITIES, HYP")
    print(nx.info(g_hyp_as_nodes))
    subgraphs_hyp = community_sub_graphs(g_hyp_as_nodes, funct=lambda x: nx.community.greedy_modularity_communities(x.to_undirected()))  #funct=curvature_communities) # funct=lambda x: nx.community.greedy_modularity_communities(x.to_undirected())) #nx.community.greedy_modularity_communities(x.to_undirected()))  # community_louvain.best_partition
    # list_subgraph_central(subgraphs_hyp, funct=nx.betweenness_centrality)  # nx.percolation_centrality, attribute='state'  load_centrality

    # components = wcc_sub_graphs(g_hyp_as_nodes)
    # list_subgraph_bridges(components)

    print("CURVATURE ON HYP SUBGRAPHS")
    curvature(subgraphs_hyp)


def nx2neo(centrality):
    for node_id, val in centrality:
        DB.update_node(node_id, {'centrality': val})


def main():
    neo2nx()


if __name__ == "__main__":
    main()
