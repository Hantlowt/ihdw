import os
from singleton_decorator import singleton
from mako.template import Template
from mako.lookup import TemplateLookup
from mako import exceptions
import shutil
from markdown import markdown

@singleton
class Builder:
    def __init__(self, db, global_config):
        self.db = db
        self.global_config = global_config
    def load_templates(self):
        self.templates = [os.path.join(dp, f) for dp, dn, fn in os.walk(os.path.expanduser("templates")) for f in fn]
    def content_to_dict(self, content, rel=True):
        a = {d: content[d]['value'] for d in content.data.keys()}
        if rel:
            b = {d: self.content_to_dict(content[d][0], False) for d in content.relations.keys()}
            return {**a, **b}
        return a
    def getURL(self, content):
        page = [p for p in self.global_config['pages'] if p['category'] == content.category]
        if len(page) == 0:
            return ''
        return Template(page[0]['url']).render(**self.content_to_dict(content))
    def generate_file(self, content, page):
        url = Template(page['url']).render(**self.content_to_dict(content))
        url = url.replace(' ', '-').lower()
        with open('templates/'+page['template']) as f:
            template = Template(f.read(), lookup=TemplateLookup(directories=['templates']))
        try:
            generated = template.render(db=self.db, global_config=self.global_config, content_to_dict=self.content_to_dict ,getURL=self.getURL, markdown=markdown, current=content, **self.content_to_dict(content))
        except:
            generated = exceptions.text_error_template().render()
        filename = 'build/'+ url + '/index.html'
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, "w") as f:
            f.write(generated)
    def generate_website(self):
        self.load_templates()
        if not os.path.exists('templates'):
            shutil.copytree(os.path.dirname(os.path.realpath(__file__))+'/templates', 'templates')
        if os.path.exists('build'):
            shutil.rmtree('build', ignore_errors=True)
        os.mkdir('build')
        if os.path.exists('templates/static'):
            shutil.copytree('templates/static', 'build/static')
        for page in self.global_config['pages']:
            for content in self.db.nodes(page['category']):
                if content['enabled']['value']:
                    self.generate_file(content, page)

"""
@singleton
class Builder:
    def __init__(self, db, global_config):
        self.db = db
        self.global_config = global_config
        #self.load_templates()
        if not os.path.exists('templates'):
            shutil.copytree(os.path.dirname(os.path.realpath(__file__))+'/templates', 'templates')
    def load_templates(self):
        self.templates = [os.path.join(dp, f) for dp, dn, fn in os.walk(os.path.expanduser("templates")) for f in fn]
    def compile(self, page):
        config = [p for p in self.global_config['pages'] if p['category'] == page.category]
        if len(config) > 0:
            config = config[0]
        data =  {d: markdown(page.data[d]['content']) if page.data[d]['type'] == 'markdown' else page.data[d]['content'] for d in page.data.keys()}
        if config != []:
            data['url'] = Template(config['url']).render(**data)
        relations =  {d: compile(page[d]) for d in page.relations.keys()}
    def generate_file(self, page, config):
        data = self.data_to_content()
        with open('templates/'+config['template']) as f:
            template = Template(f.read())
        relations = {r: self.data_to_content(page[r][0].data) for r in page.relations.keys()}
        generated = template.render(db=self.db, global_config=self.global_config, **data, **relations)
        filename = 'build/'+ data['url'] + '/index.html'
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, "w") as f:
            f.write(generated)
    def prepare_data(self):
        self.data = {}
        for config in self.global_config['pages']:
            self.data[config['category']] = []
            for page in self.db.nodes(config['category']):
                self.data[config['category']] += [self.compile(page)]

    def generate_website(self):
        if os.path.exists('build'):
            shutil.rmtree('build', ignore_errors=True)
        os.mkdir('build')
        if os.path.exists('templates/static'):
            shutil.copytree('templates/static', 'build/static')
        for config in self.global_config['pages']:
            for page in self.db.nodes(config['category']):
                self.generate_file(page, config)
"""