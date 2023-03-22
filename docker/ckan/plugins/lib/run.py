import subprocess


def run(cmd: str):
    # print(cmd)
    result = subprocess.getoutput(cmd)
    return result
