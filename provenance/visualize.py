"""Standalone accessible SVG, no Graphviz/browser dependency."""
from html import escape

COLORS={'ToolCall':'#d8ecff','ToolResult':'#e9ddff','FileVersion':'#ddf4df','PolicyFinding':'#ffd9d9','IntegrityChange':'#ffe9bc','ModelTurn':'#eeeeee','ModelRequest':'#eeeeee','TrustedTask':'#fff4bd'}

def render(graph,path):
    # Ordered nodes with all edges in a side lane; scales without hiding nodes.
    nodes=list(graph)
    index={k:i for i,k in enumerate(nodes)}
    width=1100; height=max(350,200+len(nodes)*65)
    lines=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" role="img" aria-labelledby="title desc">',
           '<title id="title">Agent evidence provenance graph</title>',
           '<desc id="desc">Nodes follow export order. Solid edges are observed evidence, dashed orange edges are uncertain hypotheses, dotted gray edges mean chronology only. No edge proves cognitive influence.</desc>',
           '<rect width="100%" height="100%" fill="white"/>',
           '<text x="20" y="25" font-size="18">Evidence DAG: observed (solid), possible (orange dashed), time only (gray dotted)</text>',
           '<text x="20" y="50" font-size="12">Types: task · model · tool call/result · file version · integrity change · policy finding. Labels include type and evidence ID.</text>',
           '<defs><marker id="arrow" markerWidth="8" markerHeight="8" refX="7" refY="3" orient="auto"><path d="M0,0 L0,6 L7,3 z" fill="#555"/></marker></defs>']
    for i,(a,b,d) in enumerate(graph.edges(data=True)):
        ya=100+index[a]*65; yb=100+index[b]*65
        lane=630+(i%16)*24
        status=d['evidence_status']; color='#c67800' if status in ('uncertain','hypothesis') else '#aaa' if status=='chronological' else '#38566b'
        dash=' stroke-dasharray="3 5"' if status=='chronological' else ' stroke-dasharray="8 4"' if status in ('uncertain','hypothesis') else ''
        label=escape(f'{a} → {b}: {d["relation"]} ({status}); {d["source_ref"]}')
        lines.append(f'<path d="M590,{ya} C{lane},{ya} {lane},{yb} 590,{yb}" fill="none" stroke="{color}"{dash} marker-end="url(#arrow)"><title>{label}</title></path>')
        lines.append(f'<text x="{lane}" y="{(ya+yb)/2}" font-size="9" fill="{color}">{escape(d["relation"])}</text>')
    for key,d in graph.nodes(data=True):
        y=100+index[key]*65
        label=f'{key} [{d["node_type"]}] {d.get("label", "")}'
        lines.extend([f'<rect x="20" y="{y-20}" width="570" height="44" rx="5" fill="{COLORS.get(d["node_type"],"#eee")}" stroke="#777"/>',f'<text x="30" y="{y-2}" font-size="11">{escape(label[:90])}<title>{escape(label)}</title></text>',f'<text x="30" y="{y+14}" font-size="10">{escape(d.get("source_ref", "")[:95])}</text>'])
    lines.append('</svg>')
    path.write_text('\n'.join(lines)+'\n')
