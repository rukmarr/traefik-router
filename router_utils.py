from router_models import Node, Frontend, Edge, prefetch
import tomlkit
import json
import requests

root_config_port = 8080
root_address = ''

def find_in_seq(seq, predicate, default=None):
    return next(filter(predicate, seq), default)

def find_by_id(seq, id, default=None):
    return find_in_seq(seq, lambda e: e.id == id, default)

def check_json_template(dict, keys):
    if dict is None or len(keys) != len(dict.keys()): 
        return False

    for key in keys:
        if key not in dict:
            return False

    return True

class NodeView():

    def __init__(self, id, name, address, endpoints, routing_port, 
        config_port, parents=None, children=None):
        
        self.id = id
        self.name = name
        self.address = address

        self.parents = parents or []
        self.children = children or []

        self.endpoints = endpoints
        self.routing_port = routing_port
        self.config_port = config_port

        self.routes = {}

    def __str__(self):

        parents_str = ' '.join([str(node.id) for node in self.parents])
        children_str = ' '.join([str(node.id) for node in self.children])

        routes_str = '\n\t'.join([p + ' ==> ' + ' or '.join([t+r['path'] for t in r['servers']]) for p, r
            in self.routes.items()])
        endpoints_str = '\n\t'.join(['{0}:{1}{2} ({2})'.format(self.address, e.backend_port, e.routing_path) 
            for e in self.endpoints])

        return 'NODE #{0} {1}\n\tPARENTS: {2}\n\tCHILDREN: {3}\n\tROUTES:\n\t{4}\n\tENDPOINTS:\n\t{5}'.format(self.id, 
            self.name, parents_str, children_str, routes_str, endpoints_str)

    def add_child(self, node):
        self.children.append(node)
        if self not in node.parents:
            node.add_parent(self)

    def remove_child(self, node):
        self.children.remove(node)
        if self in node.parents:
            node.remove_parent(self)

    def add_parent(self, node):
        self.parents.append(node)
        if self not in node.children:
            node.add_child(self)

    def remove_parent(self, node):
        self.parents.remove(node)
        if self in node.children:
            node.remove_child(self)

    def recompute_routes(self):

        self.routes = {}
        for node in self.children:

            for endpoint in node.endpoints:
 
                url = "http://{0}:{1}".format(node.address, 
                    endpoint.backend_port)
                
                self.routes[endpoint.routing_path] = {
                    'servers': [url,],
                    'node_id': node.id,
                    'is_private': endpoint.is_private,
                    'health_check': endpoint.check_ping,
                    'transit': False
                }

            for path, route in node.routes.items():

                if path in self.routes:
                    continue

                url = "http://{0}:{1}".format(node.address, 
                    node.routing_port)
                health_check = route['health_check'] and "/ping_{0}/ping".format(route['node_id'])

                if path in self.routes:
                    self.routes[path]['servers'].push[url]
                else:
                    self.routes[path] = {
                        'servers': [url,],
                        'node_id': node.id,
                        'is_private': route['is_private'],
                        'health_check': health_check,
                        'transit': True
                    }

    def update_parents_routes(self):
        queue = self.parents[:]
        for node in queue:

            node.recompute_routes()
            for parent in node.parents:
                # check if current node is the last child in the queue
                if all(map(lambda n: n not in queue or queue.index(n) <= queue.index(node), 
                    parent.children)):
                    queue.append(parent)
            node.send_config()

    def update_upwards(self):
        self.recompute_routes()
        self.send_config()        
        self.update_parents_routes()

    def send_config(self):
        backends = {}
        frontends = {}

        if self.id == 1:
            return self.send_root_config()

        for i, (routing_path, route) in enumerate(self.routes.items()):

            backend = {
                'loadBalancer': {'method': 'wrr'}
            }
            
            if route['health_check'] and route['transit']:
                backend['health_check'] = {
                    'path': route['health_check'],
                    'interval': "10s"
                }
            backend['servers'] = {}
            for j, server in enumerate(route['servers']):
                backend['servers']['server{0}'.format(j)] = {
                    'url': server,
                    'weight': 1
                }

            backends['backend{0}'.format(i)] = backend

            frontend =  {
                'entryPoints': ['http'],
                'backend': 'backend{0}'.format(i),
                'priority': 20,
            }

            if route['transit']:
                frontend['routes'] = {'match': {'rule': 'PathPrefix:' + routing_path}}
            else:
                frontend['routes'] = {'match': {'rule': 'PathPrefixStrip:' + routing_path}}

            # no redirect due to websockets quirks
            if not route['is_private']:
                cookie_frontend = {
                    'entryPoints': ['http'],
                    'backend': 'backend{0}'.format(i),
                    'priority': 10,
                    'routes' : {'match': {'rule': 'HeadersRegexp: Cookie, routing='+routing_path}},
                }
                frontends['cookie{0}'.format(i)] = cookie_frontend

            frontends['frontend{0}'.format(i)] = frontend

        toml_str = tomlkit.dumps({'backends': backends, 'frontends': frontends})

        config_url = 'http://localhost:{0}/config_{1}/config'.format(root_config_port, self.id)
        try:
            r = requests.put(config_url, data=toml_str)
        except:
            return 500

        return r.status_code

    def send_root_config(self):
        backends = {}
        frontends = {}

        for i, (routing_path, route) in enumerate(self.routes.items()):

            backend = {
                'loadBalancer': {'method': 'wrr'}
            }

            if route['health_check'] and route['transit'] == str:
                backend['health_check'] = {
                    'path': route['health_check'],
                    'interval': "10s"
                }
            backend['servers'] = {}
            for j, server in enumerate(route['servers']):
                backend['servers']['server{0}'.format(j)] = {
                    'url': server,
                    'weight': 1
                }

            backends['backend{0}'.format(i)] = backend

            main_frontend =  {
                'backend': 'backend{0}'.format(i),
                'priority': 20,
            }

            if route['transit']:
                main_frontend['routes'] = {'match': {'rule': 'PathPrefix:' + routing_path}}
            else:
                main_frontend['routes'] = {'match': {'rule': 'PathPrefixStrip:' + routing_path}}

            if not route['is_private']:
                main_frontend['entryPoints']  =  ['http',]
                main_frontend['headers'] = {'customresponseheaders': {
                    'Set-Cookie': 'routing={0}; domain={1}; path=/'.format(routing_path, root_address)
                }}

                # no redirect due to websockets quirks
                cookie_frontend = {
                    'entryPoints': ['http',],
                    'backend': 'backend{0}'.format(i),
                    'priority': 10,
                    'routes' : {'match': {'rule': 'HeadersRegexp: Cookie, routing='+routing_path}}
                }

                # redirect - undocumented feature, works just like entrypoint's, with url-rewrite
                # regex from https://tools.ietf.org/html/rfc3986#appendix-B
                redirect_frontend = {
                    'entryPoints':  ['http',],
                    'backend': 'backend{0}'.format(i),
                    'priority': 15,
                    'routes' : {'match': {'rule': 'HeadersRegexp: Referer, ' + routing_path}},
                    'redirect': {  
                        'regex': "^(([^:/?#]+):)?(//([^/?#]*))?([^?#]*)(\\?([^#]*))?(#(.*))?",
                        'replacement': "$1$3" + routing_path + "$5$6"
                    }
                }

                frontends['redirect{0}'.format(i)] = redirect_frontend
                frontends['cookie{0}'.format(i)] = cookie_frontend

            else:
                main_frontend['entryPoints']  =  ['private',]

            frontends['frontend{0}'.format(i)] = main_frontend

        toml_str = tomlkit.dumps({'backends': backends, 'frontends': frontends})

        try:
            toml_file = open('routes.toml', 'w')
            toml_file.write(toml_str)

            return 200
        except:
            return 500



