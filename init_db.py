import sys
import os

try: 
    entrance_port = int(sys.argv[1])
    private_port = int(sys.argv[2])
except IndexError:
    print("Usage: python init_db.py [ listening port ] [ configuration port ]")
    exit()
except ValueError:
    print("Error: invalid port")
    exit()



from router_models import db, Node, Frontend, Edge

db.connect()
try:
    db.drop_tables([Node, Edge, Frontend])
except: 
    pass
db.create_tables([Node, Edge, Frontend])


Node.create(name="root", address="localhost", routing_port=entrance_port, config_port=private_port)

db.close()
