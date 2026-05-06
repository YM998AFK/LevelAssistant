"""一次性全面扫描 ws 中所有引擎常见崩溃点"""
import sys, json, pathlib
sys.stdout.reconfigure(encoding='utf-8')

WS_PATH = pathlib.Path('output/new/汉诺塔挑战_workdir/b8212e928dc647cfb659bc74e0cff402.ws')
ws = json.loads(WS_PATH.read_bytes().decode('utf-8'))

VEC3_KEYS = {'Position', 'Size', 'EulerAngles', 'Scale', 'BoundsCenter', 'BoundsSize'}
issues = []

def scan(obj, path=''):
    if isinstance(obj, dict):
        # 1. Vector3 元素必须是字符串
        for k in VEC3_KEYS:
            if k in obj and isinstance(obj[k], list):
                for i, v in enumerate(obj[k]):
                    if not isinstance(v, str):
                        issues.append(('VEC3_NOT_STR', f'{path}.{k}[{i}]', v))

        # 2. props2 变量必须有 "value" 键（不是 "val"）
        if 'props2' in obj:
            for vname, vdef in obj['props2'].items():
                if isinstance(vdef, dict) and 'val' in vdef and 'value' not in vdef:
                    issues.append(('PROPS2_VAL_NOT_VALUE', f'{path}.props2.{vname}', vdef))

        # 3. Effect 的 AssetId 必须是整数
        if obj.get('type') == 'Effect':
            aid = obj.get('props', {}).get('AssetId')
            if isinstance(aid, str):
                issues.append(('EFFECT_ASSETID_STR', path, aid))

        # 4. block param: 字符串/数字/bool 类型必须有 "value"
        t = obj.get('type')
        if t in ('string', 'number', 'bool', 'color') and 'value' not in obj and 'val' not in obj:
            issues.append(('PARAM_MISSING_VALUE', path, obj))

        for k, v in obj.items():
            scan(v, f'{path}.{k}')
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            scan(v, f'{path}[{i}]')

scan(ws)

if issues:
    print(f"发现 {len(issues)} 个问题：")
    for kind, path, val in issues:
        print(f"  [{kind}] {path} = {val!r}")
else:
    print("✅ 未发现结构问题，ws 应可正常导入。")
