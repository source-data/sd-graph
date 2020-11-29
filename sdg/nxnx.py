import networkx as nx
from GraphRicciCurvature.OllivierRicci import OllivierRicci
import matplotlib.pyplot as plt
import matplotlib
from sklearn import preprocessing

matplotlib.use('TkAgg')


def viz_curvature(curv, N=5):
    curv.compute_ricci_flow(iterations=100)
    pos_curv = nx.spring_layout(curv.G, weight='weight', seed=10)
    c = nx.get_edge_attributes(curv.G, 'ricciCurvature')
    le = preprocessing.LabelEncoder()
    node_color = le.fit_transform(list(c.values()))
    nx.draw(curv.G, pos_curv, edge_cmap=plt.cm.PuOr, edge_color=node_color, node_size=50, linewidths=0, alpha=0.8)
    plt.show()


def viz_curvature_distro(curv):
    # Plot the histogram of Ricci curvatures
    plt.subplot(2, 1, 1)
    ricci_curvatures = nx.get_edge_attributes(curv.G, curvature).values()
    plt.hist(ricci_curvatures, bins=20)
    plt.xlabel('Ricci curvature')
    plt.title("Histogram of Ricci Curvatures (Karate Club)")

    # Plot the histogram of edge weights
    plt.subplot(2, 1, 2)
    weights = nx.get_edge_attributes(G, "weight").values()
    plt.hist(weights,bins=20)
    plt.xlabel('Edge weight')
    plt.title("Histogram of Edge weights (Karate Club)")

    plt.tight_layout()

if __name__ == '__main__':
    g = nx.davis_southern_women_graph()
    curv = OllivierRicci(g, alpha=0.5, method="Sinkhorn", verbose="INFO")
    curv.compute_ricci_curvature()
    viz_curvature()
