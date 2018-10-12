from peewee import *

db = SqliteDatabase('/etc/traefik/router.sqlite', pragmas={'foreign_keys': 1})

class BaseModel(Model):
    class Meta:
        database = db

class Node(BaseModel):
    name = TextField()
    address = TextField()
    routing_port = IntegerField()
    config_port = IntegerField()

class Frontend(BaseModel):
    routing_path = TextField()
    backend_port = IntegerField()
    backend_path = TextField()
    is_private = BooleanField(default=False)
    check_ping = BooleanField(default=True)
    node = ForeignKeyField(Node, backref='frontends', on_delete='CASCADE')


class Edge(BaseModel):
    from_node = ForeignKeyField(Node, backref='inbound_edges', on_delete='CASCADE')
    to_node = ForeignKeyField(Node, backref='outbound_edges', on_delete='CASCADE')

    class Meta():
        indexes = (
            # Specify a unique multi-column index on from/to-user.
            (('from_node_id', 'to_node_id'), True),
        )

if __name__ == "__main__":

    db.connect()
    db.create_tables([Node, Edge, Frontend])

    Node.create(name="ROOT", address="localhost", routing_port="8080", config_port="8081") #1
    Node.create(name="load_balancer_1", address="localhost", routing_port="8085", config_port="8086") 
    Node.create(name="load_balancer_2", address="localhost", routing_port="8090", config_port="8091") 
    Node.create(name="hosting_1", address="localhost", routing_port="8095", config_port="8096") 
    Node.create(name="hosting_1", address="localhost", routing_port="8100", config_port="8101") 
    Node.create(name="hosting_1", address="localhost", routing_port="8105", config_port="8106")

    Edge.create(from_node=1, to_node=2)
    Edge.create(from_node=1, to_node=3)
    Edge.create(from_node=2, to_node=4)
    Edge.create(from_node=2, to_node=5)
    Edge.create(from_node=3, to_node=5)
    Edge.create(from_node=3, to_node=6)

    Frontend.create(routing_path="/api1", backend_port="8097", backend_path="/", node=4)
    Frontend.create(routing_path="/api2", backend_port="8102", backend_path="/", node=5)
    Frontend.create(routing_path="/api3", backend_port="8107", backend_path="/test", node=6)

    Frontend.create(routing_path="/lbadmin", backend_port="8092", backend_path="/", node=2)


    '''
    Node.create(name="ROOT", address="apmath.spbu.ru", routing_port="8080") #1
    Node.create(name="load_balancer_1", address="load1.apmath.spbu.ru", routing_port="8080")
    Node.create(name="load_balancer_2", address="load2.apmath.spbu.ru", routing_port="8080")
    Node.create(name="hosting1", address="198.1.25.4", routing_port="8080") #4
    Node.create(name="hosting2", address="198.1.25.6", routing_port="8080")
    Node.create(name="hosting3", address="198.1.25.5", routing_port="8080")
    Node.create(name="private_hosting", address="128.12.15.3", routing_port="8080") #7
    Node.create(name="express_server", address="exp.spbu.ru", routing_port="8080")
    Node.create(name="test_server", address="198.1.25.78", routing_port="8080")
    

    Edge.create(from_node=1, to_node=2)
    Edge.create(from_node=1, to_node=3)
    Edge.create(from_node=1, to_node=8)

    Edge.create(from_node=2, to_node=4)
    Edge.create(from_node=2, to_node=5)

    Edge.create(from_node=3, to_node=5)
    Edge.create(from_node=3, to_node=6)
    Edge.create(from_node=3, to_node=7)

    Edge.create(from_node=6, to_node=9)

    Edge.create(from_node=8, to_node=9)


    Frontend.create(routing_path="/express/path_1", backend_port="80", backend_path="", node_id=8)
    Frontend.create(routing_path="/express/api", backend_port="4000", backend_path="/api", node_id=8)

    Frontend.create(routing_path="/test/path_1", backend_port="80", backend_path="", node_id=9)
    Frontend.create(routing_path="/test/api", backend_port="4000", backend_path="/api", node_id=9)

    Frontend.create(routing_path="/user/igor", backend_port="9562", backend_path="", node_id=4)

    Frontend.create(routing_path="/user/anna", backend_port="9132", backend_path="", node_id=5)
    Frontend.create(routing_path="/user/bob", backend_port="9478", backend_path="", node_id=5)

    Frontend.create(routing_path="/private", backend_port="80", backend_path="", node_id=6)

    Frontend.create(routing_path="/rocks", backend_port="7088", backend_path="/admin", node_id=7)
    '''

    db.close()


