# the joy of X11 
# on local Mac
# # from # https://medium.com/@mreichelt/how-to-show-x11-windows-within-docker-on-mac-50759f4b65cb
# allow access from localhost
# xhost + 127.0.0.1; docker-compose run --rm -e DISPLAY=host.docker.internal:0 flask python -m sdg.algonet
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
from cdlib.algorithms import spinglass, louvain, girvan_newman, label_propagation, infomap
from . import DB
from neotools.db import Query
from sklearn import preprocessing
import matplotlib.pyplot as plt
from math import isnan, log
from collections import OrderedDict
from datetime import datetime, timedelta
import matplotlib
matplotlib.use('TkAgg')  # supported values are ['GTK3Agg', 'GTK3Cairo', 'MacOSX', 'nbAgg', 'Qt4Agg', 'Qt4Cairo', 'Qt5Agg', 'Qt5Cairo', 'TkAgg', 'TkCairo', 'WebAgg', 'WX', 'WXAgg', 'WXCairo', 'agg', 'cairo', 'pdf', 'pgf', 'ps', 'svg', 'template']#


# TODO: [x]redo percolation now that bug on source/dataget state fixed!!!
# TODO: only dominant hypothese
# TODO: [x] temporal centrality difference
# TODO: [x] structural gap and constraint analysis to identify bridge between communities
# TODO: [ ] identify boring communities
# TODO: [ ] use undirected figure co-occurence network
# TODO: [ ] derivative network with correlation
# TODO: [ ] master regulator metrics
# TODO: [ ] derivative network from Fast Random Projection
# TODO: [x] undirected graph in neo4j query to reduce duplicates
# TODO: [x] undirected graph WHERE id(source) > id(target)
# TODO: [ ] difference between betweennness and percolatoin centrality
# TODO: [ ] normalize centrality by multiplying by -log freq of n_panels / N_panels
# TODO: [ ] generate benchmark list with random selection, by freq, by degree and by centrality and neg centrality



class STATS(Query):
    code='''
MATCH
    (coll:SDCollection)-->(a:SDArticle)-->(f:SDFigure)-->(p:SDPanel)-->(ct:CondTag)-->(e:H_Entity),
    (a)-->(h:Hypothesis)
WHERE
    e.type IN ['gene', 'protein', 'geneprod'] AND
    // coll.name = 'PUBLICSEARCH' AND
    a.journalName = 'biorxiv'
    // coll.name IN ['Cell Biology', 'Molecular Biology', 'Biochemistry', 'Cancer Biology', 'Developmental Biology', 'Microbiology'] AND
    // DATETIME(a.pub_date) < DATETIME($date)
    AND (h.n_articles >= 2 OR h.n_panels >= 2 * 2)
    AND (NOT h.self_test)
    AND (NOT e.boring)
    AND (NOT e.name IN split('.,-()abcdefg1234567890', ''))
RETURN
    COUNT(DISTINCT a) AS N_articles,
    COUNT(DISTINCT f) AS N_figures,
    COUNT(DISTINCT p) AS N_panels,
    COUNT(DISTINCT e) AS N_entities,
    COUNT(DISTINCT h) AS N_hypothesis
    '''
    returns=['N_articles', 'N_figures', 'N_panels', 'N_entities', 'N_hypothesis']


