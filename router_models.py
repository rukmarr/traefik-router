from peewee import *

db = SqliteDatabase('router.sqlite', pragmas={'foreign_keys': 1})

class BaseModel(Model):
    class Meta:
        database = db

class Node(BaseModel):
    name = TextField()
    address = TextField()
    routing_port = IntegerField()
    config_port = IntegerField()

class Frontend(BaseModel):
    name = TextField()
    routing_path = TextField()
    backend_port = IntegerField()
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
    db.close()


