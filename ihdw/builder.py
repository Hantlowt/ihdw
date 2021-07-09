import os
from singleton_decorator import singleton
from jinja2 import Template
import shutil
from markdown import markdown

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
    def data_to_content(self, data):
        return {d: markdown(data[d]['content']) if data[d]['type'] == 'markdown' else data[d]['content'] for d in data.keys()}
    def generate_file(self, page, config):
        url = Template(config['url']).render(**self.data_to_content(page.data))
        with open('templates/'+config['template']) as f:
            template = Template(f.read())
        relations = {r: self.data_to_content(page[r][0].data) for r in page.relations.keys()}
        generated = template.render(db=self.db, global_config=self.global_config, **self.data_to_content(page.data), **relations)
        filename = 'build/'+ url + '/index.html'
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, "w") as f:
            f.write(generated)
    def generate_website(self):
        if os.path.exists('build'):
            shutil.rmtree('build', ignore_errors=True)
        os.mkdir('build')
        if os.path.exists('templates/static'):
            shutil.copytree('templates/static', 'build/static')
        for config in self.global_config['pages']:
            for page in self.db.nodes(config['category']):
                self.generate_file(page, config)