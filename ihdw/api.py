#from ihf import Ihf
import hug
from hug.types import *
from ihdb import Ihdb
from hashlib import sha512
from uuid import uuid4
import time
import os
from ihdw.builder import Builder
import jwt
from hug.middleware import CORSMiddleware
import secrets

api = hug.API(__name__)
api.http.add_middleware(CORSMiddleware(api))

def error(message):
    return {'error': message}

with open("apiKey","a+") as f:
    f.seek(0)
    if (len(f.read())) == 0:
        f.write(secrets.token_urlsafe())
        f.seek(0)
    secret_key = f.read()

def create_global_config():
    g = db.create_node('Global_Config')
    g.id = 'Global_Config'
    g.save()
    g['__key__'] = uuid4().hex
    g['website_name'] = 'Your WebSite'
    g['website_url'] = 'https://your-website.com'
    g['pages'] = [{'category': 'Post', 'url': 'post/{{title.lower()}}', 'template':''}]
    g['deployment_script'] = ''
    return g

def hash_password(password):
    return sha512((password+global_config['__key__']).encode()).hexdigest()

def token_verify(token):
    global secret_key
    try:
        return jwt.decode(token, secret_key, algorithm="HS256")
    except jwt.DecodeError:
        return False

token_key_authentication = hug.authentication.token(token_verify)


@hug.get("/token_authenticated", requires=token_key_authentication)  # noqa
def token_auth_call(user: hug.directives.user):
    return user

@hug.post(requires=token_key_authentication)
def register_superadmin():
    account = db.create_node('Account')
    account['name'] = 'root'
    account['__password__'] = hash_password('root')
    account['isSuperAdmin'] = True

def getAccountById(id):
    return db.node(id, 'Account')

@hug.post()
def login(name, password):
    time.sleep(3) #Simple protection against brute-force attack
    password_hash = hash_password(password)
    try:
        account = [a for a in db.nodes('Account') if a['name'] == name and a['__password__'] == password_hash][0]
        return {
            "token": jwt.encode({"id": account.id, "isSuperAdmin": account["isSuperAdmin"]}, secret_key, algorithm="HS256")
        }
    except Exception as e:
        return error("Incorrect name or password")

@hug.post(requires=token_key_authentication)
def register(name, password):
    account = db.create_node('Account')
    account['name'] = name
    account['__password__'] = hash_password(password)
    account['isSuperAdmin'] = False
    return f'{name} added successfully'

@hug.get()    
def build():
    try:
        self.builder.generate_website()
        self.info = "Successfully built"
    except Exception as e:
        self.error = str(e)

@hug.get(requires=token_key_authentication)
def getProfileInformations(user: hug.directives.user):
    account = getAccountById(user['id'])
    return {'name': account['name'], 'isSuperAdmin': account['isSuperAdmin']}

@hug.post(requires=token_key_authentication)    
def updateProfile(name, password, user: hug.directives.user):
    account = getAccountById(user['id'])
    if len(name) > 0:
        account['name'] = name
        if len(password) > 0:
            account['__password__'] = hash_password(password)
        return 'Account updated.'
    else:
        return error('Name cannot be null.')
    
@hug.get(requires=token_key_authentication)
def getPages():
    return global_config['pages']

@hug.get(requires=token_key_authentication)
def getCategories():
    cat = db.get_all_categories()
    cat.remove('Global_Config')
    cat.remove('Account')
    return cat

@hug.get(requires=token_key_authentication)
def getAvailableCategories():
    cat = db.get_all_categories()
    cat.remove('Global_Config')
    cat.remove('Account')
    for page in global_config['pages']:
        if page['category'] in cat:
            cat.remove(page['category'])
        else:
            global_config['pages'].remove(page)
    return cat

@hug.get(requires=token_key_authentication)
def getUsedCategories():
    return [page['category'] for page in global_config['pages']]

def delete_page(self):
    self.config['pages'].remove(self.selected_page)
    self.config.save()
    self.selected_page = None


def add_new_page(self):
    self.config['pages'] += [{'category': '', 'url': 'post/{url}', 'template':''}]
    self.config.save()

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

@hug.get(requires=token_key_authentication)
def getConfig():
    return {'name': global_config['website_name'], 'url': global_config['website_url']}

@hug.post(requires=token_key_authentication)
def updateConfig(name, url):
    if len(name) > 0:
        global_config['website_name'] = name
    if len(url) > 0:
        global_config['website_url'] = url
    return 'Config updated.'
    
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


def generate_function(url, method='GET', parameters=(), requires=()):
    name = url[1:].replace('/', '_').replace('.', '_')
    headers = ", headers: { 'Content-Type': 'application/json' }, "
    if len(requires) > 0 and requires[0].startswith('Token'):
        headers = ", headers: { 'Content-Type': 'application/json', 'Authorization': this.token}, "
    if method == 'GET':
        url += '?'
        for p in parameters:
            url += f"{p}='+{p}+'&"
        url = url[:-1]
        body = ''
    else:
        body = "body: '{"
        for p in parameters:
            body += f"\"{p}\":\"'+{p}+'\","
        body = body[:-1]+"}'"
    parameters = str(parameters).replace("'", '').replace(",)", ")")
    save_token = "this.token = (await p)['token']; window.localStorage.setItem('token', this.token);" if name == "login" else ""
    result = """
    Api.prototype."""+name+""" = async function"""+parameters+""" {
        p = new Promise((resolve, reject) => {
            fetch(this.api_url+'"""+url+"""', {method: '"""+method+"""'"""+headers+body+"""}).then(async x => {let j = await x.json(); if (!x.ok || (typeof j === "object" && "error" in j)) {reject("error" in j ? j['error'] : j)} else {resolve(j)} }).catch(err => reject(err))
        });
        """+save_token+"""
        return await p;

    }
    """
    return result


@hug.get('/api.js', output=hug.output_format.html)
def js(request, response):
    response.content_type = "application/javascript"
    result = """
class Api {
    constructor() {
        this.api_url = 'http://"""+request.host+":"+str(request.port)+"""';
        this.token = window.localStorage.getItem('token');
    }
    disconnect() {
        window.localStorage.removeItem('token')
        this.token = null;
    }
    }

    """
    doc = hug.API(__name__).http.documentation()
    for url in list(doc['handlers']):
        for method in list(doc['handlers'][url]):
            parameters = tuple(doc['handlers'][url][method]['inputs']) if 'inputs' in doc['handlers'][url][method].keys() else ()
            requires = tuple(doc['handlers'][url][method]['requires']) if 'requires' in doc['handlers'][url][method].keys() else ()
            result += generate_function(url, method, parameters, requires)
    result += "window.api = new Api()"
    return result

@hug.get('/debug', output=hug.output_format.html)
def debug(response):
    return '<script src="/api.js"></script>'



db = Ihdb('db')
global_config = db.node('Global_Config', 'Global_Config')
if global_config is None:
    global_config = create_global_config()
    register_superadmin()
    a = db.create_node('Author', {'name': 'Toto', 'description': 'Is a studpi writer'})
    p = db.create_node('Post', {'title': 'Test', 'content':'test'})
    p['author'] = a