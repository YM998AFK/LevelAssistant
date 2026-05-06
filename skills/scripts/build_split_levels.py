"""Split 测试-未发布版本 into 练习7 (cid=3) and 练习9 (cid=2) level zips.

Strategy: Clone the source ws, rewrite control's BlockScript and myblockdefine
to lock a specific cid, remove orphan fragments, update solution.json with a
fresh project UUID, then repack as zip under output/modify/.
"""
from __future__ import annotations
import copy
import json
import shutil
import tempfile
import uuid
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = ROOT / '参考-extracted' / '测试-未发布版本'
SRC_WS = SRC_DIR / 'a89f0fad-7509-48be-9ee0-d3d98f3575f3.ws'
SRC_SOLUTION = SRC_DIR / 'solution.json'
SRC_EXPORT = SRC_DIR / 'export_info.json'
SRC_ICON = SRC_DIR / '3fa65470-e2fc-4391-97fc-c41e9562d793.png'
OUT_DIR = ROOT / 'output' / 'modify'


def find_node_by_name(scene, name):
    for c in scene.get('children', []):
        if c.get('props', {}).get('Name') == name:
            return c
    return None


def find_blockscript_of(parent):
    for c in parent.get('children', []):
        if c.get('type') == 'BlockScript':
            return c
    return None


def var_param(val):
    return {'type': 'var', 'val': str(val)}


def block_param(val):
    return {'type': 'block', 'val': val}


def B(define, params=None, children=None, next_block=None):
    """Build a block node."""
    sec = {}
    if params is not None:
        sec['params'] = params
    if children is not None:
        sec['children'] = children
    node = {'define': define, 'sections': [sec] if sec else [{}]}
    if next_block is not None:
        node['next'] = next_block
    return node


def build_cin_cut_branch(values):
    """Build chained ListAdd blocks for cin_cut injection."""
    chain = None
    for v in reversed(values):
        new_node = {
            'define': 'ListAdd',
            'sections': [
                {'params': [var_param(v), var_param('cin_cut')]}
            ],
        }
        if chain is not None:
            new_node['next'] = chain
        chain = new_node
    return chain


def build_init_fragment(cid_value, cin_values):
    """Build the 'WhenReceiveMessage 初始化' fragment with only the relevant ListAdd chain."""
    list_add_chain = build_cin_cut_branch(cin_values)
    # WhenReceiveMessage('初始化') -> ListDeleteAll('cin_cut') -> ListAdd chain
    frag = {
        'pos': ['-1072.6', '399.4446'],
        'head': {
            'define': 'WhenReceiveMessage',
            'sections': [
                {
                    'params': [var_param('初始化')],
                    'children': [
                        {
                            'define': 'ListDeleteALl',
                            'sections': [{'params': [var_param('cin_cut')]}],
                            'next': list_add_chain,
                        }
                    ],
                }
            ],
        },
    }
    return frag


def patch_whengamestarts_frag0(frag, cid_value):
    """Modify the 'WhenGameStarts' fragment so the initial cid matches target."""
    # Fragment head: WhenGameStarts -> SetVar cid '1' -> Hide -> Forever ...
    head = frag.get('head', {})
    children = head.get('sections', [{}])[0].get('children', [])
    for ch in children:
        if ch.get('define') == 'SetVar':
            params = ch.get('sections', [{}])[0].get('params', [])
            if len(params) >= 2 and params[0].get('val') == 'cid':
                params[1]['val'] = str(cid_value)
                return
    raise RuntimeError('Could not locate SetVar cid in fragment 0')


def patch_show_fragment(frag, cid_value, i_start, repeat_count):
    """Modify fragment 2 (WhenReceiveMessage '展示关卡效果')."""
    head = frag.get('head', {})
    children = head.get('sections', [{}])[0].get('children', [])
    found_cid = False
    found_i = False
    found_repeat = False
    for ch in children:
        if ch.get('define') == 'SetVar':
            params = ch.get('sections', [{}])[0].get('params', [])
            if len(params) >= 2 and params[0].get('val') == 'cid':
                params[1]['val'] = str(cid_value)
                found_cid = True
            elif len(params) >= 2 and params[0].get('val') == 'i':
                params[1]['val'] = str(i_start)
                found_i = True
        elif ch.get('define') == 'Repeat':
            params = ch.get('sections', [{}])[0].get('params', [])
            if params:
                params[0]['val'] = str(repeat_count)
                found_repeat = True
    if not (found_cid and found_i and found_repeat):
        raise RuntimeError(
            f'Show-fragment patch failed: cid={found_cid} i={found_i} repeat={found_repeat}'
        )


def patch_myblock_cid(blockscript, cid_value):
    """Modify myblockdefine's SetVar cid."""
    myblocks = blockscript.get('myblocks', [])
    for mb in myblocks:
        if mb.get('displayName') == '初始化' or 'myblockdefine' in mb.get('name', ''):
            frag = mb.get('fragment', {})
            children = frag.get('head', {}).get('sections', [{}])[0].get('children', [])
            for ch in children:
                if ch.get('define') == 'SetVar':
                    params = ch.get('sections', [{}])[0].get('params', [])
                    if len(params) >= 2 and params[0].get('val') == 'cid':
                        params[1]['val'] = str(cid_value)
                        return
    raise RuntimeError('Could not patch myblockdefine cid')