class HYP_AS_NODE(Query):

    code = '''
MATCH
    (source:Hypothesis)-->(target:Hypothesis),
    (up:H_Entity)-->(source),
    (target:Hypothesis)-->(do),
    (coll:SDCollection),
    (coll)-->(a:SDArticle)-->(source),
    (coll)-->(b:SDArticle)-->(target)
WHERE
    up.type IN ['gene', 'protein', 'geneprod'] AND do.type IN ['gene', 'protein', 'geneprod'] AND
    // DATETIME(a.pub_date) < DATETIME($date) AND DATETIME(b.pub_date) < DATETIME($date) AND
    a.journalName = 'biorxiv' AND  b.journalName = 'biorxiv' AND
    // coll.name = 'Neuroscience' AND
    // coll.name = "Microbiology" AND
    // coll.name IN ['Cell Biology', 'Molecular Biology', 'Biochemistry', 'Cancer Biology', 'Developmental Biology', 'Microbiology'] AND
    // coll.name = 'covid19' AND
    // coll.name = 'refereed preprints' AND
    // coll.name = 'PUBLICSEARCH' AND
    (
      (source.n_panels >= 2 * $threshold OR source.n_articles >= $threshold) AND
      (target.n_panels >= 2 * $threshold OR target.n_articles >= $threshold)
    )
    AND (NOT source.self_test) AND (NOT target.self_test)
    AND (NOT up.boring) AND (NOT do.boring)
    AND (NOT up.name IN split('.,-()abcdefg1234567890', ''))
    AND (NOT do.name IN split('.,-()abcdefg1234567890', '')) // AND
    //id(source) > id(target)  // if undirected, avoid permuation
WITH DISTINCT
    source, target,
    a, b, 
    DATETIME(a.pub_date) <= DATETIME($date) AS source_previously_reported,
    DATETIME(b.pub_date) <= DATETIME($date) AS target_previously_reported
WITH DISTINCT
    source, target,
    COLLECT(DISTINCT a.doi) + COLLECT(DISTINCT b.doi) AS dois,
    apoc.convert.toFloat(SUM(apoc.convert.toFloat(source_previously_reported)) > 0) AS source_state,  // percolation state of knolwedge is represented as the fraction of papers considered as not novel
    apoc.convert.toFloat(SUM(apoc.convert.toFloat(target_previously_reported)) > 0) AS target_state  
RETURN DISTINCT {
    source: {id: id(source), description: source.description, dois: [], state: source_state, n_panels: source.n_panels},
    target: {id: id(target), description: target.description, dois: [], state: target_state, n_panels: target.n_panels}
} AS edge
    '''
    returns = ['edge']


class ENTITY_AS_NODE(Query):
    code = '''
MATCH 
    (coll:SDCollection)-->(a:SDArticle)-->(h:Hypothesis),
    (source:H_Entity)-->(h:Hypothesis)-->(target:H_Entity)
WHERE
    source.type IN ['gene', 'protein', 'geneprod'] AND target.type IN ['gene', 'protein', 'geneprod'] AND
    // coll.name = 'PUBLICSEARCH' AND
    a.journalName = 'biorxiv'
    // coll.name IN ['Cell Biology', 'Molecular Biology', 'Biochemistry', 'Cancer Biology', 'Developmental Biology', 'Microbiology'] AND
    // DATETIME(a.pub_date) < DATETIME($date)
    AND (h.n_articles >= $threshold OR h.n_panels >= 2 * $threshold)
    AND (NOT h.self_test)
    AND (NOT source.boring) AND (NOT target.boring)
    AND (NOT source.name IN split('.,-()abcdefg1234567890', ''))
    AND (NOT target.name IN split('.,-()abcdefg1234567890', '')) //AND
    // id(source) > id(target)  // if undirected, avoid permutation
WITH DISTINCT 
    source, target,
    DATETIME(a.pub_date) <= DATETIME($date) AS previously_reported
WITH DISTINCT
    source, target,
    apoc.convert.toFloat(SUM(apoc.convert.toFloat(previously_reported)) > 0) AS state 
RETURN DISTINCT {
    source: {id: id(source), description: source.name, state: state},
    target: {id: id(target), description: target.name, state: state}
} AS edge
    '''
    returns = ['edge']


# class FIG_COOCURRENCE(Query):

#     code = '''
# MATCH 
#     (coll:SDCollection)-->(a:SDArticle)-[:HasCo]->(co:FigureCoOcurrence),
#     (e1:H_Entity)-[:in_fig_co]-(co)-[:in_fig_co]-(e2:H_Entity)
# WHERE
#     e1.type IN ['gene', 'protein', 'geneprod'] AND e2.type IN ['gene', 'protein', 'geneprod'] AND
#     // coll.name = 'PUBLICSEARCH' AND
#     a.journalName = 'biorxiv'
#     // coll.name IN ['Cell Biology', 'Molecular Biology', 'Biochemistry', 'Cancer Biology', 'Developmental Biology', 'Microbiology'] AND
#     // DATETIME(a.pub_date) < DATETIME($date)
#     AND (co.n_articles) >= $threshold
#     AND (NOT e1.boring) AND (NOT e2.boring)
#     AND (NOT e1.name IN split('.,-()abcdefg1234567890', ''))
#     AND (NOT e2.name IN split('.,-()abcdefg1234567890', ''))
# WITH DISTINCT 
#     e1, e2,
#     DATETIME(a.pub_date) < DATETIME($date) AS previously_reported
# WITH DISTINCT
#     e1, e2,
#     apoc.convert.toFloat(SUM(apoc.convert.toFloat(previously_reported)) > 0) AS state 
# RETURN DISTINCT {
#     source: {id: id(e1), description: e1.name, state: state},
#     target: {id: id(e2), description: e2.name, state: state}
# } AS edge
#     '''
#     returns = ['edge']


