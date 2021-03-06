from router_models import Node, Frontend, Edge, db
from router_utils import load_nodes_view, check_json_template, find_by_id, check_for_cycles

import json
from hashids import Hashids
hashids = Hashids(min_length=8)

from flask import request, render_template, url_for, Flask
app = Flask(__name__)

import peewee


@app.before_request
def _db_connect():
    db.connect()

@app.teardown_request
def _db_close(exc):
    if not db.is_closed():
        db.close()

@app.route('/')
def main_page():

    nodes = load_nodes_view(routes=False)
    frontends = Frontend.select()

    return render_template('index.html', 
        nodes=nodes, frontends=frontends,
        css_url=url_for('static', filename='style.css'),
        js_url=url_for('static', filename='main.js'))

@app.route('/api/node/create', methods=['POST'])
def create_node():

    if not check_json_template(request.json, ['name',
        'address', 'routing_port', 'config_port']):
        return 'Error: not enough arguments', 400

    try:
        node = Node.create(**request.json)
    except:
        return 'Error: wrong arguments', 400

    Frontend.create(name=node.name+' ping', routing_path="/ping_{0}".format(node.id), 
        backend_port=node.routing_port, node_id=node.id, is_private=True, check_ping=False)
    Frontend.create(name=node.name+' config', routing_path="/config_{0}".format(node.id),
        backend_port=node.config_port, node_id=node.id, is_private=True, check_ping=False)

    return json.dumps({'id': node.id}), 200

    
@app.route('/api/node/delete', methods=['DELETE'])
def delete_node():
    if not check_json_template(request.json, ['id',]):
        return 'Error: not enough arguments', 400
    
    try:
        node = Node.get_by_id(request.json['id'])
    except peewee.DoesNotExist:
        return 'Error: node does not exist', 404

    nodes_view = load_nodes_view()
    node_view = find_by_id(nodes_view, node.id)

    for parent in node_view.parents:
        parent.children.remove(node_view)
        parent.update_upwards()

    node.delete_instance()

    return 'OK', 200

@app.route('/api/node/update', methods=['POST'])
def update_node():
    if not check_json_template(request.json, ['id', 'name',
        'address', 'routing_port', 'config_port']):
        return 'Error: not enough arguments', 400

    try:
        node = Node.get_by_id(request.json['id'])
    except peewee.DoesNotExist:
        return 'Error: node does not exist', 404

    try:
        node.name = request.json['name']
        node.address = request.json['address']
        node.routing_port = request.json['routing_port']
        node.config_port = request.json['config_port']

        node.save()
    except:
        return 'Error: wrong arguments', 400

    nodes_view = load_nodes_view()
    node_view = find_by_id(nodes_view, request.json['id'])
    node_view.update_upwards()

    return 'OK', 200

@app.route('/api/node/update_config', methods=['POST'])
def update_node_config():
    if not check_json_template(request.json, ['id',]):
        return 'Error: not enough arguments', 400

    nodes_view = load_nodes_view()
    node_view = find_by_id(nodes_view, request.json['id'])

    if not node_view:
        return 'Error: node does not exist', 404

    ret = node_view.send_config()
    if ret==200:
        return 'OK', 200
    else:
        return 'Config deploy failed', ret

@app.route('/api/edge/create', methods=['POST', 'DELETE'])
def create_edge():

    if not check_json_template(request.json, ['from_node', 'to_node']):
        return 'Error: not enough arguments', 400
    nodes_view = load_nodes_view()
    from_node_view = find_by_id(nodes_view, request.json['from_node'])
    to_node_view = find_by_id(nodes_view, request.json['to_node'])

    if not check_for_cycles([from_node_view, to_node_view]):
        return 'Error: edge will create cycle', 400

    try:
        Edge.create(**request.json)
    except:
        return 'Error: wrong arguments', 400

    from_node_view.add_child(to_node_view)
    
    from_node_view.update_upwards()
    return 'OK', 200
    

@app.route('/api/edge/delete', methods=['DELETE'])
def delete_edge():
    if not check_json_template(request.json, ['from_node', 'to_node']):
        return 'Error: not enough arguments', 400

    try:
        edge = Edge.get(**request.json)
    except peewee.DoesNotExist:
        return 'Error: edge does not exist', 404

    nodes_view = load_nodes_view()
    edge.delete_instance()

    from_node_view = find_by_id(nodes_view, request.json['from_node'])
    to_node_view = find_by_id(nodes_view, request.json['to_node'])
    from_node_view.remove_child(to_node_view)
    from_node_view.update_upwards()
    return 'OK', 200


@app.route('/api/frontend/create', methods=['POST', 'DELETE'])
def create_frontend():

    if not check_json_template(request.json, ['name', 
        'backend_port', 'node_id', 'is_private',
        'check_ping']):

        return 'Error: not enough arguments', 400

    if request.json['node_id'] == 1:
        return 'Error: frontend cannot be created on root node', 400

    routing_path = '/' + hashids.encode(request.json['backend_port'] * 10 + request.json['node_id'])

    try:
        frontend = Frontend.create(routing_path=routing_path,**request.json)
    except:
        return 'Error: wrong arguments', 400
    
    nodes_view = load_nodes_view()

    host_node_view = find_by_id(nodes_view, request.json["node_id"])
    host_node_view.update_parents_routes()
    
    return json.dumps({'id': frontend.id}), 200


@app.route('/api/frontend/delete', methods=['DELETE'])
def delete_frontend():
    if not check_json_template(request.json, ['id',]):
        return 'Error: not enough arguments', 400


    try:
        frontend = Frontend.get_by_id(request.json['id'])
    except peewee.DoesNotExist:
        return 'Error: frontend does not exist', 404

    frontend.delete_instance()

    nodes_view = load_nodes_view()
    host_node_view = find_by_id(nodes_view, frontend.node_id)
    host_node_view.update_parents_routes()
    return 'OK', 200    


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8082, debug=True)



