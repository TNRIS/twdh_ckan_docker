import glob
import os
import subprocess

patch_files = glob.glob("./patches/*.patch")

for patch_path in patch_files:
    print(f"RUNNING PATCH AT {patch_path}...")
    output = subprocess.Popen(
        f"git am {patch_path}", stdout=subprocess.PIPE, shell=True)
    (out, err) = output.communicate()
    os.system(f"echo {out}")
    print(out)
