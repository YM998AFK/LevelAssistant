"""Dump myblock definitions (custom block definitions)."""
import json
import sys
from pathlib import Path


def dump_block(b, depth=0, indent='  '):
    out = []
    while b:
        name = b.get('define', '?')
        sections = b.get('sections', [])
        params_str = []
        children_blocks = []
        for sec in sections:
            for p in sec.get('params', []):
                if isinstance(p, dict):
                    if p.get('type') == 'var':
                        params_str.append(repr(p.get('val')))
                    elif p.get('type') == 'block':
                        v = p.get('val')
                        if isinstance(v, dict):
                            sub = dump_block(v, 0, '')
                            params_str.append('[' + ' '.join(sub).strip() + ']')
                        else:
                            params_str.append(str(v))
                    else:
                        params_str.append(json.dumps(p, ensure_ascii=False))
                else:
                    params_str.append(str(p))
            for ch in sec.get('children', []):
                children_blocks.append(ch)
        out.append(indent * depth + name + '(' + ', '.join(params_str) + ')')
        for ch in children_blocks:
            sub = dump_block(ch, depth + 1, indent)
            out.extend(sub)
        b = b.get('next')
    return out


def main():
    p = Path(sys.argv[1])
    d = json.loads(p.read_text(encoding='utf-8'))

    def walk(node):
        if isinstance(node, dict):
            if 'myblocks' in node:
                for mb in node['myblocks']:
                    print('\n=== MyBlock:', mb.get('displayName'), '(', mb.get('name'), ')')
                    frag = mb.get('fragment', {})
                    for ln in dump_block(frag.get('head', {})):
                        print(ln)
            for v in node.values():
                if isinstance(v, (dict, list)):
                    walk(v)
        elif isinstance(node, list):
            for v in node:
                walk(v)

    walk(d)


if __name__ == '__main__':
    main()
