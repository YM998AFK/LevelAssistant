"""Detail dump of specific fragments with raw condition contents."""
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
    target_name = sys.argv[2] if len(sys.argv) > 2 else None
    d = json.loads(p.read_text(encoding='utf-8'))

    def deep_walk(node, parent_name=''):
        if not isinstance(node, dict):
            return
        t = node.get('type')
        props = node.get('props', {})
        name = props.get('Name', '')
        if t == 'BlockScript' and (target_name is None or parent_name == target_name):
            frags = node.get('fragments', [])
            if frags:
                print(f'\n=== BlockScript  parent=[{parent_name}]')
                for i, f in enumerate(frags):
                    print(f'-- fragment {i} --')
                    lines = dump_block(f.get('head', {}))
                    for ln in lines:
                        print(ln)
        new_parent = name if name else parent_name
        for c in node.get('children', []):
            deep_walk(c, new_parent)

    deep_walk(d.get('scene', {}), 'scene')


if __name__ == '__main__':
    main()
