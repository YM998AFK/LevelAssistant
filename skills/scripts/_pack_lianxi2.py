import sys
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r'c:\Users\Hetao\Desktop\公司\scripts')
import pkg_utils

workdir = r'c:\Users\Hetao\Desktop\公司\output\modify\低16-2_练习2-v1_workdir'
out_zip = r'c:\Users\Hetao\Desktop\公司\output\modify\低16-2_练习2-v1.zip'

result = pkg_utils.pack_zip_clean(workdir, out_zip)
print('pack result:', result)
