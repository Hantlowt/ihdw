from ihf import Ihf
from ihdb import Ihdb
from hashlib import sha512
from uuid import uuid4
import time

db = Ihdb('db')
global_config = db.node('Global_Config', 'Global_Config')
if global_config is None:
    global_config = create_global_config()
    register_superadmin()

def create_global_config():
    g = db.create_node('Global_Config')
    g.id = 'Global_Config'
    g.save()
    g['key'] = uuid4().hex
    g['website_name'] = 'Your WebSite'
    return g

def hash_password(password):
    return sha512((password+g['key']).encode()).hexdigest()

def register_superadmin():
    account = db.create_node('Account')
    accont['name'] = 'root'
    account['password'] = hash_password('root')
    account['isSuperAdmin'] = True

class Admin:
    def __init__(self, client):
        self.account_id = client.session.get_data('account_id', None)
        self.account = db.node(self.account_id, 'Account') if self.account_id is not None else None
        self.error = ''
        self.website_name = g['website_name']

    def login(name, password):
        time.sleep(3) #Simple protection against brute-force attack
        password_hash = hash_password(password)
        try:
            self.account = [a for a in db.nodes('Account') if a['name'] = name and a['password'] == password_hash][0]
        except Exception:
            print("Incorrect name or password")
    
    def register(name, password):
        account = db.create_node('Account')
        account['name'] = name
        account['password'] = hash_password(password)
        account['isSuperAdmin'] = False


def serve(host='localhost', port=1910):
    Ihf(Todo, 'admin.html', host=host, port=port).serve()