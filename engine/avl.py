"""
AVL Tree module:
- Self-balancing Binary Search Tree
- Computes heights and balance factors
- Real-time reactive balancing
- Automates and animates all four rotation cases:
  1. Single Right Rotation (LL Case)
  2. Single Left Rotation (RR Case)
  3. Double Left-Right Rotation (LR Case)
  4. Double Right-Left Rotation (RL Case)
- Emits detailed trace events for step-through visualization
"""
from typing import Optional, Dict, Any, List
from engine.tracer import TraceRecorder

class AVLNode:
    def __init__(self, key: int):
        self.key = key
        self.height = 1
        self.left: Optional['AVLNode'] = None
        self.right: Optional['AVLNode'] = None

    def balance_factor(self) -> int:
        lh = self.left.height if self.left else 0
        rh = self.right.height if self.right else 0
        return lh - rh

    def update_height(self):
        lh = self.left.height if self.left else 0
        rh = self.right.height if self.right else 0
        self.height = 1 + max(lh, rh)

    def to_dict(self) -> Dict[str, Any]:
        """Convert subtree to hierarchical dict for canvas rendering."""
        return {
            "key": self.key,
            "height": self.height,
            "bf": self.balance_factor(),
            "left": self.left.to_dict() if self.left else None,
            "right": self.right.to_dict() if self.right else None
        }

