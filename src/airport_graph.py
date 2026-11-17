import hashlib
import json
from pathlib import Path

import networkx as nx
import pandas as pd


NODE_ATTRIBUTES = ('name', 'city', 'country', 'iata', 'icao', 'latitude', 'longitude')


def build_graph_from_tables(nodes, edges):
    """Build an undirected binary graph from the shared node and edge tables."""
    required_nodes = {'airport_id', *NODE_ATTRIBUTES}
    required_edges = {'source_id', 'destination_id'}
    if not required_nodes.issubset(nodes.columns) or not required_edges.issubset(edges.columns):
        raise ValueError('Node or edge table is missing required columns.')

    nodes = nodes.copy()
    edges = edges.copy()
    for frame, fields in ((nodes, ('airport_id',)), (edges, ('source_id', 'destination_id'))):
        for field in fields:
            values = pd.to_numeric(frame[field], errors='raise')
            if values.isna().any() or (values < 0).any() or (values % 1 != 0).any():
                raise ValueError(f'{field} must contain nonnegative integer IDs.')
            frame[field] = values.astype('int64')

    if nodes['airport_id'].duplicated().any():
        raise ValueError('Airport IDs in the node table must be unique.')
    if (edges['source_id'] >= edges['destination_id']).any():
        raise ValueError('Each edge must use distinct endpoints in ascending order.')
    if edges.duplicated(['source_id', 'destination_id']).any():
        raise ValueError('The edge table must not contain duplicate pairs.')
    node_ids = set(nodes['airport_id'])
    if not set(edges['source_id']).union(edges['destination_id']).issubset(node_ids):
        raise ValueError('Every edge endpoint must appear in the node table.')

    for field in ('latitude', 'longitude'):
        nodes[field] = pd.to_numeric(nodes[field], errors='raise')

    graph = nx.Graph()
    for record in nodes.to_dict('records'):
        airport_id = int(record.pop('airport_id'))
        attributes = {field: None if pd.isna(record[field]) or record[field] == '' else record[field]
                      for field in NODE_ATTRIBUTES}
        graph.add_node(airport_id, **attributes)
    graph.add_edges_from(edges[['source_id', 'destination_id']].itertuples(index=False, name=None))
    graph.graph.update(node_key='OpenFlights airport ID', direction='undirected',
                       edge_rule='one or more retained zero-stop listings in either direction',
                       weights='none', codeshares='included')
    return graph


def load_shared_graph(directory):
    """Load and validate a graph handoff written by the participant 2 notebook."""
    directory = Path('./' + str(directory))
    with (directory / 'manifest.json').open(encoding='utf-8') as manifest_file:
        manifest = json.load(manifest_file)
    for name in ('nodes', 'edges'):
        file_info = manifest['files'][name]
        actual_hash = hashlib.sha256((directory / file_info['path']).read_bytes()).hexdigest()
        if actual_hash != file_info['sha256']:
            raise ValueError(f'{name} table does not match the manifest checksum.')

    nodes = pd.read_csv(directory / manifest['files']['nodes']['path'], dtype='string', keep_default_na=False)
    edges = pd.read_csv(directory / manifest['files']['edges']['path'], dtype='string', keep_default_na=False)
    graph = build_graph_from_tables(nodes, edges)
    if graph.number_of_nodes() != manifest['counts']['graph_nodes'] or graph.number_of_edges() != manifest['counts']['graph_edges']:
        raise ValueError('Graph size does not match the manifest.')
    return graph