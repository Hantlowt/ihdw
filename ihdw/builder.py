import os
from singleton_decorator import singleton
from jinja2 import Template
import shutil

@singleton
class Builder:
    def __init__(self, db, global_config):
        self.db = db
        self.global_config = global_config
        self.load_templates()
        if not os.path.exists('templates'):
            shutil.copytree(os.path.dirname(os.path.realpath(__file__))+'/templates', 'templates')
    def load_templates(self):
        self.templates = [os.path.join(dp, f) for dp, dn, fn in os.walk(os.path.expanduser("templates")) for f in fn]
    def generate_file(self, page, config):
        url = Template(config['url']).render(**page.data)
        with open(config['template']) as f:
            template = Template(f.read())
        relations = {r: page[r][0].data for r in page.relations.keys()}
        generated = template.render(db=self.db, global_config=self.global_config, **page.data, **relations)
        filename = 'www/result/'+ url + '/index.html'
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, "w") as f:
            f.write(generated)
    def generate_website(self):
        if os.path.exists('www/result'):
            shutil.rmtree('www/result', ignore_errors=True)
        os.mkdir('www/result')
        if os.path.exists('templates/static'):
            shutil.copytree(os.path.dirname('templates/static', 'www/result/static'))
        for config in self.global_config['pages']:
            for page in self.db.nodes(config['category']):
                self.generate_file(page, config)