class AVLTree:
    def __init__(self):
        self.root: Optional[AVLNode] = None

    def get_snapshot(self) -> Optional[Dict[str, Any]]:
        return self.root.to_dict() if self.root else None

    def insert(self, key: int, tracer: Optional[TraceRecorder] = None) -> List[Dict[str, Any]]:
        if tracer is None:
            tracer = TraceRecorder()

        tracer.record(
            "start",
            f"Starting insertion of key {key} into AVL Tree.",
            tree=self.get_snapshot()
        )
        self.root = self._insert_node(self.root, key, tracer)
        tracer.record(
            "state",
            f"Key {key} successfully integrated. Tree is balanced.",
            tree=self.get_snapshot()
        )
        return tracer.get_trace()

    def _insert_node(self, node: Optional[AVLNode], key: int, tracer: TraceRecorder) -> AVLNode:
        if not node:
            tracer.record(
                "insert",
                f"Created new leaf node with key {key}.",
                key=key,
                tree=self.get_snapshot()
            )
            return AVLNode(key)

        tracer.record(
            "compare",
            f"Comparing inserting key {key} with node {node.key}.",
            key=key,
            current=node.key,
            tree=self.get_snapshot()
        )

        if key < node.key:
            tracer.record(
                "highlight",
                f"{key} < {node.key}: traversing left subtree.",
                direction="left",
                current=node.key,
                tree=self.get_snapshot()
            )
            node.left = self._insert_node(node.left, key, tracer)
        elif key > node.key:
            tracer.record(
                "highlight",
                f"{key} > {node.key}: traversing right subtree.",
                direction="right",
                current=node.key,
                tree=self.get_snapshot()
            )
            node.right = self._insert_node(node.right, key, tracer)
        else:
            tracer.record(
                "info",
                f"Duplicate key {key} already exists in tree. No change made.",
                current=node.key,
                tree=self.get_snapshot()
            )
            return node

        # Update height
        node.update_height()
        bf = node.balance_factor()

        tracer.record(
            "check_balance",
            f"Node {node.key} recalculated: height={node.height}, balance_factor={bf}.",
            current=node.key,
            bf=bf,
            height=node.height,
            tree=self.get_snapshot()
        )

        # Balance check
        # Case 1: Left-Left (LL) -> Single Right Rotation
        if bf > 1 and node.left and key < node.left.key:
            tracer.record(
                "rotate",
                f"Imbalance at node {node.key} (BF={bf})! Left-Left (LL) Case detected. Executing Right Rotation.",
                case="LL",
                rotation="Right",
                pivot=node.key,
                child=node.left.key,
                tree=self.get_snapshot()
            )
            return self._right_rotate(node, tracer)

        # Case 2: Right-Right (RR) -> Single Left Rotation
        if bf < -1 and node.right and key > node.right.key:
            tracer.record(
                "rotate",
                f"Imbalance at node {node.key} (BF={bf})! Right-Right (RR) Case detected. Executing Left Rotation.",
                case="RR",
                rotation="Left",
                pivot=node.key,
                child=node.right.key,
                tree=self.get_snapshot()
            )
            return self._left_rotate(node, tracer)

        # Case 3: Left-Right (LR) -> Double Rotation (Left on child, then Right on node)
        if bf > 1 and node.left and key > node.left.key:
            tracer.record(
                "rotate",
                f"Imbalance at node {node.key} (BF={bf})! Left-Right (LR) Case detected. Step 1: Left Rotate child {node.left.key}.",
                case="LR",
                rotation="Left-Right (Part 1)",
                pivot=node.left.key,
                tree=self.get_snapshot()
            )
            node.left = self._left_rotate(node.left, tracer)
            tracer.record(
                "rotate",
                f"Left-Right (LR) Step 2: Right Rotate node {node.key}.",
                case="LR",
                rotation="Left-Right (Part 2)",
                pivot=node.key,
                tree=self.get_snapshot()
            )
            return self._right_rotate(node, tracer)

        # Case 4: Right-Left (RL) -> Double Rotation (Right on child, then Left on node)
        if bf < -1 and node.right and key < node.right.key:
            tracer.record(
                "rotate",
                f"Imbalance at node {node.key} (BF={bf})! Right-Left (RL) Case detected. Step 1: Right Rotate child {node.right.key}.",
                case="RL",
                rotation="Right-Left (Part 1)",
                pivot=node.right.key,
                tree=self.get_snapshot()
            )
            node.right = self._right_rotate(node.right, tracer)
            tracer.record(
                "rotate",
                f"Right-Left (RL) Step 2: Left Rotate node {node.key}.",
                case="RL",
                rotation="Right-Left (Part 2)",
                pivot=node.key,
                tree=self.get_snapshot()
            )
            return self._left_rotate(node, tracer)

        return node

    def delete(self, key: int, tracer: Optional[TraceRecorder] = None) -> List[Dict[str, Any]]:
        if tracer is None:
            tracer = TraceRecorder()

        tracer.record(
            "start",
            f"Starting deletion of key {key} from AVL Tree.",
            tree=self.get_snapshot()
        )
        self.root = self._delete_node(self.root, key, tracer)
        tracer.record(
            "state",
            f"Deletion complete. Tree re-balanced.",
            tree=self.get_snapshot()
        )
        return tracer.get_trace()

    def _delete_node(self, root: Optional[AVLNode], key: int, tracer: TraceRecorder) -> Optional[AVLNode]:
        if not root:
            tracer.record("info", f"Key {key} not found in AVL Tree.", tree=self.get_snapshot())
            return root

        tracer.record(
            "compare",
            f"Comparing target key {key} with current node {root.key}.",
            key=key,
            current=root.key,
            tree=self.get_snapshot()
        )

        if key < root.key:
            root.left = self._delete_node(root.left, key, tracer)
        elif key > root.key:
            root.right = self._delete_node(root.right, key, tracer)
        else:
            # Node to be deleted found
            tracer.record(
                "delete",
                f"Found node {root.key} to remove.",
                current=root.key,
                tree=self.get_snapshot()
            )
            if not root.left:
                temp = root.right
                return temp
            elif not root.right:
                temp = root.left
                return temp

            # Node with two children: Get the inorder successor (smallest in the right subtree)
            successor = self._min_value_node(root.right)
            tracer.record(
                "highlight",
                f"Node {root.key} has two children. Inorder successor is {successor.key}. Replacing value.",
                successor=successor.key,
                current=root.key,
                tree=self.get_snapshot()
            )
            root.key = successor.key
            root.right = self._delete_node(root.right, successor.key, tracer)

        if not root:
            return None

        root.update_height()
        bf = root.balance_factor()

        tracer.record(
            "check_balance",
            f"Post-delete balance check at node {root.key}: BF={bf}.",
            current=root.key,
            bf=bf,
            tree=self.get_snapshot()
        )

        # Rebalance
        if bf > 1 and root.left and root.left.balance_factor() >= 0:
            tracer.record("rotate", f"Delete LL Case: Right rotate {root.key}.", case="LL", tree=self.get_snapshot())
            return self._right_rotate(root, tracer)

        if bf > 1 and root.left and root.left.balance_factor() < 0:
            tracer.record("rotate", f"Delete LR Case: Double rotation on {root.key}.", case="LR", tree=self.get_snapshot())
            root.left = self._left_rotate(root.left, tracer)
            return self._right_rotate(root, tracer)

        if bf < -1 and root.right and root.right.balance_factor() <= 0:
            tracer.record("rotate", f"Delete RR Case: Left rotate {root.key}.", case="RR", tree=self.get_snapshot())
            return self._left_rotate(root, tracer)

        if bf < -1 and root.right and root.right.balance_factor() > 0:
            tracer.record("rotate", f"Delete RL Case: Double rotation on {root.key}.", case="RL", tree=self.get_snapshot())
            root.right = self._right_rotate(root.right, tracer)
            return self._left_rotate(root, tracer)

        return root

    def _min_value_node(self, node: AVLNode) -> AVLNode:
        curr = node
        while curr.left:
            curr = curr.left
        return curr

    def _left_rotate(self, z: AVLNode, tracer: TraceRecorder) -> AVLNode:
        y = z.right
        assert y is not None
        T2 = y.left

        # Perform rotation
        y.left = z
        z.right = T2

        # Update heights
        z.update_height()
        y.update_height()

        tracer.record(
            "state",
            f"Left rotation complete: {y.key} becomes new root of subtree replacing {z.key}.",
            pivot=z.key,
            new_root=y.key,
            tree=self.get_snapshot()
        )
        return y

    def _right_rotate(self, z: AVLNode, tracer: TraceRecorder) -> AVLNode:
        y = z.left
        assert y is not None
        T3 = y.right

        # Perform rotation
        y.right = z
        z.left = T3

        # Update heights
        z.update_height()
        y.update_height()

        tracer.record(
            "state",
            f"Right rotation complete: {y.key} becomes new root of subtree replacing {z.key}.",
            pivot=z.key,
            new_root=y.key,
            tree=self.get_snapshot()
        )
        return y
