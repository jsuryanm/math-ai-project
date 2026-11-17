"""Export an offline, dependency-free browser demonstration from the shared model."""
import json
from pathlib import Path


def export_airport_demo(graph, retained, output='airport_network_demo.html'):
    nodes = [{'id': int(i), **{k: a.get(k) for k in ('name', 'iata', 'icao', 'city', 'country')}}
             for i, a in sorted(graph.nodes(data=True))]
    fields = ['airline', 'airline_id', 'source_code', 'source_id', 'destination_code',
              'destination_id', 'codeshare', 'stops', 'equipment']
    counts = retained.drop_duplicates(subset=fields).groupby(['source_id', 'destination_id']).size()
    payload = {'nodes': nodes, 'edges': sorted([sorted(map(int, e)) for e in graph.edges]),
               'listings': [[int(s), int(t), int(v)] for (s, t), v in counts.items()]}
    template = Path(__file__).with_name('airport_demo_template.html').read_text(encoding='utf-8')
    encoded = json.dumps(payload, ensure_ascii=False).replace('<', '\\u003c')
    output = Path(output)
    output.write_text(template.replace('__AIRPORT_DATA__', encoded), encoding='utf-8')
    return output
