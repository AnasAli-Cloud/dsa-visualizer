"""
Hash Mapper module:
- Implements hash table with Separate Chaining for collision resolution
- Static bucket array of size N (e.g. 7 or 10)
- Computes visual hash function: idx = key % capacity
- Collisions are dynamically chained in fixed-size bucket linked-list chains
- Detailed step tracing: hashing calculation, chain traversal, collision detection, insertion/deletion
"""
from typing import List, Optional, Dict, Any
from engine.tracer import TraceRecorder

class HashNode:
    def __init__(self, key: int, value: str, next_node: Optional['HashNode'] = None):
        self.key = key
        self.value = value
        self.next = next_node

    def to_dict(self) -> Dict[str, Any]:
        return {
            "key": self.key,
            "value": self.value,
            "next": self.next.to_dict() if self.next else None
        }

class HashTable:
    def __init__(self, capacity: int = 7):
        self.capacity = capacity
        self.buckets: List[Optional[HashNode]] = [None] * self.capacity
        self.size = 0

    def hash_func(self, key: int) -> int:
        return key % self.capacity

    def get_table_state(self) -> List[List[Dict[str, Any]]]:
        """Returns visual snapshot of all buckets and their chains."""
        state = []
        for i in range(self.capacity):
            chain = []
            curr = self.buckets[i]
            while curr:
                chain.append({"key": curr.key, "value": curr.value})
                curr = curr.next
            state.append(chain)
        return state

    def insert(self, key: int, value: Optional[str] = None, tracer: Optional[TraceRecorder] = None) -> List[Dict[str, Any]]:
        if tracer is None:
            tracer = TraceRecorder()

        if value is None:
            value = str(key)

        idx = self.hash_func(key)

        tracer.record(
            "hash_compute",
            f"Computing Hash for key {key}: hash({key}) = {key} % {self.capacity} = Bucket {idx}.",
            key=key,
            value=value,
            bucket_idx=idx,
            formula=f"{key} % {self.capacity} = {idx}",
            table=self.get_table_state()
        )

        curr = self.buckets[idx]
        prev = None
        chain_pos = 0

        # Traverse chain to inspect collisions or update existing key
        while curr:
            tracer.record(
                "chain_traverse",
                f"Traversing Bucket [{idx}], chain position {chain_pos}: Checking existing node with key {curr.key}.",
                bucket_idx=idx,
                chain_pos=chain_pos,
                existing_key=curr.key,
                target_key=key,
                table=self.get_table_state()
            )
            if curr.key == key:
                # Key already exists: update value
                curr.value = value
                tracer.record(
                    "state",
                    f"Key {key} already present at Bucket [{idx}], updated value to '{value}'.",
                    bucket_idx=idx,
                    key=key,
                    value=value,
                    table=self.get_table_state()
                )
                return tracer.get_trace()
            prev = curr
            curr = curr.next
            chain_pos += 1

        new_node = HashNode(key, value)
        if prev is None:
            # First element in bucket
            self.buckets[idx] = new_node
            tracer.record(
                "insert",
                f"Bucket [{idx}] is empty! Placed ({key}: '{value}') as the head of bucket chain.",
                bucket_idx=idx,
                key=key,
                value=value,
                collision=False,
                table=self.get_table_state()
            )
        else:
            # Collision! Separate Chaining links it to the tail
            prev.next = new_node
            tracer.record(
                "insert",
                f"COLLISION! Bucket [{idx}] already has items. Appended ({key}: '{value}') to separate chain.",
                bucket_idx=idx,
                key=key,
                value=value,
                collision=True,
                chain_pos=chain_pos,
                table=self.get_table_state()
            )

        self.size += 1
        tracer.record(
            "state",
            f"Key {key} mapped successfully. Load Factor = {self.size}/{self.capacity} ({self.size / self.capacity:.2f}).",
            table=self.get_table_state(),
            size=self.size,
            load_factor=round(self.size / self.capacity, 2)
        )
        return tracer.get_trace()

    def search(self, key: int, tracer: Optional[TraceRecorder] = None) -> List[Dict[str, Any]]:
        if tracer is None:
            tracer = TraceRecorder()

        idx = self.hash_func(key)
        tracer.record(
            "hash_compute",
            f"Searching key {key}: hash({key}) = {key} % {self.capacity} = Bucket {idx}.",
            key=key,
            bucket_idx=idx,
            table=self.get_table_state()
        )

        curr = self.buckets[idx]
        pos = 0
        found = False

        while curr:
            tracer.record(
                "chain_traverse",
                f"Checking Bucket [{idx}], node {pos}: {curr.key} == {key}?",
                bucket_idx=idx,
                chain_pos=pos,
                key=curr.key,
                target_key=key,
                table=self.get_table_state()
            )
            if curr.key == key:
                tracer.record(
                    "highlight",
                    f"FOUND! Key {key} discovered at Bucket [{idx}], chain index {pos}.",
                    bucket_idx=idx,
                    chain_pos=pos,
                    key=key,
                    value=curr.value,
                    table=self.get_table_state()
                )
                found = True
                break
            curr = curr.next
            pos += 1

        if not found:
            tracer.record(
                "info",
                f"Key {key} not found in Bucket [{idx}] chain.",
                bucket_idx=idx,
                key=key,
                table=self.get_table_state()
            )

        return tracer.get_trace()

    def delete(self, key: int, tracer: Optional[TraceRecorder] = None) -> List[Dict[str, Any]]:
        if tracer is None:
            tracer = TraceRecorder()

        idx = self.hash_func(key)
        tracer.record(
            "hash_compute",
            f"Deleting key {key}: hash({key}) = {key} % {self.capacity} = Bucket {idx}.",
            key=key,
            bucket_idx=idx,
            table=self.get_table_state()
        )

        curr = self.buckets[idx]
        prev = None
        pos = 0
        deleted = False

        while curr:
            if curr.key == key:
                if prev is None:
                    self.buckets[idx] = curr.next
                else:
                    prev.next = curr.next
                self.size -= 1
                deleted = True
                tracer.record(
                    "delete",
                    f"Deleted key {key} from Bucket [{idx}], position {pos}.",
                    bucket_idx=idx,
                    chain_pos=pos,
                    key=key,
                    table=self.get_table_state()
                )
                break
            prev = curr
            curr = curr.next
            pos += 1

        if not deleted:
            tracer.record("info", f"Key {key} not found to delete.", bucket_idx=idx, table=self.get_table_state())

        tracer.record("state", f"Delete operation finished for key {key}.", table=self.get_table_state())
        return tracer.get_trace()
