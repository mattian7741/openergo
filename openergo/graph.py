import glob
import json
import os
import re
from abc import ABC, abstractmethod
from typing import Any, Dict, List

import graphviz
from openergo.utility import Utility


class Node(ABC):
    def __init__(self, name: str) -> None:
        self.name: str = ".".join(sorted(set(name.split("."))))
        self.children: List['Node'] = []

    def add_child(self, child: 'Node') -> None:
        self.children.append(child)

    @abstractmethod
    def graphviz_attr(self) -> Dict[str, Any]:
        pass


class Component(Node):
    def __init__(self, config: Dict[str, Any]) -> None:
        super().__init__(Utility.deep_get(config, "name"))
        self.config = config

    def graphviz_attr(self) -> Dict[str, Any]:
        is_defined = bool(self.config.get("package") and self.config.get("lib_func"))
        return {
            "fontcolor": "#ffffff" if is_defined else "#000000",
            "color": "#ffffff80" if is_defined else "#00000080",
            "style": "solid" if is_defined else "dashed",
            "penwidth": "4",
            "fixedsize": "true",
            "shape": "circle",
            "width": "3",
            "label": f'<{self.name}>',
        }


class Edge(Node):
    def graphviz_attr(self) -> Dict[str, Any]:
        return {
            "shape": "none",
            "label": self.name,
        }


class GraphManager:
    def __init__(self):
        self.nodes = []
        self.edges = []

    def add_node(self, node: Node):
        self.nodes.append(node)

    def add_edge(self, from_node: Node, to_node: Node):
        self.edges.append((from_node, to_node))

    def render_graph(self):
        dot = graphviz.Digraph(comment="Component Diagram")
        dot.attr('graph', bgcolor="#0071BD", nodesep="5", pad="1", rankdir="TB")
        dot.attr('node', fontcolor="#ffffff", fontname="courier", fontsize="30")
        dot.attr('edge', color="#ffffff80")

        for node in self.nodes:
            dot.node(node.name, **node.graphviz_attr())

        for from_node, to_node in self.edges:
            dot.edge(from_node.name, to_node.name)

        dot.render(".graph.gv", view=True)


def parse_configs(folder: str) -> List[Dict[str, Any]]:
    config_files = glob.glob(os.path.join(folder, "**/*.json"), recursive=True)
    configs = []
    for file in config_files:
        with open(file, "r", encoding="utf8") as f:
            data = json.load(f)
            if isinstance(data, list):
                configs.extend(data)
            elif isinstance(data, dict) and "name" in data:
                configs.append(data)
    return configs


def build_graph(manager: GraphManager, configs: List[Dict[str, Any]]):
    for config in configs:
        component = Component(config)
        manager.add_node(component)
        # Logic to add edges based on config
        # Example: manager.add_edge(prev_component, component)

# Usage
manager = GraphManager()
config_data = parse_configs("path/to/config/folder")
build_graph(manager, config_data)
manager.render_graph()
