from ihf import Ihf
from ihdb import Ihdb
from hashlib import sha512
from uuid import uuid4
import time
import os
from builder import Builder

def create_global_config():
    g = db.create_node('Global_Config')
    g.id = 'Global_Config'
    g.save()
    g['__key__'] = uuid4().hex
    g['website_name'] = 'Your WebSite'
    g['website_url'] = 'https://your-website.com'
    g['pages'] = [{'category': 'Post', 'url': 'post/{{url.lower()}}', 'template':''}]
    g['deployment_script'] = ''
    return g

def hash_password(password):
    return sha512((password+global_config['__key__']).encode()).hexdigest()

def register_superadmin():
    account = db.create_node('Account')
    account['name'] = 'root'
    account['__password__'] = hash_password('root')
    account['isSuperAdmin'] = True

class Admin:
    def __init__(self, client):
        self.__session__ = client.session
        account_id = self.__session__.get_data('account_id', None)
        self.account = db.node(account_id, 'Account') if account_id is not None else None
        self.error = ''
        self.info = ''
        self.config = global_config
        self.builder = Builder(db, self.config)
        self.selected_page = None
        self.selected_node = None
        self.search_result = []
        self.gen_all_categories()

    def login(self, name, password):
        time.sleep(3) #Simple protection against brute-force attack
        password_hash = hash_password(password)
        try:
            self.account = [a for a in db.nodes('Account') if a['name'] == name and a['__password__'] == password_hash][0]
            self.__session__.data['account_id'] = self.account.id
            self.error = ''
            self.info = ''
        except Exception:
            self.error = "Incorrect name or password"
    
    def logout(self):
        self.account = None
        self.__session__.data['account_id'] = None
    
    def register(self, name, password):
        account = db.create_node('Account')
        account['name'] = name
        account['__password__'] = hash_password(password)
        account['isSuperAdmin'] = False
        self.info = f'{name} added successfully'
    
    def build(self):
        try:
            self.builder.generate_website()
            self.info = "Successfully built"
        except Exception as e:
            self.error = str(e)
    
    def update_profile(self, name, password=''):
        if len(name) > 0:
            self.account['name'] = name
            if len(password) > 0:
                self.account['__password__'] = hash_password(password)
            self.info = 'Account updated.'
        else:
            self.error = 'Name cannot be null.'
    
    def delete_page(self):
        self.config['pages'].remove(self.selected_page)
        self.selected_page = None

    def add_new_page(self):
        self.config['pages'] += [{'category': '', 'url': 'post/{url}', 'template':''}]

    def select_page(self, index):
        self.builder.load_templates()
        self.gen_all_categories()
        self.selected_page = self.config['pages'][int(index)]
    
    def update_page(self, category, url, template):
        if category in db.get_all_categories():
            self.selected_page['category'] = category
        if len(url) > 0:
            self.selected_page['url'] = url
        if template in self.builder.templates:
            self.selected_page['template'] = template
        self.config.save()
    
    def gen_all_categories(self):
        self.all_categories = db.get_all_categories()
        self.all_categories.remove('Global_Config')
        self.all_categories.remove('Account')
    
    def update_config(self, name, url):
        self.config['website_name'] = name
        self.config['website_url'] = url
        self.info = 'Config updated.'
    
    def search(self, category, condition):
        condition = None if len(condition) == 0 else condition
        nodes = db.nodes(category, where=condition)
        self.search_result = []
        for n in nodes:
            d = {}
            d['id'] = n.id
            d['category'] = n.category
            d['preview_name'] = f"{n['title'] or n['name']}" if (n['title'] or n['name']) != [] else n.id
            d['preview_data'] = n.data.copy()
            d['preview_data'].pop('title', None)
            d['preview_data'].pop('name', None)
            d['preview_data'] = str(d['preview_data']).strip()[0:50]
            self.search_result += [d]
    
    def select_node(self, id, category):
        self.selected_node = db.node(id, category)
    
    def add_node(self, category):
        self.selected_node = db.create_node(category)
        if category in self.all_categories:
            self.selected_node.data = {k: '' for k in db.nodes(category)[0].data.keys()}
        self.selected_node.save()
    
    def delete_node(self):
        db.delete(self.selected_node)
        self.selected_node = None
    
    def update_data(self, data):
        self.selected_node.data = data
        self.selected_node.save()
        self.info = "Saved."
    
    def add_data(self, name, value):
        self.selected_node[name] = value
    
    def delete_data(self, name):
        self.selected_node.data.pop(name)
        self.selected_node.save()
    
    def add_relation(self, name, rel):
        category, id = rel.split(':')
        node = db.node(id, category)
        if node != None:
            self.selected_node[name] = node
        else:
            self.error = "No node found with this id"
    
    def delete_relation(self, name):
        self.selected_node.delete_relation(name)
        self.selected_node.save()

db = Ihdb('db')
global_config = db.node('Global_Config', 'Global_Config')
if global_config is None:
    global_config = create_global_config()
    register_superadmin()
    a = db.create_node('Author', {'name': 'Toto', 'description': 'Is a studpi writer'})
    p = db.create_node('Post', {'title': 'Test', 'content':'test'})
    p['author'] = a

def serve(host='localhost', port=1910):
    Ihf(Admin, os.path.dirname(os.path.realpath(__file__))+'/index.html', host=host, port=port, loading_indicator=True).serve()

if __name__ == "__main__":
    serve()