def full_graph(q):
    results = DB.query(q)
    g = nx.DiGraph()
    for r in results:
        source = r['edge']['source']
        target = r['edge']['target']
        g.add_node(source['id'], description=source['description'], dois=source.get('dois', []), state=source.get('state'), n_panels=source.get('n_panels'))
        g.add_node(target['id'], description=target['description'], dois=target.get('dois', []), state=target.get('state'), n_panels=target.get('n_panels'))
        g.add_edge(source['id'], target['id'])
    return g


def get_stats(q):
    results = DB.query(q)
    stats = {k: results[0][k] for k in q.returns}
    return stats


def community_sub_graphs(g, funct):
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


def curvature(subg):
    # negative of the curvature: positive value are the most curved bridge-like; negative are the most community like
    curv = OllivierRicci(subg, alpha=0.3, exp_power=0.5, method="Sinkhorn", verbose="INFO")
    # curv = FormanRicci(subg)
    curv.compute_ricci_curvature()
    curvatures = dict(curv.G.nodes('ricciCurvature'))
    curvatures = {k: -v for k, v in curvatures.items()}  # change size so that most neg curv are prioritized
    return curvatures


def curvature_communities(g, iterations=20):
    curv = OllivierRicci(g.to_undirected(), alpha=0.3, exp_power=0.5, method="Sinkhorn", verbose="INFO")
    curv.compute_ricci_flow(iterations=iterations)
    communities = curv.ricci_community()  # the function will return a tuple of (cutpoint, dict_of_community).
    subgraphs = dict2subgraphs(g, communities[1])
    return subgraphs


def list_subgraph_bridges(subgraphs, N=10):
    for i, subg in enumerate(subgraphs[:N]):
        print(f"{i}: {len(subg)} nodes with CC={nx.average_clustering(subg):.2f}")
        bridges = nx.bridges(subg.to_undirected())
        for s, t in bridges:
            source = subg.nodes[s]
            target = subg.nodes[t]
            print(f"\t{i}: {source.get('description')} |||||| {target.get('description')}")


def list_subgraph_central(subgraphs, stats, funct, percentile=5, max=10, viz=False, **kwargs):
    highlights = OrderedDict()
    for i, subg in enumerate(subgraphs[:max]):
        print(f"{i}: {len(subg)} nodes with CC={nx.average_clustering(subg):.3f}")
        centrality = funct(subg, **kwargs)
        # elminate nan values
        centrality = {k:v for k, v in centrality.items() if not isnan(v)}
        # normalize with -log(freq_in_panels)
        centrality_normalized = centrality  # OrderedDict()
        # for nodeId, val in centrality.items():
        #     n_panels = subg.nodes[nodeId]['n_panels']
        #     freq_in_panels = n_panels / stats['N_panels']
        #     somehow val should be rescaled based on the distribution?
        #     also freq should be relative to subgraph, not full db
        #     centrality_normalized[nodeId] = val * (-log(freq_in_panels))
        centrality_values = list(centrality_normalized.values())
        N = len(centrality)
        threshold_value = np.percentile(centrality_values, 100 - percentile)
        centrality_filtered = dict(filter(lambda e : e[1] > threshold_value, centrality_normalized.items()))
        centrality_sorted = OrderedDict(sorted(centrality_filtered.items(), key=lambda e: e[1], reverse=True))  # nodeId: centrality_value
        highlights[i] = centrality_sorted
        # hist_metric(subg, centrality)
        for j, (node_id, val) in enumerate(centrality_sorted.items()):
            node = subg.nodes[node_id]
            p = sum(x >= val for x in centrality_values) / N
            print(f"\t{j}: {node.get('description')} {', '.join([doi for doi in node.get('dois')])} ({val:.3f}, p(x>val)={p:.2f})")
        if viz:
            selected_nodes = centrality_sorted.keys()
            viz_centrality(subg, centrality, highlights=selected_nodes)
    return highlights


