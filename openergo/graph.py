import glob
import json
import os
import re
from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List

import graphviz

from openergo.utility import Utility


class Node(ABC):
    def __init__(self, name: str) -> None:
        self._name: str = ".".join(sorted(set(name.split("."))))
        self._nodes: List[Node] = []
        nodes.append(self)

    def add_node(self, node: "Node") -> None:
        self._nodes.append(node)

    def __str__(self) -> str:
        return self._name

    @abstractmethod
    def attr(self) -> Dict[str, Any]:
        pass

    @property
    def nodes(self) -> List["Node"]:
        return self._nodes


nodes: List[Node] = []


class Component(Node):
    def __init__(self, config: Dict[str, Any]) -> None:
        super().__init__(Utility.deep_get(config, "name"))
        self._config: Dict[str, Any] = config

    def config(self, key: str) -> Any:
        return Utility.deep_get(self._config, key, None)

    def attr(self) -> Dict[str, Any]:
        is_def: int = int(bool(self.config("shell.procedure")))
        result: Dict[str, Any] = {
            "fontcolor": "#222222",
            "color": "#888888",
            "style": ["dashed", "solid"][is_def],
            "penwidth": "4",
            "fixedsize": "true",
            "shape": "circle",
            "width": "3",
            "label": f'<<table border="0" cellborder="0"><tr><td bgcolor="#EEEEEE">{str(self)}</td></tr></table>>',
        }
        return result


class Edge(Node):
    def attr(self) -> Dict[str, Any]:
        return {
            "fontcolor": "#222222",
            "fixedsize": "false",
            "shape": "none",
            "label": str(self),
        }


def add_configs(configs: List[Dict[str, Any]], folder: str) -> None:
    config_files: List[str] = glob.glob(
        os.path.join(folder, "**/*.json"), recursive=True)

    for config_file in config_files:
        with open(config_file, "r", encoding="utf8") as stream:
            config_json: Any = json.load(stream)
            if isinstance(config_json, list):
                configs.extend(config_json)
            elif isinstance(config_json, dict) and "name" in config_json:
                configs.append(config_json)


def load_configs(folders: List[str]) -> List[Dict[str, Any]]:
    configs: List[Dict[str, Any]] = []

    for folder in folders:
        add_configs(configs, folder)
    return configs


def do_graph(keys: List[str], folders: List[str]) -> None:
    cfgs: List[Dict[str, Any]] = load_configs(folders)
    for config in cfgs:
        for key in keys:
            build_graph(Edge(key), config, cfgs)


def build_graph(
        out_edge: Edge, cfg: Dict[str, Any], cfgs: List[Dict[str, Any]]) -> None:
    out_key: str = str(out_edge)
    get_key: Callable[[str], Any] = lambda key: Utility.deep_get(cfg, key)

    for input_keys in get_key("input.keys"):
        input_keys_parts: List[str] = [
            part for part in input_keys.split(".") if part]
        negated_keys: set[str] = {part[1:]
                                  for part in input_keys_parts if part.startswith("~")}
        required_keys: set[str] = {
            part for part in input_keys_parts if not part.startswith("~")}
        out_key_parts: set[str] = set(out_key.split("."))

        if required_keys <= out_key_parts and not negated_keys & out_key_parts:
            in_edge: Edge = Edge(input_keys)
            out_edge.add_node(in_edge)

            component: Component = Component(cfg)
            in_edge.add_node(component)

            for output_key in get_key("output.keys"):
                do_substitution(
                    input_keys,
                    output_key,
                    out_key,
                    cfgs,
                    component)


def do_substitution(
    input_key: str,
    output_key: str,
    routingkey: str,
    cfgs: List[Dict[str, Any]],
    component: Component,
) -> None:
    derived_key: str = re.sub(
        r"\?",
        ".".join(set(routingkey.split(".")) - set(input_key.split("."))),
        output_key,
    )
    outbound: Edge = Edge(derived_key)

    for config in cfgs:
        build_graph(outbound, config, cfgs)

    if derived_key != output_key:
        interim: Edge = Edge(output_key)
        interim.add_node(outbound)
        outbound = interim

    component.add_node(outbound)


def graph(folders: List[str], rks: List[str]) -> None:
    do_graph(rks, folders)

    dot: graphviz.Digraph = graphviz.Digraph(comment="Component Diagram")
    dot.attr("graph", bgcolor="#EEEEEE", nodesep="5", pad="1", rankdir="TB")
    dot.attr("edge", color="#888888")
    dot.attr("node", fontcolor="#222222", fontname="courier", fontsize="30")

    edges: set[tuple[str, str]] = set()
    for node in nodes:
        dot.node(str(node), **node.attr())
        for child in node.nodes:
            if str(node) == str(child):
                continue
            edges.add((str(node), str(child)))
    for edge in edges:
        dot.edge(*edge, color="#888888", arrowsize="1.0", minlen="3")

    dot.render(".graph.gv", view=True)