def load_nodes_view(routes=True):

    edges_data = Edge.select()
    nodes_data = Node.select()
    frontends_data = Frontend.select()

    # perform two queries and connect frontends to responded nodes
    nodes_data = prefetch(nodes_data, frontends_data)

    nodes = [NodeView(node.id, node.name, node.address, 
        node.frontends, node.routing_port, node.config_port) for node in nodes_data]

    for edge in edges_data:
        from_node = find_by_id(nodes, edge.from_node_id)
        to_node = find_by_id(nodes, edge.to_node_id)

        from_node.add_child(to_node)

    if routes:
        queue = list(filter(lambda n: len(n.children) == 0, nodes))
        for node in queue:
            node.recompute_routes()

            if node.id == 1:
                global root_config_port
                global root_address
                root_config_port = node.config_port
                root_address = node.address

            for parent in node.parents:
                # check if current node is the last child in the queue
                if all(map(lambda n: n not in queue or queue.index(n) <= queue.index(node), 
                    parent.children)):
                    queue.append(parent)

    return nodes


def check_for_cycles(new_edge):

    from_node = new_edge[0]
    to_node = new_edge[1]

    queue = [to_node, ]
    for node in queue:
        if node == from_node:
            return False

        for child in node.children:
            if child not in queue:
                queue.append(child)

    return True