def build_zip(
    level_label: str,
    cid_value: int,
    i_start: int,
    repeat_count: int,
    cin_values: list,
    out_zip: Path,
):
    src_data = json.loads(SRC_WS.read_text(encoding='utf-8'))
    data = copy.deepcopy(src_data)

    scene = data['scene']
    control = find_node_by_name(scene, 'control')
    if control is None:
        raise RuntimeError('control node not found')
    control_script = find_blockscript_of(control)
    if control_script is None:
        raise RuntimeError('control BlockScript not found')

    frags = control_script.get('fragments', [])
    # Expected indexes: 0=WhenGameStarts, 1=成绩判断, 2=展示关卡效果,
    # 3=空 WhenGameStarts (orphan), 4=初始化, 5-8=orphans.

    # Patch myblockdefine cid
    patch_myblock_cid(control_script, cid_value)

    # Patch fragment 0: SetVar cid
    patch_whengamestarts_frag0(frags[0], cid_value)

    # Patch fragment 2: 展示关卡效果 handler
    patch_show_fragment(frags[2], cid_value, i_start, repeat_count)

    # Rebuild fragment 4: 初始化 handler with only cin_values
    frags[4] = build_init_fragment(cid_value, cin_values)

    # Drop orphan fragments: 3 (empty WhenGameStarts) and 5..8
    # Keep 0, 1, 2, 4
    keep = [frags[0], frags[1], frags[2], frags[4]]
    control_script['fragments'] = keep

    # Update level name in project metadata
    # Generate new UUIDs for this project
    new_project_uuid = str(uuid.uuid4())
    new_ws_basename = str(uuid.uuid4())
    new_ws_filename = new_ws_basename + '.ws'

    # Update solution.json
    solution_data = json.loads(SRC_SOLUTION.read_text(encoding='utf-8'))
    solution_data['name'] = level_label
    solution_data['modified'] = solution_data.get('modified', 0)
    projects = solution_data.get('projects', [])
    if projects:
        proj = projects[0]
        proj['uuid'] = new_project_uuid
        # file path: pangu3d/universe/develop/{solutionUid}/{uuid}.ws
        export_info = json.loads(SRC_EXPORT.read_text(encoding='utf-8'))
        solution_uid = export_info.get('solutionUid', '615929056776421384')
        proj['file'] = f'pangu3d/universe/develop/{solution_uid}/{new_ws_filename}'
        if SRC_ICON.exists():
            proj['icon'] = f'pangu3d/universe/develop/{solution_uid}/{SRC_ICON.name}'

    # Write into tmp dir then zip
    with tempfile.TemporaryDirectory() as td:
        tdp = Path(td)
        (tdp / new_ws_filename).write_text(
            json.dumps(data, ensure_ascii=False, separators=(',', ':')), encoding='utf-8'
        )
        (tdp / 'solution.json').write_text(
            json.dumps(solution_data, ensure_ascii=False, separators=(',', ':')),
            encoding='utf-8',
        )
        (tdp / 'export_info.json').write_text(
            SRC_EXPORT.read_text(encoding='utf-8'), encoding='utf-8'
        )
        if SRC_ICON.exists():
            shutil.copyfile(SRC_ICON, tdp / SRC_ICON.name)

        out_zip.parent.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(out_zip, 'w', zipfile.ZIP_DEFLATED) as zf:
            for p in tdp.iterdir():
                zf.write(p, arcname=p.name)

    # Verify
    verify_ws = json.loads(
        json.dumps(data, ensure_ascii=False)
    )  # round-trip sanity check
    vscene = verify_ws['scene']
    vctrl = find_node_by_name(vscene, 'control')
    vscript = find_blockscript_of(vctrl)
    vfrags = vscript['fragments']
    assert len(vfrags) == 4, f'expected 4 fragments kept, got {len(vfrags)}'
    # Print confirmation
    print(f'\n[Built] {out_zip.name}')
    print(f'  level name : {level_label}')
    print(f'  cid        : {cid_value}')
    print(f'  i_start    : {i_start}')
    print(f'  repeat     : {repeat_count}')
    print(f'  cin_cut    : {cin_values}')
    print(f'  ws file    : {new_ws_filename}')
    print(f'  project uuid: {new_project_uuid}')


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    # 练习7 → cid=3, i=2, Repeat=2, uses 医药包 data
    build_zip(
        level_label='检查物资箱-练习7',
        cid_value=3,
        i_start=2,
        repeat_count=2,
        cin_values=[15, 8, 20, 5, 12, 9, 18, 3, 11, 14],
        out_zip=OUT_DIR / '检查物资箱-练习7-v1.zip',
    )

    # 练习9 → cid=2, i=2, Repeat=3, uses 矿泉水 data
    build_zip(
        level_label='检查物资箱-练习9',
        cid_value=2,
        i_start=2,
        repeat_count=3,
        cin_values=[12, 8, 15, 20, 5, 18, 30, 25, 10, 22],
        out_zip=OUT_DIR / '检查物资箱-练习9-v1.zip',
    )


if __name__ == '__main__':
    main()
