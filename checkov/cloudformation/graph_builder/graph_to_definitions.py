import os
from typing import List, Dict, Any, Tuple

from checkov.cloudformation.graph_builder.graph_components.block_types import CloudformationTemplateSections, BlockType
from checkov.cloudformation.graph_builder.graph_components.blocks import CloudformationBlock
from checkov.cloudformation.parser.node import dict_node


def convert_graph_vertices_to_definitions(
    vertices: List[CloudformationBlock], root_folder: str
) -> Tuple[Dict[str, Dict[str, Any]], Dict[str, Dict[str, Any]]]:
    definitions: Dict[str, Dict[str, Any]] = {}
    breadcrumbs: Dict[str, Dict[str, Any]] = {}
    for vertex in vertices:
        if vertex.block_type != BlockType.RESOURCE:
            continue
        block_path = vertex.path
        block_type = CloudformationTemplateSections.RESOURCES.value if vertex.block_type == 'resource' else vertex.block_type
        block_name = vertex.name.split('.')[-1]  # vertex.name is "type.name" so type.name -> [type, name]

        definition = {
            'Type': vertex.attributes['resource_type'],
            'Properties': vertex.config
        }
        definitions.setdefault(block_path, {}).setdefault(block_type, {}).setdefault(block_name, definition)

        relative_block_path = f"/{os.path.relpath(block_path, root_folder)}"
        add_breadcrumbs(vertex, breadcrumbs, relative_block_path)
    return definitions, breadcrumbs


def add_breadcrumbs(vertex: CloudformationBlock, breadcrumbs: Dict[str, Dict[str, Any]], relative_block_path: str) -> None:
    vertex_breadcrumbs = vertex.breadcrumbs
    if vertex_breadcrumbs:
        breadcrumbs.setdefault(relative_block_path, {})[vertex.name] = vertex_breadcrumbs