def viz_centrality(subg, centrality, highlights=[]):
    labels = {id: f"{subg.nodes[id]['description']}" for id in highlights}
    alpha = centrality
    # colors = dict(subg.nodes('state'))
    # le = preprocessing.LabelEncoder()
    bi_color = ['sandybrown', 'navy']  # https://matplotlib.org/3.1.0/gallery/color/named_colors.html
    colors = {k: bi_color[int(state)] for k, state in subg.nodes('state')}
    # color_codes = le.fit_transform(list(centrality.values()))
    # colors = dict(zip(subg.nodes, color_codes))
    # fancy curvature-enhanced layout
    assert len(colors) == len(subg), f"{len(colors)} colors <> subg with {len(subg)} nodes"
    curv4display = OllivierRicci(subg.to_undirected(), alpha=0.3, exp_power=0.5, method="Sinkhorn", )
    curv4display.compute_ricci_curvature()
    # curv4display.compute_ricci_flow(iterations=5)
    # some nodes are dropped in curv4display...? or some ids are changed?
    subg_nodes = dict(subg.nodes())
    subg_nodeIds = subg_nodes.keys()
    for id in curv4display.G:
        assert id in subg_nodeIds
    print(f"curvature lost {len(subg) - len(curv4display.G)}")
    colors = [colors[id] for id in curv4display.G]
    assert len(curv4display.G) == len(colors)
    N = len(curv4display.G)
    pos = nx.spring_layout(curv4display.G, k=1/(4*N**0.5), weight='weight', seed=4)
    nx.draw(
        curv4display.G,
        pos=pos,
        edge_color='lightgrey',
        linewidths=0,
        with_labels=True,
        node_size=50,
        labels=labels,
        cmap=plt.cm.seismic,  # https://matplotlib.org/3.1.0/tutorials/colors/colormaps.html
        node_color=colors,  # centrality_values,
        font_size=9,
        font_family='DejaVu Sans',
        alpha=0.8)
    plt.show()


def viz_curvature(curv, highlights=[], iterations=20):
    print(f"computing Ricci flow ({iterations} iterations)")
    curv.compute_ricci_flow(iterations=iterations)

    print("layout")
    pos_curv = nx.spring_layout(curv.G, weight='weight', seed=10)

    c_edge = nx.get_edge_attributes(curv.G, 'ricciCurvature')
    le_edge = preprocessing.LabelEncoder()
    edge_color = le_edge.fit_transform(list(c_edge.values()))

    c_node = nx.get_node_attributes(curv.G, 'ricciCurvature')
    le_node = preprocessing.LabelEncoder()
    node_color = le_node.fit_transform(list(c_node.values()))

    # labels = nx.get_node_attributes(curv.G, 'description')
    labels = {}
    for id in highlights:
        node = curv.G.nodes[id]
        labels[id] = f"{node['description']} ({node['ricciCurvature']:.2f})" 

    nx.draw(
        curv.G,
        pos_curv,
        cmap=plt.cm.seismic,
        edge_cmap=plt.cm.seismic,  # blue negative, red positive
        edge_color=edge_color,
        node_color=node_color,
        node_size=50,
        linewidths=0,
        with_labels=True,
        labels=labels,
        font_size=9,
        font_family='DejaVu Sans',
        alpha=0.8
    )
    plt.show()


def hist_metric(g, metric_name):
    # fromh ttps://graphriccicurvature.readthedocs.io/en/latest/tutorial.html
    # Plot the histogram of Ricci curvatures
    # plt.subplot(2, 1, 1)
    metric_values = nx.get_edge_attributes(g, metric_name).values()
    plt.hist(metric_values, bins=20)
    plt.title("Histogram of Ricci Curvatures")
    plt.show()


def find_inter_community_bridges(g, subgraphs):
    pass


def automagic(g, community_funct, highlight_funct, stats, viz=True):
    components = community_sub_graphs(g, funct=nx.weakly_connected_components)
    gcc = components[0]
    # list_subgraph_bridges(components)
    print(f"CENTRALITY ON ENTIRE GCC COMPONENTS")
    list_subgraph_central([gcc], stats, funct=highlight_funct, viz=viz)

    subgraphs_hyp = community_sub_graphs(gcc, funct=community_funct)
    print(f"CENTRALITY ON {len(subgraphs_hyp)} COMMUNITIES FROM THE GCC ({len(gcc)} elements)")
    list_subgraph_central(subgraphs_hyp, stats, funct=highlight_funct, viz=viz)


