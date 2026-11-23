"""
Binary Heap module:
- Dynamic toggling: Min-Heap and Max-Heap
- Simultaneous dual representation: Linear array + Logical tree
- Sift-up and sift-down operations with color-coded trace events
  (comparisons = yellow, swaps = red)
- Record & Replay trace generation
"""
from typing import List, Dict, Any, Optional
from engine.tracer import TraceRecorder

class BinaryHeap:
    def __init__(self, is_min_heap: bool = True):
        self.is_min_heap = is_min_heap
        self.data: List[int] = []

    def set_mode(self, is_min_heap: bool, tracer: Optional[TraceRecorder] = None) -> List[Dict[str, Any]]:
        """Re-heapifies the existing array according to the new mode."""
        self.is_min_heap = is_min_heap
        if tracer is None:
            tracer = TraceRecorder()
        tracer.record(
            "mode_change",
            f"Switched heap mode to {'Min-Heap' if self.is_min_heap else 'Max-Heap'}. Re-heapifying...",
            mode="min" if self.is_min_heap else "max",
            array=list(self.data)
        )
        # Build heap from bottom-up
        n = len(self.data)
        for i in range((n // 2) - 1, -1, -1):
            self._sift_down(i, tracer)
        tracer.record(
            "state",
            f"Heapify complete for {'Min-Heap' if self.is_min_heap else 'Max-Heap'}.",
            array=list(self.data),
            mode="min" if self.is_min_heap else "max"
        )
        return tracer.get_trace()

    def _prioritizes(self, a: int, b: int) -> bool:
        """True if element 'a' should be higher in priority than 'b'."""
        return (a < b) if self.is_min_heap else (a > b)

    def insert(self, val: int, tracer: Optional[TraceRecorder] = None) -> List[Dict[str, Any]]:
        if tracer is None:
            tracer = TraceRecorder()

        self.data.append(val)
        idx = len(self.data) - 1
        tracer.record(
            "insert",
            f"Appended {val} at index {idx} (bottom of tree / end of array).",
            index=idx,
            val=val,
            array=list(self.data)
        )

        self._sift_up(idx, tracer)
        tracer.record(
            "state",
            f"Insertion of {val} finished. Valid {'Min-Heap' if self.is_min_heap else 'Max-Heap'} restored.",
            array=list(self.data)
        )
        return tracer.get_trace()

    def _sift_up(self, idx: int, tracer: TraceRecorder):
        while idx > 0:
            parent_idx = (idx - 1) // 2
            val = self.data[idx]
            pval = self.data[parent_idx]

            tracer.record(
                "compare",
                f"Comparing child [{idx}]={val} with parent [{parent_idx}]={pval}.",
                idx1=idx,
                idx2=parent_idx,
                val1=val,
                val2=pval,
                array=list(self.data)
            )

            if self._prioritizes(val, pval):
                # Swap needed
                self.data[idx], self.data[parent_idx] = self.data[parent_idx], self.data[idx]
                tracer.record(
                    "swap",
                    f"Violation! Swapping child [{idx}]={val} with parent [{parent_idx}]={pval}.",
                    idx1=idx,
                    idx2=parent_idx,
                    val1=val,
                    val2=pval,
                    array=list(self.data)
                )
                idx = parent_idx
            else:
                tracer.record(
                    "highlight",
                    f"Order property satisfied: parent [{parent_idx}]={pval} is correct relative to [{idx}]={val}.",
                    indices=[idx, parent_idx],
                    array=list(self.data)
                )
                break

    def extract_root(self, tracer: Optional[TraceRecorder] = None) -> List[Dict[str, Any]]:
        if tracer is None:
            tracer = TraceRecorder()

        if not self.data:
            tracer.record("error", "Cannot extract: Heap is empty.")
            return tracer.get_trace()

        root_val = self.data[0]
        last_val = self.data[-1]

        if len(self.data) == 1:
            self.data.pop()
            tracer.record(
                "delete",
                f"Extracted only element ({root_val}). Heap is now empty.",
                val=root_val,
                index=0,
                array=[]
            )
            return tracer.get_trace()

        # Swap root with last
        tracer.record(
            "swap",
            f"Moving root {root_val} to the end and replacing root with last element {last_val}.",
            idx1=0,
            idx2=len(self.data) - 1,
            val1=root_val,
            val2=last_val,
            array=list(self.data)
        )
        self.data[0] = self.data.pop()

        tracer.record(
            "delete",
            f"Extracted root {root_val}. Now sifting down new root {self.data[0]} at index 0.",
            val=root_val,
            index=0,
            array=list(self.data)
        )

        self._sift_down(0, tracer)
        tracer.record(
            "state",
            f"Extract root complete. Extracted value: {root_val}.",
            extracted=root_val,
            array=list(self.data)
        )
        return tracer.get_trace()

    def _sift_down(self, idx: int, tracer: TraceRecorder):
        n = len(self.data)
        while True:
            left_idx = 2 * idx + 1
            right_idx = 2 * idx + 2
            priority_idx = idx

            if left_idx < n:
                tracer.record(
                    "compare",
                    f"Comparing current [{priority_idx}]={self.data[priority_idx]} with left child [{left_idx}]={self.data[left_idx]}.",
                    idx1=priority_idx,
                    idx2=left_idx,
                    array=list(self.data)
                )
                if self._prioritizes(self.data[left_idx], self.data[priority_idx]):
                    priority_idx = left_idx

            if right_idx < n:
                tracer.record(
                    "compare",
                    f"Comparing best candidate [{priority_idx}]={self.data[priority_idx]} with right child [{right_idx}]={self.data[right_idx]}.",
                    idx1=priority_idx,
                    idx2=right_idx,
                    array=list(self.data)
                )
                if self._prioritizes(self.data[right_idx], self.data[priority_idx]):
                    priority_idx = right_idx

            if priority_idx != idx:
                val1 = self.data[idx]
                val2 = self.data[priority_idx]
                self.data[idx], self.data[priority_idx] = self.data[priority_idx], self.data[idx]
                tracer.record(
                    "swap",
                    f"Sift-down swap: index {idx} ({val1}) with index {priority_idx} ({val2}).",
                    idx1=idx,
                    idx2=priority_idx,
                    val1=val1,
                    val2=val2,
                    array=list(self.data)
                )
                idx = priority_idx
            else:
                tracer.record(
                    "highlight",
                    f"Sift-down stopped at index {idx}: Heap invariant satisfied.",
                    indices=[idx],
                    array=list(self.data)
                )
                break

    def get_state(self) -> Dict[str, Any]:
        return {
            "mode": "min" if self.is_min_heap else "max",
            "array": list(self.data),
            "size": len(self.data)
        }
