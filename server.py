"""
Standard library HTTP server for the Data Structures Visualizer.
Runs without requiring external pip dependencies.
Directly handles API endpoints for Heap, AVL, Graph, and Hash Table operations,
serving the modern HTML5/Canvas/CSS visualization client.
"""
import os
import json
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from engine.heap import BinaryHeap
from engine.avl import AVLTree
from engine.graph import Graph
from engine.hash_table import HashTable

PORT = 8000
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")

# In-memory singletons for active visualizer state
heap_instance = BinaryHeap(is_min_heap=True)
avl_instance = AVLTree()
graph_instance = Graph(is_directed=False)
hash_instance = HashTable(capacity=7)

def init_default_graph():
    """Seed graph with default nodes and edges for immediate visualization."""
    positions = {
        "A": {"x": 120, "y": 80},
        "B": {"x": 280, "y": 60},
        "C": {"x": 120, "y": 240},
        "D": {"x": 300, "y": 230},
        "E": {"x": 460, "y": 140},
        "F": {"x": 480, "y": 280}
    }
    for n, p in positions.items():
        graph_instance.add_node(n, p["x"], p["y"])
    edges = [
        ("A", "B", 4),
        ("A", "C", 2),
        ("B", "C", 1),
        ("B", "D", 5),
        ("C", "D", 8),
        ("C", "E", 10),
        ("D", "E", 2),
        ("D", "F", 6),
        ("E", "F", 3)
    ]
    for u, v, w in edges:
        graph_instance.add_edge(u, v, w)

init_default_graph()

class DSAVisualizerHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=STATIC_DIR, **kwargs)

    def _send_json(self, data, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode("utf-8"))

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_POST(self):
        content_length = int(self.headers.get("Content-Length", 0))
        post_data = self.rfile.read(content_length)
        body = json.loads(post_data.decode("utf-8")) if content_length > 0 else {}
        path = urlparse(self.path).path

        global heap_instance, avl_instance, graph_instance, hash_instance

        # ================= HEAP API =================
        if path == "/api/heap/insert":
            val = int(body.get("val", 0))
            trace = heap_instance.insert(val)
            self._send_json({"trace": trace, "state": heap_instance.get_state()})

        elif path == "/api/heap/extract":
            trace = heap_instance.extract_root()
            self._send_json({"trace": trace, "state": heap_instance.get_state()})

        elif path == "/api/heap/toggle_mode":
            mode = body.get("mode", "min")
            trace = heap_instance.set_mode(is_min_heap=(mode == "min"))
            self._send_json({"trace": trace, "state": heap_instance.get_state()})

        elif path == "/api/heap/reset":
            heap_instance = BinaryHeap(is_min_heap=(body.get("mode", "min") == "min"))
            self._send_json({"status": "ok", "state": heap_instance.get_state()})

        # ================= AVL API =================
        elif path == "/api/avl/insert":
            key = int(body.get("key", 0))
            trace = avl_instance.insert(key)
            self._send_json({"trace": trace, "tree": avl_instance.get_snapshot()})

        elif path == "/api/avl/delete":
            key = int(body.get("key", 0))
            trace = avl_instance.delete(key)
            self._send_json({"trace": trace, "tree": avl_instance.get_snapshot()})

        elif path == "/api/avl/reset":
            avl_instance = AVLTree()
            self._send_json({"status": "ok", "tree": None})

        # ================= GRAPH API =================
        elif path == "/api/graph/bfs":
            start = body.get("start", "A")
            trace = graph_instance.bfs(start)
            self._send_json({"trace": trace, "graph": graph_instance.get_structure()})

        elif path == "/api/graph/dfs":
            start = body.get("start", "A")
            trace = graph_instance.dfs(start)
            self._send_json({"trace": trace, "graph": graph_instance.get_structure()})

        elif path == "/api/graph/dijkstra":
            start = body.get("start", "A")
            trace = graph_instance.dijkstra(start)
            self._send_json({"trace": trace, "graph": graph_instance.get_structure()})

        elif path == "/api/graph/prim":
            start = body.get("start", "A")
            trace = graph_instance.prim_mst(start)
            self._send_json({"trace": trace, "graph": graph_instance.get_structure()})

        elif path == "/api/graph/add_node":
            node = body.get("node", "").strip().upper()
            x = float(body.get("x", 200))
            y = float(body.get("y", 150))
            if node:
                graph_instance.add_node(node, x, y)
            self._send_json({"graph": graph_instance.get_structure()})

        elif path == "/api/graph/add_edge":
            u = body.get("u", "").strip().upper()
            v = body.get("v", "").strip().upper()
            w = float(body.get("weight", 1.0))
            if u and v:
                graph_instance.add_edge(u, v, w)
            self._send_json({"graph": graph_instance.get_structure()})

        elif path == "/api/graph/reset":
            graph_instance = Graph(is_directed=False)
            init_default_graph()
            self._send_json({"graph": graph_instance.get_structure()})

        # ================= HASH TABLE API =================
        elif path == "/api/hash/insert":
            key = int(body.get("key", 0))
            val = body.get("val", str(key))
            trace = hash_instance.insert(key, val)
            self._send_json({"trace": trace, "table": hash_instance.get_table_state()})

        elif path == "/api/hash/search":
            key = int(body.get("key", 0))
            trace = hash_instance.search(key)
            self._send_json({"trace": trace, "table": hash_instance.get_table_state()})

        elif path == "/api/hash/delete":
            key = int(body.get("key", 0))
            trace = hash_instance.delete(key)
            self._send_json({"trace": trace, "table": hash_instance.get_table_state()})

        elif path == "/api/hash/reset":
            cap = int(body.get("capacity", 7))
            hash_instance = HashTable(capacity=cap)
            self._send_json({"status": "ok", "table": hash_instance.get_table_state()})

        else:
            self.send_error(404, "Endpoint not found")

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/state":
            self._send_json({
                "heap": heap_instance.get_state(),
                "avl": avl_instance.get_snapshot(),
                "graph": graph_instance.get_structure(),
                "hash": hash_instance.get_table_state()
            })
        else:
            super().do_GET()

def run_server(port=PORT):
    server_address = ('', port)
    httpd = HTTPServer(server_address, DSAVisualizerHandler)
    print(f"==================================================")
    print(f" DSA Visualizer (Python Server) running on http://localhost:{port}")
    print(f"==================================================")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server.")
        httpd.server_close()

if __name__ == "__main__":
    run_server()
