from ihf import Ihf
from ihdb import Ihdb
from hashlib import sha512
from uuid import uuid4
import time
import os

def create_global_config():
    g = db.create_node('Global_Config')
    g.id = 'Global_Config'
    g.save()
    g['__key__'] = uuid4().hex
    g['website_name'] = 'Your WebSite'
    g['website_url'] = 'https://your-website.com'
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
    
    def update_profile(self, name, password=''):
        if len(name) > 0:
            self.account['name'] = name
            if len(password) > 0:
                self.account['__password__'] = hash_password(password)
            self.info = 'Account updated.'
        else:
            self.error = 'Name cannot be null.'
    
    def update_config(self, name, url):
        self.config['website_name'] = name
        self.config['website_url'] = url
        self.info = 'Config updated.'

db = Ihdb('db')
global_config = db.node('Global_Config', 'Global_Config')
if global_config is None:
    global_config = create_global_config()
    register_superadmin()

def serve(host='localhost', port=1910):
    Ihf(Admin, os.path.dirname(os.path.realpath(__file__))+'/index.html', host=host, port=port).serve()

if __name__ == "__main__":
    serve()