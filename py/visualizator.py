import networkx as nx
import matplotlib.pyplot as plt

from py.fsm import FiniteStateMachine, Transition
from py.node import Node
from py.tree import Tree


def hierarchy_pos(g, root, levels=None, width=1., height=1.):
    total = "total"
    current = "current"

    def make_levels(levels, node=root, current_level=0, parent=None):
        if not current_level in levels:
            levels[current_level] = {total: 0, current: 0}
        levels[current_level][total] += 1
        neighbors = g.neighbors(node)
        for neighbor in neighbors:
            if not neighbor == parent:
                levels = make_levels(levels, neighbor, current_level + 1, node)
        return levels

    def make_pos(pos, node=root, current_level=0, parent=None, vert_loc=0):
        dx = 1 / levels[current_level][total]
        left = dx / 2
        pos[node] = ((left + dx * levels[current_level][current]) * width, vert_loc)
        levels[current_level][current] += 1
        neighbors = g.neighbors(node)
        for neighbor in neighbors:
            if not neighbor == parent:
                pos = make_pos(pos, neighbor, current_level + 1, node, vert_loc - vert_gap)
        return pos

    if levels is None:
        levels = make_levels({})
    else:
        levels = {l: {total: levels[l], current: 0} for l in levels}
    vert_gap = height / (max([l for l in levels]) + 1)
    return make_pos({})


class Visualizator:
    model = None
    edges = []
    nodes = []
    edge_labels = {}
    nodes_labels = {}
    count = 1
    graph = nx.Graph()

    def __init__(self, tree: Tree):
        self.model = tree
        self.define_tree(self.model.root, 1)

    def define_tree(self, node: Node, parent_pos: int):
        temp = str(node.value) + '\n' + str(node.nullable) + '\n' + str(node.first_pos) + '\n' + str(node.last_pos)
        self.nodes_labels.update({self.count: temp})
        self.nodes.append(self.count)
        if parent_pos != self.count:
            self.edges.append((parent_pos, self.count))
        temp_count = self.count
        self.count += 1
        if node.left is not None:
            self.define_tree(node.left, temp_count)
        if node.right is not None:
            self.define_tree(node.right, temp_count)

    def show_tree(self):
        self.graph.add_edges_from(self.edges)
        pos = hierarchy_pos(self.graph, 1)
        nx.draw(self.graph, pos, node_color='white')
        nx.draw_networkx_labels(self.graph, pos, self.nodes_labels, font_size=7, node_size=50)
        plt.show()

    # def __init__(self, fsm: FiniteStateMachine):
    #     self.model = fsm
    #     labels = {}
    #     count = 0
    #     for state in self.model.transitions:
    #         # self.edge_labels.update({count: state.by})
    #         self.edge_labels[count] = state.by
    #         self.edges.append((state.from_state, state.to_state))
    #         count += 1
    #
    # def draw_automat(self):
    #
    #     self.graph.add_edges_from(self.edges)
    #     nx.draw(self.graph)
    #     pos = nx.spring_layout(self.graph)
    #     nx.draw_networkx_edge_labels(self.graph, pos)
    #     plt.show()
