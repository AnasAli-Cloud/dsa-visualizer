"""
Graph module:
- Force-directed / interactive graph representation
- Traversal Suite:
  * BFS using custom MyQueue (FIFO queue)
  * DFS using custom MyStack (LIFO stack) with backtracking
- Optimization Solvers:
  * Dijkstra's Algorithm (shortest path relaxation with custom priority queue)
  * Prim's MST (Minimum Spanning Tree visualizer turning optimal edges green)
- Emits atomic steps for real-time visualization of frontiers, stacks, queues, and tables
"""
from typing import Dict, List, Any, Optional, Tuple
from engine.tracer import TraceRecorder
from engine.structures import MyQueue, MyStack

class Edge:
    def __init__(self, u: str, v: str, weight: float):
        self.u = u
        self.v = v
        self.weight = weight

    def to_dict(self) -> Dict[str, Any]:
        return {"u": self.u, "v": self.v, "weight": self.weight}

class Graph:
    def __init__(self, is_directed: bool = False):
        self.is_directed = is_directed
        self.adj: Dict[str, List[Tuple[str, float]]] = {}
        self.node_positions: Dict[str, Dict[str, float]] = {}

    def add_node(self, node: str, x: float = 0.0, y: float = 0.0):
        if node not in self.adj:
            self.adj[node] = []
            self.node_positions[node] = {"x": x, "y": y}

    def add_edge(self, u: str, v: str, weight: float = 1.0):
        self.add_node(u)
        self.add_node(v)
        # Avoid duplicate edges
        self.adj[u] = [(n, w) for n, w in self.adj[u] if n != v]
        self.adj[u].append((v, weight))
        if not self.is_directed:
            self.adj[v] = [(n, w) for n, w in self.adj[v] if n != u]
            self.adj[v].append((u, weight))

    def get_structure(self) -> Dict[str, Any]:
        edges = []
        seen = set()
        for u, neighbors in self.adj.items():
            for v, w in neighbors:
                edge_id = f"{u}->{v}" if self.is_directed else tuple(sorted([u, v]))
                if edge_id not in seen:
                    seen.add(edge_id)
                    edges.append({"u": u, "v": v, "weight": w})
        return {
            "nodes": list(self.adj.keys()),
            "positions": self.node_positions,
            "edges": edges,
            "directed": self.is_directed
        }

    # ==================== BFS Traversal ====================
    def bfs(self, start_node: str, tracer: Optional[TraceRecorder] = None) -> List[Dict[str, Any]]:
        if tracer is None:
            tracer = TraceRecorder()

        if start_node not in self.adj:
            tracer.record("error", f"Start node '{start_node}' does not exist.")
            return tracer.get_trace()

        visited = set([start_node])
        queue = MyQueue()
        queue.enqueue(start_node)

        tracer.record(
            "queue_push",
            f"BFS started from '{start_node}'. Enqueued '{start_node}'.",
            node=start_node,
            queue=queue.to_list(),
            visited=list(visited)
        )

        while not queue.is_empty():
            curr = queue.dequeue()
            tracer.record(
                "queue_pop",
                f"Dequeued '{curr}' from FIFO Queue. Exploring frontiers...",
                current=curr,
                queue=queue.to_list(),
                visited=list(visited)
            )

            for neighbor, weight in sorted(self.adj[curr], key=lambda x: str(x[0])):
                tracer.record(
                    "explore_edge",
                    f"Checking neighbor '{neighbor}' of '{curr}'.",
                    from_node=curr,
                    to_node=neighbor,
                    edge={"u": curr, "v": neighbor, "weight": weight},
                    queue=queue.to_list(),
                    visited=list(visited)
                )

                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.enqueue(neighbor)
                    tracer.record(
                        "queue_push",
                        f"Unvisited neighbor '{neighbor}' discovered! Enqueuing to FIFO Queue.",
                        node=neighbor,
                        from_node=curr,
                        queue=queue.to_list(),
                        visited=list(visited)
                    )
                else:
                    tracer.record(
                        "info",
                        f"Neighbor '{neighbor}' is already visited.",
                        current=curr,
                        neighbor=neighbor,
                        queue=queue.to_list()
                    )

        tracer.record(
            "state",
            f"BFS traversal from '{start_node}' completed.",
            visited=list(visited),
            queue=[]
        )
        return tracer.get_trace()

    # ==================== DFS Traversal ====================
    def dfs(self, start_node: str, tracer: Optional[TraceRecorder] = None) -> List[Dict[str, Any]]:
        if tracer is None:
            tracer = TraceRecorder()

        if start_node not in self.adj:
            tracer.record("error", f"Start node '{start_node}' does not exist.")
            return tracer.get_trace()

        stack = MyStack()
        visited = set()
        edge_to = {}

        stack.push(start_node)
        tracer.record(
            "stack_push",
            f"DFS started. Pushed '{start_node}' onto custom LIFO stack.",
            node=start_node,
            stack=stack.to_list(),
            visited=list(visited)
        )

        while not stack.is_empty():
            curr = stack.pop()
            tracer.record(
                "stack_pop",
                f"Popped '{curr}' from LIFO stack.",
                current=curr,
                stack=stack.to_list(),
                visited=list(visited)
            )

            if curr not in visited:
                visited.add(curr)
                tracer.record(
                    "visit",
                    f"Marked '{curr}' as visited.",
                    current=curr,
                    stack=stack.to_list(),
                    visited=list(visited)
                )

                # Push unvisited neighbors in reverse order so lowest gets visited first
                neighbors = sorted(self.adj[curr], key=lambda x: str(x[0]), reverse=True)
                for neighbor, weight in neighbors:
                    if neighbor not in visited:
                        stack.push(neighbor)
                        edge_to[neighbor] = curr
                        tracer.record(
                            "stack_push",
                            f"Pushed unvisited neighbor '{neighbor}' onto LIFO stack.",
                            node=neighbor,
                            from_node=curr,
                            stack=stack.to_list(),
                            visited=list(visited)
                        )
            else:
                tracer.record(
                    "backtrack",
                    f"Node '{curr}' was already visited, backtracking...",
                    current=curr,
                    stack=stack.to_list(),
                    visited=list(visited)
                )

        tracer.record(
            "state",
            f"DFS traversal complete from '{start_node}'.",
            visited=list(visited),
            stack=[]
        )
        return tracer.get_trace()

    # ==================== Dijkstra Shortest Path ====================
    def dijkstra(self, start_node: str, tracer: Optional[TraceRecorder] = None) -> List[Dict[str, Any]]:
        if tracer is None:
            tracer = TraceRecorder()

        if start_node not in self.adj:
            tracer.record("error", f"Start node '{start_node}' does not exist.")
            return tracer.get_trace()

        distances = {node: float('inf') for node in self.adj}
        distances[start_node] = 0
        parent = {node: None for node in self.adj}
        visited = set()

        # Priority Queue simulation: entries are (distance, node)
        pq: List[Tuple[float, str]] = [(0, start_node)]

        tracer.record(
            "relax",
            f"Initialized Dijkstra from '{start_node}'. Distance to '{start_node}' = 0, all others = ∞.",
            distances={k: (str(v) if v != float('inf') else "∞") for k, v in distances.items()},
            pq=list(pq),
            current=start_node
        )

        while pq:
            # Pop minimum distance node (custom manual min extraction)
            min_idx = 0
            for i in range(1, len(pq)):
                if pq[i][0] < pq[min_idx][0]:
                    min_idx = i
            curr_dist, u = pq.pop(min_idx)

            if u in visited:
                continue
            visited.add(u)

            tracer.record(
                "highlight",
                f"Selected '{u}' with minimum tentative distance {curr_dist}.",
                current=u,
                dist=curr_dist,
                visited=list(visited),
                distances={k: (str(v) if v != float('inf') else "∞") for k, v in distances.items()}
            )

            for v, weight in self.adj[u]:
                if v not in visited:
                    new_dist = curr_dist + weight
                    old_dist = distances[v]
                    tracer.record(
                        "compare",
                        f"Examining edge ({u} -> {v}, weight={weight}). Tentative = {curr_dist} + {weight} = {new_dist} vs Current = {('∞' if old_dist == float('inf') else old_dist)}.",
                        u=u,
                        v=v,
                        weight=weight,
                        new_dist=new_dist,
                        old_dist=('∞' if old_dist == float('inf') else old_dist)
                    )

                    if new_dist < old_dist:
                        distances[v] = new_dist
                        parent[v] = u
                        pq.append((new_dist, v))
                        tracer.record(
                            "relax",
                            f"Relaxation successful! Updated distance of '{v}' to {new_dist} via '{u}'.",
                            u=u,
                            v=v,
                            new_dist=new_dist,
                            distances={k: (str(v) if v != float('inf') else "∞") for k, v in distances.items()},
                            parent=parent
                        )

        tracer.record(
            "state",
            f"Dijkstra shortest paths from '{start_node}' calculated.",
            distances={k: (str(v) if v != float('inf') else "∞") for k, v in distances.items()},
            parent=parent,
            visited=list(visited)
        )
        return tracer.get_trace()

    # ==================== Prim's Minimum Spanning Tree ====================
    def prim_mst(self, start_node: Optional[str] = None, tracer: Optional[TraceRecorder] = None) -> List[Dict[str, Any]]:
        if tracer is None:
            tracer = TraceRecorder()

        if not self.adj:
            tracer.record("error", "Graph is empty.")
            return tracer.get_trace()

        nodes = list(self.adj.keys())
        if start_node is None or start_node not in self.adj:
            start_node = nodes[0]

        visited = set([start_node])
        mst_edges: List[Dict[str, Any]] = []
        total_weight = 0.0

        tracer.record(
            "highlight",
            f"Prim's MST initialized starting with vertex '{start_node}'.",
            current=start_node,
            visited=list(visited),
            mst_edges=list(mst_edges)
        )

        while len(visited) < len(self.adj):
            # Find candidate edge with minimal weight connecting visited set to unvisited set
            best_edge = None
            min_weight = float('inf')

            for u in visited:
                for v, weight in self.adj[u]:
                    if v not in visited:
                        tracer.record(
                            "compare",
                            f"Evaluating candidate edge ({u} - {v}) with weight {weight}.",
                            u=u,
                            v=v,
                            weight=weight,
                            current_min=min_weight if min_weight != float('inf') else "None"
                        )
                        if weight < min_weight:
                            min_weight = weight
                            best_edge = (u, v, weight)

            if not best_edge:
                tracer.record("info", "Graph is disconnected; MST spans reachable connected component.")
                break

            u, v, weight = best_edge
            visited.add(v)
            mst_edges.append({"u": u, "v": v, "weight": weight})
            total_weight += weight

            tracer.record(
                "mst_edge",
                f"Optimal edge found! Added ({u} - {v}) with weight {weight} to MST (turned GREEN).",
                edge={"u": u, "v": v, "weight": weight},
                mst_edges=list(mst_edges),
                visited=list(visited),
                total_weight=total_weight
            )

        tracer.record(
            "state",
            f"Prim's MST complete! Spanned {len(visited)} nodes with Total MST Weight = {total_weight}.",
            mst_edges=list(mst_edges),
            total_weight=total_weight,
            visited=list(visited)
        )
        return tracer.get_trace()
