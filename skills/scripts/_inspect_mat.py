import sys, re
sys.stdout.reconfigure(encoding='utf-8')
from pathlib import Path

MEISHU = Path(r'D:\meishu\Assets\BundleResources')

# 找几个 mat 文件，看 shader 引用格式
mats = list(MEISHU.rglob('*.mat'))[:5]
print(f'找到 {len(list(MEISHU.rglob("*.mat")))} 个 mat 文件')
for mat in mats:
    print(f'\n=== {mat.name} ===')
    try:
        txt = mat.read_text(encoding='utf-8', errors='ignore')
        for line in txt.splitlines()[:30]:
            if any(k in line for k in ['Shader', 'shader', 'RenderQueue', 'Emission', 'Keywords', 'm_Name']):
                print(' ', line.strip())
    except Exception as e:
        print('  读取失败:', e)
