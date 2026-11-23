"""
Trace recorder for the Python DSA Visualizer engine.
Follows the exact 'Record & Replay' architecture:
Compute first, record atomic steps, render smoothly in the UI.
"""
from typing import List, Dict, Any, Optional

class TraceRecorder:
    def __init__(self):
        self.steps: List[Dict[str, Any]] = []

    def clear(self):
        self.steps.clear()

    def record(self, step_type: str, description: str, **kwargs):
        """
        step_type can be:
        - 'compare': comparing two elements
        - 'swap': swapping two elements
        - 'highlight': highlighting a node/element
        - 'unhighlight': resetting node/element
        - 'insert': inserting element
        - 'delete': removing element
        - 'rotate': tree rotation (LL, RR, LR, RL)
        - 'relax': edge relaxation in graph algorithms
        - 'mst_edge': adding edge to MST
        - 'stack_push' / 'stack_pop': DFS stack state
        - 'queue_push' / 'queue_pop': BFS queue state
        - 'hash_compute': hash function calculation
        - 'chain_traverse': traversing linked list chain in hash table
        - 'state': full snapshot of the structure
        """
        payload = {
            "type": step_type,
            "description": description,
            **kwargs
        }
        self.steps.append(payload)

    def get_trace(self) -> List[Dict[str, Any]]:
        return list(self.steps)
