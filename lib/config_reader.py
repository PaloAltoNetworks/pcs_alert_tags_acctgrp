import os
import yaml
import ast


class ConfigReader(object):
    def __init__(self):
        config = self.read_yml('configs')
        res = ast.literal_eval(str(config["prisma_cloud"]))
        self.rl_user = res['username']
        self.rl_pass = res['password']
        self.rl_cust = res['customer_name']
        self.rl_api_base = res['api_base']

    @classmethod
    def read_yml(self, f):
        yml_path = os.path.join(os.path.dirname(__file__), "../config/%s.yml" % f)
        with open(yml_path,'r') as stream:
            return yaml.safe_load(stream)
