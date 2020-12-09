import networkx as nx
import numpy as np
from cdlib.algorithms import spinglass
from neotools.db import Query
from sklearn.feature_extraction.text import TfidfVectorizer
from math import isnan
from collections import OrderedDict
from . import DB


class ENTITY_AS_NODE(Query):
    code = '''
MATCH 
    (coll:SDCollection)-->(a:SDArticle)-[r:HasH]->(h:Hypothesis),
    (source:H_Entity)-->(h:Hypothesis)-->(target:H_Entity)
WHERE
    source.type IN ['gene', 'protein', 'geneprod'] AND 
    target.type IN ['gene', 'protein', 'geneprod'] AND
    a.journalName = 'biorxiv'
    AND (h.n_articles >= $threshold OR h.n_panels >= 2 * $threshold)
    AND (NOT h.self_test)
    AND (NOT source.boring) AND (NOT target.boring)
    AND (NOT source.name IN split('.,-()abcdefg1234567890', ''))
    AND (NOT target.name IN split('.,-()abcdefg1234567890', ''))
WITH DISTINCT
    source, target, a
WITH DISTINCT
    source, target,
    COLLECT(DISTINCT a.pub_date) AS aggregated_pub_dates,
    COLLECT(DISTINCT a.doi) AS dois,
    COUNT(DISTINCT a) AS n_articles
RETURN DISTINCT {
    source: {id: id(source), description: source.name},
    target: {id: id(target), description: target.name}
} AS edge
    '''
    returns = ['edge']


class SUMMARIES_BY_HYP_COMMUNITY(Query):
    code = '''
MATCH (h:H_Entity)
WHERE EXISTS(h.hypothesis_community)
WITH h
ORDER BY h.community_centrality DESC
WITH
  COLLECT(DISTINCT h) AS entities, 
  COLLECT(DISTINCT h.name) AS entity_names,
  h.hypothesis_community AS community_id
ORDER BY community_id
MATCH 
  (a:SDArticle)-[r1:HasH]->(hyp:Hypothesis)-[r2]-(h:H_Entity)
WHERE h.hypothesis_community = community_id
WITH DISTINCT 
  a, 
  community_id,
  entity_names,
  entities, 
  COUNT(DISTINCT h) AS overlap_size,  // NEED TO COMPUTE ENRICHMENT AND THRESHOLD BASE ON HYPERGEOM http://metascape.org/blog/?p=122
  SUM(DISTINCT r1.n_panels) AS n_panels
ORDER BY community_id ASC, overlap_size DESC, n_panels DESC
RETURN
  COLLECT(DISTINCT a.title) AS summaries,  // we could choose to use abstracts or something else
  COLLECT(DISTINCT a.doi) AS dois,
  entities,
  entity_names,
  community_id;
    '''
    returns = ['community_id', 'summaries', 'dois', 'entities', 'entity_names']


class ALL_SUMMARIES(Query):
    code = '''
MATCH 
    (coll:SDCollection)-->(a:SDArticle)-[r:HasH]->(h:Hypothesis)
WHERE
    a.journalName = 'biorxiv'
RETURN DISTINCT
    a.title AS summary  // we could aslo choose to use abstract or something else
    '''
    returns = ['summary']


class RESET_CENTRALITY_PROPERTIES(Query):
    code = '''
MATCH (h:H_Entity)
SET h.general_centrality = NULL, h.hypothesis_community = NULL, h.community_centrality = NULL
RETURN COUNT(h) AS reset_entities
    '''
    returns = ['reset_entities']


class DELETE_AUTO_TOPICS(Query):
    code = '''
MATCH (a:SDAutoTopics) DETACH DELETE a
RETURN COUNT(a) AS deleted
    '''
    returns = ['deleted']


class MERGE_AUTO_TOPICS_COLLECTION(Query):
    code = '''
MERGE (autotopics:SDAutoTopics {community_id: $community_id, topics: $topics})
WITH autotopics
MATCH (a:SDArticle)
WHERE a.doi in $dois
MERGE (autotopics)-[:has_article]->(a)
WITH autotopics
MATCH (entity:H_Entity)
WHERE id(entity) in $entities_ids
MERGE (autotopics)-[:has_highlighted_entity]->(entity)
RETURN autotopics
    '''
    returns = ['autotopics']


def full_graph(q):
    results = DB.query(q)
    g = nx.DiGraph()
    for r in results:
        source = r['edge']['source']
        target = r['edge']['target']
        g.add_node(source['id'], description=source['description'])
        g.add_node(target['id'], description=target['description'])
        g.add_edge(source['id'], target['id'])
    return g


def community_sub_graphs(g, funct):
    communities = funct(g)
    communities_sorted = sorted(communities, key=len, reverse=True)
    return [g.subgraph(nbunch) for nbunch in communities_sorted]


