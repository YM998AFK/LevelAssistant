import sys, json, os
sys.stdout.reconfigure(encoding='utf-8')

agent_file = r'C:\Users\Hetao\.cursor\projects\c-Users-Hetao-Desktop\agent-tools\efd26796-73bb-471d-b04b-4d880543cf59.txt'
with open(agent_file, 'r', encoding='utf-8') as f:
    resp = json.load(f)

data = resp['data']
out = r'C:\Users\Hetao\Desktop\公司\output\new\_ws_data_only.json'
with open(out, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, separators=(',', ':'))
print('written', os.path.getsize(out), 'bytes to', out)
