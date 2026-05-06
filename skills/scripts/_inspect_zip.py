import json, sys

sys.stdout.reconfigure(encoding='utf-8')

ws_path = r'c:\Users\Hetao\Desktop\公司\output\modify\低16-2_练习2-v1_workdir\55457a4f-886a-4f76-b0ce-fbed8c682ea1.ws'
with open(ws_path, encoding='utf-8') as f:
    ws = json.load(f)

# 查看 res 字段
res = ws.get('res', {})
print('res type:', type(res))
print('res keys:', list(res.keys()) if isinstance(res, dict) else 'list')
print()

def find_code_fields(obj, path='', depth=0):
    if depth > 6: return
    if isinstance(obj, dict):
        for k, v in obj.items():
            cur = path + '.' + k
            if isinstance(v, str) and len(v) > 10:
                if any(x in v for x in ['#include', 'int main', 'cout', 'cin', 'for(', 'endl']):
                    print(f'CODE FOUND at {cur}:')
                    print(repr(v[:300]))
                    print()
            find_code_fields(v, cur, depth+1)
    elif isinstance(obj, list):
        for i, item in enumerate(obj[:5]):
            find_code_fields(item, path+f'[{i}]', depth+1)

print('Searching for C++ code in entire ws...')
find_code_fields(ws)
print('Search complete.')