def list_subgraph_central(
    subgraphs,
    funct=None,
    percentile=5,
    **kwargs
):
    highlights = OrderedDict()
    for i, subg in enumerate(subgraphs):
        print(f"{i}: {len(subg)} nodes with CC={nx.average_clustering(subg):.3f}")
        centrality = funct(subg, **kwargs)
        centrality = {k: v for k, v in centrality.items() if not isnan(v)}
        centrality_values = list(centrality.values())
        N = len(centrality)
        threshold_value = np.percentile(centrality_values, 100 - percentile)
        centrality_filtered = dict(filter(lambda e : e[1] > threshold_value, centrality.items()))
        centrality_sorted = OrderedDict(sorted(centrality_filtered.items(), key=lambda e: e[1], reverse=True))  # nodeId: centrality_value
        highlights[i] = centrality_sorted
        for j, (node_id, val) in enumerate(centrality_sorted.items()):
            print(f"\t{j}: {subg.nodes[node_id]['description']} ({val:.3f})")
    return highlights


def name_hypothesis_community():
    def select_best(corpus, collections):
        vectorizer = TfidfVectorizer(
            stop_words='english',
            token_pattern=r'[ΑαΒβΓγΔδΕεΖζΗηΘθΙιΚκΛλΜμΝνΞξΟοΠπΡρΣσςΤτΥυΦφΧχΨψΩωA-Za-z0-9\-–—‐−]{3,}',
            max_df=0.01,
            min_df=0
        )
        vectorizer.fit_transform(corpus)
        keywords = vectorizer.get_feature_names()
        concatenated_summaries = []
        for community_id, module in collections.items():
            summaries = module['summaries']
            concatenated_summaries.append(' '.join([a for a in summaries]))
        X = vectorizer.transform(concatenated_summaries)
        keywords = vectorizer.get_feature_names()
        N, M = X.shape
        X = X.toarray()
        community_ids = list(collections.keys())
        for i in range(N):
            d = {keywords[j]: X[i][j] for j in range(M)}
            d = sorted(d.items(), key=lambda e: e[1], reverse=True)
            n = min(10, len(d))  #  max 10 topics
            topics = dict(d[:n]).keys()  # the top10 keywordss
            community_id = community_ids[i]
            entity_names = collections[community_id]['entity_names']
            topics = [t for t in topics if t not in entity_names]
            collections[community_id]['topics'] = topics
            print(f"Collection topics: {', '.join(topics[:5])}")
            print(f"Key entities: {', '.join(entity_names)}")
            print()

    results_corpus = DB.query(ALL_SUMMARIES())
    corpus = [r['summary'] for r in results_corpus]
    results_modules = DB.query(SUMMARIES_BY_HYP_COMMUNITY())
    collections = {}
    for r in results_modules:
        community_id = r['community_id']
        collections[community_id] = {
            'entities': r['entities'],
            'entity_names': r['entity_names'],
            'summaries': r['summaries'],
            'dois': r['dois']
        }
    select_best(corpus, collections)
    # uptdate database
    deleted = DB.query(DELETE_AUTO_TOPICS())
    print(f"{deleted[0]['deleted']} nodes deleted")
    for community_id, collection in collections.items():
        entities_ids = [entity.id for entity in collection['entities']]
        q = MERGE_AUTO_TOPICS_COLLECTION(params={
            'community_id': community_id,
            'topics': collection['topics'],
            'entities_ids': entities_ids,
            'dois': collection['dois']
        })
        r = DB.query(q)
        print(f"create auto topics collection {r[0]['autotopics']['topics']}")


def automagic(g, community_funct, highlight_funct):
    components = community_sub_graphs(g, funct=nx.weakly_connected_components)
    gcc = components[0]
    print(f"CENTRALITY ON ENTIRE GCC COMPONENTS")
    general_highlights = list_subgraph_central([gcc], funct=highlight_funct)
    general_highlights = general_highlights[0]  # only one element

    subgraphs_hyp = community_sub_graphs(gcc, funct=community_funct)
    print(f"CENTRALITY ON {len(subgraphs_hyp)} COMMUNITIES FROM THE GCC ({len(gcc)} elements)")
    community_highlights = list_subgraph_central(subgraphs_hyp, funct=highlight_funct)
    return general_highlights, community_highlights


def neo2nx(threshold=2):
    def community_funct(x): return spinglass(x.to_undirected()).communities
    def highlight_funct(x): return nx.load_centrality(x, normalized=True)
    g_entity_as_nodes = full_graph(ENTITY_AS_NODE(params={'threshold': threshold}))
    print("ENTITY CENTRALITY")
    print(nx.info(g_entity_as_nodes))
    general_highlights, community_highlights = automagic(g_entity_as_nodes, community_funct, highlight_funct)
    return general_highlights, community_highlights


def nx2neo(general_highlights, community_highlights):
    print("Writing results to database")
    res = DB.query(RESET_CENTRALITY_PROPERTIES())
    assert res[0]['reset_entities'] > 0, "centrality properties could not be reset properly"
    for node_id, val in general_highlights.items():
        DB.update_node(node_id, {'general_centrality': val})
    for communityId, highlights in community_highlights.items():
        for node_id, val in highlights.items():
            DB.update_node(node_id, {'hypothesis_community': communityId, 'community_centrality': val})


def main():
    general_highlights, community_highlights = neo2nx()
    nx2neo(general_highlights, community_highlights)
    name_hypothesis_community()


if __name__ == "__main__":
    main()
