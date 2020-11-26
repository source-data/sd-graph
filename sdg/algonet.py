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

# xhost + 127.0.0.1; docker-compose run --rm -e DISPLAY=host.docker.internal:0 flask python -m sdg.algonet

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
from pathlib import Path
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
# TODO: [ ] test PMFG https://gmarti.gitlab.io/networks/2018/06/03/pmfg-algorithm.html
# TODO: [ ] try in neo4j louvain and betweenness and then inter community bridges
# TODO: [ ] give name to cluster based on top TF IDF of concatenated titles.
# TODO: [ ] empirical p-value based on whole network distribution of centrality
# TODO: [ ] make movie of percolation centrality
# TODO: [ ] species, type, normalization features by graphSAGE
# TODO: [ ] extract keypharses form ref report with gds.nlp amazonw



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
    (source:Hypothesis)-[:hyp_chain]->(target:Hypothesis),
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
    apoc.coll.toSet(COLLECT(DISTINCT a.doi) + COLLECT(DISTINCT b.doi)) AS dois,
    apoc.coll.toSet(COLLECT(DISTINCT a.pub_date) + COLLECT(DISTINCT b.pub_date)) AS aggregated_pub_dates
RETURN DISTINCT {
    source: {id: id(source), description: source.description, dois: dois, aggregated_pub_dates: aggregated_pub_dates, n_panels: source.n_panels},
    target: {id: id(target), description: target.description, dois: dois, aggregated_pub_dates: aggregated_pub_dates, n_panels: target.n_panels}
} AS edge
    '''
    returns = ['edge']


class ENTITY_AS_NODE(Query):
    code = '''
MATCH 
    (coll:SDCollection)-->(a:SDArticle)-[r:HasH]->(h:Hypothesis),
    (source:H_Entity)-->(h:Hypothesis)-->(target:H_Entity)
WHERE
    source.type IN ['gene', 'protein', 'geneprod'] AND target.type IN ['gene', 'protein', 'geneprod'] AND
    // coll.name = 'PUBLICSEARCH' AND
    a.journalName = 'biorxiv'
    // coll.name IN ['Cell Biology', 'Molecular Biology', 'Biochemistry', 'Cancer Biology', 'Developmental Biology', 'Microbiology'] AND
    AND DATETIME(a.pub_date) < DATETIME($date)
    AND (h.n_articles >= $threshold OR h.n_panels >= 2 * $threshold)
    // AND r.rank <= 5
    AND (NOT h.self_test)
    AND (NOT source.boring) AND (NOT target.boring)
    AND (NOT source.name IN split('.,-()abcdefg1234567890', ''))
    AND (NOT target.name IN split('.,-()abcdefg1234567890', '')) //AND
    // id(source) > id(target)  // if undirected, avoid permutation
WITH DISTINCT
    source, target, a
WITH DISTINCT
    source, target,
    COLLECT(DISTINCT a.pub_date) AS aggregated_pub_dates,
    COLLECT(DISTINCT a.doi) AS dois
RETURN DISTINCT {
    source: {id: id(source), description: source.name, dois: dois, aggregated_pub_dates: aggregated_pub_dates},
    target: {id: id(target), description: target.name, dois: dois, aggregated_pub_dates: aggregated_pub_dates}
} AS edge
    '''
    returns = ['edge']


class CONCEPT_AS_NODE(Query):
    code = '''
MATCH 
    (coll:SDCollection)-->(a:SDArticle)-[r:HasH]->(h:Hypothesis),
    (source:Concept)-->(h:Hypothesis)-->(target:Concept)
WHERE
    source.type = 'geneproduct' AND target.type = 'geneproduct' AND
    // coll.name = 'PUBLICSEARCH'
    a.journalName = 'biorxiv'
    // coll.name IN ['Cell Biology', 'Molecular Biology', 'Biochemistry', 'Cancer Biology', 'Developmental Biology', 'Microbiology'] AND
    // coll.name = 'covid19'
    // DATETIME(a.pub_date) < DATETIME($date)
    AND h.n_panels >= $threshold
    AND (NOT source.concept_name IN split('.,-()abcdefg1234567890', ''))
    AND (NOT target.concept_name IN split('.,-()abcdefg1234567890', ''))
    // AND r.rank <= 2
WITH DISTINCT 
    source, target,
    COLLECT(a.pub_date) AS aggregated_pub_dates,
    SUM(h.n_panels) AS n_panels
