"""Inspect a .ws file structure and print readable script outlines."""
import json
import sys
from pathlib import Path


def block_summary(b, depth=0, indent='  '):
    """Pretty-print a block chain with nesting."""
    out = []
    while b:
        name = b.get('define', '?')
        sections = b.get('sections', [])
        # collect params as strings
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
                            params_str.append('<' + v.get('define', '?') + '>')
                        else:
                            params_str.append(str(v))
                    else:
                        params_str.append(str(p))
                else:
                    params_str.append(str(p))
            for ch in sec.get('children', []):
                children_blocks.append(ch)
        out.append(indent * depth + name + '(' + ', '.join(params_str) + ')')
        for ch in children_blocks:
            sub = block_summary(ch, depth + 1, indent)
            out.extend(sub)
        b = b.get('next')
    return out


def fragment_summary(frag):
    head = frag.get('head', {})
    return block_summary(head, 0)


def main():
    p = Path(sys.argv[1])
    d = json.loads(p.read_text(encoding='utf-8'))

    def walk(node, path=''):
        if isinstance(node, dict):
            t = node.get('type')
            props = node.get('props', {})
            name = props.get('Name', '')
            if t == 'BlockScript':
                frags = node.get('fragments', [])
                if frags:
                    print(f'\n=== BlockScript at {path}  [parent Name={name}]')
                    for i, f in enumerate(frags):
                        print(f'-- fragment {i} --')
                        lines = fragment_summary(f)
                        for ln in lines:
                            print(ln)
            for k, v in node.items():
                if k in ('children', 'fragments', 'scene'):
                    walk(v, path + '/' + k)
                elif isinstance(v, (dict, list)):
                    walk(v, path + '/' + k)
        elif isinstance(node, list):
            for i, v in enumerate(node):
                walk(v, path + f'[{i}]')

    scene = d.get('scene', {})

    def walk_scene(node, path=''):
        if not isinstance(node, dict):
            return
        t = node.get('type')
        props = node.get('props', {})
        name = props.get('Name', '')
        if t == 'BlockScript':
            frags = node.get('fragments', [])
            if frags:
                print(f'\n=== BlockScript parent={path} name_of_parent_unknown')
                for i, f in enumerate(frags):
                    print(f'-- fragment {i} --')
                    lines = fragment_summary(f)
                    for ln in lines:
                        print(ln)
        for c in node.get('children', []):
            parent_label = name + '/' + c.get('props', {}).get('Name', c.get('type'))
            walk_scene(c, parent_label)

    # simpler: iterate scene children, find BlockScripts and report parent name
    def deep_walk(node, parent_name=''):
        if not isinstance(node, dict):
            return
        t = node.get('type')
        props = node.get('props', {})
        name = props.get('Name', '')
        if t == 'BlockScript':
            frags = node.get('fragments', [])
            if frags:
                print(f'\n=== BlockScript  parent=[{parent_name}]')
                for i, f in enumerate(frags):
                    print(f'-- fragment {i} --')
                    lines = fragment_summary(f)
                    for ln in lines:
                        print(ln)
        new_parent = name if name else parent_name
        for c in node.get('children', []):
            deep_walk(c, new_parent)

    deep_walk(scene, 'scene')


if __name__ == '__main__':
    main()
