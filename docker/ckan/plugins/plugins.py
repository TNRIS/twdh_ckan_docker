import json
import os
from lib.run import run

json_path = os.path.join(os.environ.get("SRC_DIR", "/"), "plugins/ckan_plugins.json")

file = open(json_path)

data = json.load(file)

GH_TOKEN = os.environ.get("GH_TOKEN", "")

class Plugin:
    def __init__(self,owner,repo,tag,branch,cmd):
        self.owner = owner
        self.repo = repo
        self.tag = tag
        self.branch = branch
        self.cmd = cmd

    def install(self):
        git = f"git clone"
        if(self.branch != ""):
            git = f"git clone -b {self.branch}"
        if(self.tag != ""):
            git = f"git clone -b {self.tag}"
        
        git = git + f" --depth 1 https://{GH_TOKEN}@github.com/{self.owner}/{self.repo} ./{self.repo}"

        print(git)

        cmds = " && ".join(self.cmd)
        
        out = run(f'''
        {git} \
        && cd {self.repo} \
        && {cmds} \
        && cd ../
        '''
        )
        print(out)

for p in data["plugins"]:
    plugin = Plugin(
        p["owner"],
        p["repo"],
        p["tag"],
        p["branch"],
        p["cmd"]
    )

    plugin.install()