def novelty_detection(community_funct, highlight_funct, threshold, dates, replicates=3, N=10):
    graphs = {}
    accumul = {}
    for i, date in enumerate(dates):
        print(f"processing graph for date: {dates[i]}...")
        graphs[i] = full_graph(HYP_AS_NODE(params={'threshold': threshold, 'date': dates[i]}))
        components = community_sub_graphs(graphs[i], funct=nx.weakly_connected_components)
        gcc = components[0]  # giant connected component
        print(f"...found giant connected component of {len(gcc)} elements.")
        accumul[i] = {}
        # ranks and scores will be summed over several rounds of stochastic community detection
        for n in range(replicates):
            print(f"replicate {n}")
            subgraphs = community_sub_graphs(gcc, funct=community_funct)  # OrderedDict['subgraphId', OrderedDict['nodeId', 'centrality']] {subgraphId: {nodeId: centrality, nodeId: centrality, ...}, subgraphsId: {...}, ...}
            highlights = list_subgraph_central(subgraphs, funct=highlight_funct, percentile=100)
            for subgId, highlighted_nodes in highlights.items():
                # use subg_index which should refer to the same sugraph across replicates and across dates
                for rank, (nodeId, val) in enumerate(highlighted_nodes.items()):
                    # accumulate rank over the community detection iterations
                    accumul[i].setdefault(nodeId, 0)
                    accumul[i][nodeId] += rank if rank <= 10 else 10
    # some nodeId might be only in one accumul
    # assuming that community detection produce roughly same communities of similar size order
    diff = {}
    nodeIds = set(accumul[0].keys()) & set(accumul[1].keys())
    for nodeId in nodeIds:
        score_old = accumul[0][nodeId]
        score_new = accumul[1][nodeId]
        diff[nodeId] = {'old': score_old, 'new': score_new, 'delta': score_old - score_new}
    diff = OrderedDict(sorted(diff.items(), key=lambda x: x[1]['delta'], reverse=True))
    for i, nodeId in enumerate(diff):
        print(f"{i+1}:\t{graphs[1].nodes[nodeId]['description']}, {accumul[0][nodeId]}, {accumul[1][nodeId]}")


# def movie_novelty(start_date="2020-01-01", end_date='2020-10-01', interval=7, threshold=2, path='./movie'):
#     start_date = datetime.strptime(start_date, "%Y-%m-%d")
#     end_date = datetime.strptime(end_date, "%Y-%m-%d")
#     interval = timedelta(interval)
#     limit_date = start_date
#     g = full_graph(HYP_AS_NODE(params={'threshold': threshold, 'date': limit_date}))
#     components = community_sub_graphs(g, funct=nx.weakly_connected_components)
#     gcc = components[0]
#     # this should include pub_date as attribute so that data comparison can be done in python
#     while limit_date < end_date:
        
#         gcc = components[0]
#         viz_centrality(g, {}, {})
#         limit_date += interval


def neo2nx():
    # def community_funct(x): return nx.community.greedy_modularity_communities(x.to_undirected())
    # def community_funct(x): return louvain(x.to_undirected()).communities
    def community_funct(x): return spinglass(x.to_undirected()).communities
    # def community_funct(x): return infomap(x.to_undirected()).communities
    # def community_funct(x): return girvan_newman(x.to_undirected()).communities
    # def community_funct(x): return label_propagation(x.to_undirected()).communities
    # def community_funct(x): return curvature_communities(x.to_undirected(), iterations=50)
    #
    # def highlight_funct(x): return nx.betweenness_centrality(x)
    def highlight_funct(x): return nx.load_centrality(x)
    # def highlight_funct(x): return nx.percolation_centrality(x, attribute='state')
    # def highlight_funct(x): return nx.constraint(x)
    # def highlight_funct(x): return nx.effective_size(x)
    #
    highlight_funct_e = highlight_funct
    # def highlight_funct_e(x): return nx.load_centrality(x)
    # def highlight_funct_e(x): return nx.betweenness_centrality(x)
    # def highlight_funct_e(x): return nx.eigenvector_centrality(x)
    # def highlight_funct_e(x): return curvature(x)

    threshold = 2
    limit_date = '2020-01-31'
    stats = {}  # get_stats(STATS(params={'threshold': threshold, 'date': limit_date}))

    g_entity_as_nodes = full_graph(ENTITY_AS_NODE(params={'threshold': threshold, 'date': limit_date}))
    print("ENTITY IMPORTANCE")
    print(nx.info(g_entity_as_nodes))
    automagic(g_entity_as_nodes, community_funct, highlight_funct_e, stats, viz=False)

    # print("NOVELTY")
    # novelty_detection(threshold=2, community_funct=community_funct, highlight_funct=highlight_funct, dates=['2020-02-01', '2020-08-01'], replicates=3)

    g_hyp_as_nodes = full_graph(HYP_AS_NODE(params={'threshold': threshold, 'date': limit_date}))
    print("HYP SIGNIFICANCE")
    print(nx.info(g_hyp_as_nodes))
    automagic(g_hyp_as_nodes, community_funct, highlight_funct, stats, viz=False)


def nx2neo(centrality):
    for node_id, val in centrality:
        DB.update_node(node_id, {'centrality': val})


def main():
    # movie_novelty()
    neo2nx()


if __name__ == "__main__":
    main()