RETURN DISTINCT
    {
        source: {id: source.concept_id, description: source.concept_name, dois: [], aggregated_pub_dates: aggregated_pub_dates, n_panels: n_panels},
        target: {id: target.concept_id, description: target.concept_name, dois: [], aggregated_pub_dates: aggregated_pub_dates, n_panels: n_panels}
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


def update_state(g, limit_datetime, date_format='%Y-%m-%d'):
    pub_date_info = g.nodes('aggregated_pub_dates')
    for nodeId, aggregated_dates in pub_date_info:
        aggregated_dates = [datetime.strptime(date, date_format) for date in aggregated_dates]
        most_recent = max(aggregated_dates)
        state = most_recent <= limit_datetime
        g.nodes[nodeId]['state'] = state
    # return g # not needed, g is by ref and mutable


def full_graph(q):
    results = DB.query(q)
    g = nx.DiGraph()
    for r in results:
        source = r['edge']['source']
        target = r['edge']['target']
        g.add_node(source['id'], description=source['description'], dois=source.get('dois', []), aggregated_pub_dates=source.get('aggregated_pub_dates'), n_panels=source.get('n_panels'))
        g.add_node(target['id'], description=target['description'], dois=target.get('dois', []), aggregated_pub_dates=target.get('aggregated_pub_dates'), n_panels=target.get('n_panels'))
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
    curv = OllivierRicci(g.to_undirected(), alpha=0.9, exp_power=0.9, method="Sinkhorn", verbose="INFO")
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


def list_subgraph_central(
    subgraphs,
    stats, 
    funct=None,
    percentile=5,
    max=100,
    pos=None,
    viz=False,
    viz_g=None,
    show=True,
    with_labels=True,
    path=None,
    **kwargs
):
    highlights = OrderedDict()
    for i, subg in enumerate(subgraphs[:max]):
        print(f"{i}: {len(subg)} nodes with CC={nx.average_clustering(subg):.3f}")
        centrality = funct(subg, **kwargs)
        # elminate nan values
        centrality = {k:v for k, v in centrality.items() if not isnan(v)}
        # normalize with -log(freq_in_panels)
        # centrality_normalized = centrality  # OrderedDict()
        # for nodeId, val in centrality.items():
        #     n_panels = subg.nodes[nodeId]['n_panels']
        #     freq_in_panels = n_panels / stats['N_panels']
        #     somehow val should be rescaled based on the distribution?
        #     also freq should be relative to subgraph, not full db
        #     centrality_normalized[nodeId] = val * (-log(freq_in_panels))
        # centrality_values = list(centrality_normalized.values())
        centrality_values = list(centrality.values())
        N = len(centrality)
        threshold_value = np.percentile(centrality_values, 100 - percentile)
        centrality_filtered = dict(filter(lambda e : e[1] > threshold_value, centrality.items()))
        centrality_sorted = OrderedDict(sorted(centrality_filtered.items(), key=lambda e: e[1], reverse=True))  # nodeId: centrality_value
        highlights[i] = centrality_sorted
        # hist_metric(subg, centrality)
        for j, (node_id, val) in enumerate(centrality_sorted.items()):
            node = subg.nodes[node_id]
            p = sum(x >= val for x in centrality_values) / N
            print(f"\t{j}: {node.get('description')} ({val:.3f}, p(x>val)={p:.2f})")
        if viz:
            selected_nodes = centrality_sorted.keys()
            if viz_g is None:
                for nodeId in selected_nodes:
                    assert nodeId in subg.nodes()
                viz_centrality(subg, centrality, highlights=selected_nodes, pos=pos, path=path, with_labels=with_labels, show=show)
            else:
                for nodeId in selected_nodes:
                    assert nodeId in viz_g.nodes()
                viz_centrality(viz_g, centrality, highlights=selected_nodes, pos=pos, path=path, with_labels=with_labels, show=show)
    return highlights


def curvature_layout(g):
    curv4display = OllivierRicci(g.to_undirected(), alpha=0.3, exp_power=0.5, method="Sinkhorn", )
    curv4display.compute_ricci_curvature()
    # curv4display.compute_ricci_flow(iterations=5)
    N = len(g)
    pos = nx.spring_layout(curv4display.G, k=1/(8*N**0.5), weight='weight', seed=4)
    return pos


def viz_centrality(subg, centrality, highlights=[], pos=None, with_labels=True, path='', show=True):
    # check https://graph-tool.skewed.de/
    labels = {id: f"{subg.nodes[id]['description']}" for id in highlights}
    # colors = dict(subg.nodes('state'))
    # bi_color = ['lemonchiffon', 'gold']  # https://matplotlib.org/3.1.0/gallery/color/named_colors.html
    # colors = {k: bi_color[int(state)] for k, state in subg.nodes('state')}
    le = preprocessing.LabelEncoder()
    color_codes = le.fit_transform(list(centrality.values()))
    color_codes = [0.5 + (0.3 * (c - 0.5)) for c in color_codes]  # rescale to be more in the pastel range of the cmap
    colors = dict(zip(subg.nodes, color_codes))
    colors = [colors.get(id, 0) for id in subg]
    # node_size = [10+40*state for nodeId, state in dict(subg.nodes('state')).items()]
    pos = curvature_layout(subg) if pos is None else pos
    fig, ax = plt.subplots()
    # fig.set_dpi(300)
    fig.set_figheight(800 / fig.dpi)
    fig.set_figwidth(800 / fig.dpi)
    fig.set_tight_layout(True)
    ax.set_title('Network dynamics')
    nx.draw(
        subg,
        ax=ax,
        pos=pos,
        edge_color='gainsboro',
        linewidths=0,
        width=1,
        with_labels=with_labels,
        node_size=30,
        labels=labels,
        cmap=plt.cm.Blues,  # https://matplotlib.org/3.1.0/tutorials/colors/colormaps.html
        node_color=colors,  # centrality_values,
        font_size=9,
        font_family='DejaVu Sans',
        alpha=0.7)
    if path:
        print(f"saving to {path}")
        plt.savefig(path, dpi=300)
    if show:
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


def movie_dynamics(start_date="2020-01-01", end_date='2020-10-01', interval=28, threshold=2, path=Path('./movie'), index=1, add_labels=False, show=False):
    start_date = datetime.strptime(start_date, "%Y-%m-%d")
    end_date = datetime.strptime(end_date, "%Y-%m-%d")
    interval = timedelta(interval)
    limit_datetime = start_date
    g = full_graph(ENTITY_AS_NODE(params={'threshold': threshold, 'date': end_date}))
    components = community_sub_graphs(g, funct=nx.weakly_connected_components)
    final_gcc = components[0]
    final_gcc_nodeids = list(final_gcc.nodes())
    # update_state(final_gcc, limit_datetime=end_date)
    pos = curvature_layout(final_gcc)
    # WARNING: also need constant color bins.
    # if add_labels:
    #     all_ids = list(gcc.nodes)
    while limit_datetime <= end_date:
        print(f"{limit_datetime}")
        g = full_graph(ENTITY_AS_NODE(params={'threshold': threshold, 'date': limit_datetime.isoformat()}))
        components = community_sub_graphs(g, funct=nx.weakly_connected_components)
        gcc = components[0]
        for nodeId in gcc.nodes():
            assert nodeId in final_gcc_nodeids
            assert gcc.nodes[nodeId]['description'] == final_gcc.nodes[nodeId]['description']
        # update_state(gcc, limit_datetime=limit_datetime)
        file_path = path / f"network_dyn_{index}.jpg" if path else ''
        list_subgraph_central(
            [gcc], 
            None, 
            funct=lambda g: nx.load_centrality(g.to_undirected()), 
            pos=pos,
            viz_g=final_gcc,
            viz=True,
            show=show,
            with_labels=False,
            path=file_path
        )
        # viz_centrality(gcc, centrality={}, highlights=all_ids, pos=pos, path=file_path, show=show)
        limit_datetime += interval
        index += 1


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
    limit_date = '2020-11-01'  # when used as param in cypher query
    date_format = '%Y-%m-%d'  # when used in python time computations
    limit_datetime = datetime.strptime(limit_date, date_format)
    stats = {}  # get_stats(STATS(params={'threshold': threshold, 'date': limit_date}))

    g_entity_as_nodes = full_graph(ENTITY_AS_NODE(params={'threshold': threshold, 'date': limit_date}))
    update_state(g_entity_as_nodes, limit_datetime=limit_datetime)
    print("ENTITY IMPORTANCE")
    print(nx.info(g_entity_as_nodes))
    automagic(g_entity_as_nodes, community_funct, highlight_funct_e, stats, viz=True)

    # print("NOVELTY")
    # novelty_detection(threshold=2, community_funct=community_funct, highlight_funct=highlight_funct, dates=['2020-02-01', '2020-08-01'], replicates=3)

    # g_hyp_as_nodes = full_graph(HYP_AS_NODE(params={'threshold': threshold, 'date': limit_date}))
    # print("HYP SIGNIFICANCE")
    # print(nx.info(g_hyp_as_nodes))
    # automagic(g_hyp_as_nodes, community_funct, highlight_funct, stats, viz=True)


def nx2neo(centrality):
    for node_id, val in centrality:
        DB.update_node(node_id, {'centrality': val})


def demo_viz():
    g = nx.karate_club_graph()
    flip = 1
    for id in g:
        flip = 1 - flip
        g.nodes[id]['state'] = flip
    viz_centrality(g, {})


def main():
    # demo_viz()
    # movie_dynamics(start_date='2020-01-01', end_date='2020-11-01', show=False, add_labels=False, index=0)
    neo2nx()


if __name__ == "__main__":
    main()
