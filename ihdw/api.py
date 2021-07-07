#from ihf import Ihf
import hug
from hug.types import *
from ihdb import Ihdb
from hashlib import sha512
from uuid import uuid4
import time
import os
#from ihdw.builder import Builder
import jwt
from hug.middleware import CORSMiddleware
import secrets
from datetime import datetime

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

def getPage(category):
    page = [p for p in global_config['pages'] if p['category'] == category]
    if len(page) > 0:
        return page[0]
    return None

@hug.get(requires=token_key_authentication)
def getPageConfig(category):
    page = getPage(category)
    if page is not None:
        return page
    return error("Can't find pages with category "+category)

@hug.post(requires=token_key_authentication)
def addOrUpdatePage(category, url, template):
    if category in getCategories():
        if len(url) == 0:
            return error('Url cannot be null')
        if len(template) == 0:
            return error ('Template cannot be null')
        page = {}
        page['category'] = category
        page['url'] = url
        page['template'] = template
        deletePage(category)
        global_config['pages'] += [page]
        global_config.save()
        return 'Saved.'
            

@hug.post(requires=token_key_authentication)
def deletePage(category):
    page = getPage(category)
    if page is not None:
        global_config['pages'].remove(page)
        global_config.save()
    return "Ok."


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

@hug.post(requires=token_key_authentication)    
def searchContent(category, condition):
    condition = None if len(condition) == 0 else condition
    nodes = db.nodes(category, where=condition)
    search_result = []
    for n in nodes:
        d = {}
        d['id'] = n.id
        d['category'] = n.category
        d['preview_name'] = n['title'] or n['name'] if (n['title'] or n['name']) != [] else n.id
        d['preview_name'] = d['preview_name']['content'] if 'content' in d['preview_name'] else d['preview_name']
        d['preview_data'] = {i: n.data[i]['content'] for i in n.data.keys()}
        d['preview_data'].pop('title', None)
        d['preview_data'].pop('name', None)
        d['preview_data'] = str(d['preview_data']).strip()[0:50]
        search_result += [d]
    return search_result

@hug.post(requires=token_key_authentication) 
def delete_content(id, category):
    db.delete(db.node(id, category))
    return 'Ok.'

@hug.post(requires=token_key_authentication) 
def add_content(category):
    n = db.create_node(category)
    if category in getCategories():
        f = db.nodes(category)[0]
        n.data = f.data.copy()
        for key in n.data.keys():
            n.data[key]['content'] = ''
            n.relations = f.relations.copy()
        n['name'] = {'type': 'text', 'content': 'New Content'}
        n['date'] = {'type': 'date', 'content': datetime.today().strftime('%Y-%m-%d')}
    n.save()
    return n.id

@hug.get(requires=token_key_authentication)    
def getContent(id, category):
    n = db.node(id, category)
    return n.data


@hug.get(requires=token_key_authentication)    
def getRelations(id, category):
    n = db.node(id, category)
    result = {}
    for r in n.relations.keys():
        result[r] = [n.relations[r][0].split(':')[0], n.relations[r][0].split(':')[1]]
    return result

@hug.post(requires=token_key_authentication)
def add_data(id, category, name, type, value):
    n = db.node(id, category)
    n[name] = {'type': type, 'content': value}
    return 'OK.'

@hug.post(requires=token_key_authentication)
def add_relation(id, category, name, rel_category):
    rel = db.nodes(rel_category)[0]
    n = db.node(id, category)
    n[name] = rel
    return 'OK.'

@hug.post(requires=token_key_authentication)
def update_relation(id, category, name, rel_category, rel_id):
    rel = db.node(rel_id, rel_category)
    if rel is not None:
        n = db.node(id, category)
        n[name] = rel
    return 'OK.'

@hug.post(requires=token_key_authentication)
def delete_relation(id, category, name):
    n = db.node(id, category)
    n.delete_relation(name)
    n.save()
    return 'OK.'

@hug.post(requires=token_key_authentication)
def delete_data(id, category, name):
    if name not in ['name', 'date']:
        n = db.node(id, category)
        n.data.pop(name)
        n.save()
        return 'OK.'
    return error("Can't delete "+name)
    
def update_data(self, data):
    self.selected_node.data = data
    self.selected_node.save()
    self.info = "Saved."


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
    a = db.create_node('Author', {'name': {'type': 'text', 'content': 'TotoPouet'}, 'date': {'type': 'date', 'content': '2020-10-19'}, 'description': {'type': 'text', 'content': 'Is a stupid writer.'}})
    b = db.create_node('Author', {'name': {'type': 'text', 'content': 'anotherauthor'}, 'date': {'type': 'date', 'content': '2020-10-19'}, 'description': {'type': 'text', 'content': 'Is a anoymous.'}})
    p = db.create_node('Post', {'name': {'type': 'text', 'content': 'Test'}, 'date': {'type': 'date', 'content': '2020-10-19'}, 'content':{'type': 'markdown', 'content': 'Test **lol**'}})
    p['author'] = b