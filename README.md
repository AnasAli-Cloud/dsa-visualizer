# Data Structures Visualizer (Python Edition)

An interactive, high-performance Data Structures & Algorithms visualizer built from scratch according to the **CS-2001 Data Structures Lab** specification, adapted into a pure Python backend + HTML5/CSS3/Canvas visualization engine.

---

## 🌟 Core Modules & Features

### 1. The Priority Engine (Binary Heap)
- **Min-Heap & Max-Heap Dynamic Toggling**: Switch modes on the fly; the engine automatically re-heapifies using bottom-up sift-down.
- **Simultaneous Dual View**: Synchronously visualizes the **logical binary tree** on Canvas alongside the **linear memory array** in the auxiliary dock.
- **Algorithmic Color-Coding**:
  - Yellow: Element comparison (`arr[child]` vs `arr[parent]`).
  - Red: Element sift-up or sift-down swap.

### 2. The Self-Balancing Core (AVL Tree)
- Dynamic Binary Search Tree with real-time balance factor ($BF = h_L - h_R$) detection.
- Automates & animates all 4 rotation scenarios:
  - **Single Right Rotation** (Left-Left Case)
  - **Single Left Rotation** (Right-Right Case)
  - **Double Left-Right Rotation** (Left-Right Case)
  - **Double Right-Left Rotation** (Right-Left Case)
- Quick preset buttons (`Preset LL`, `Preset LR`) for immediate rotation demonstration.

### 3. The Graph Navigator
- Interactive node layout with customizable vertices, weighted edges, and starting points.
- **Traversal Suite**:
  - **Breadth-First Search (BFS)**: Uses custom `MyQueue` (FIFO ring-buffer) and displays frontier elements in real-time.
  - **Depth-First Search (DFS)**: Uses custom `MyStack` (pointer-based LIFO stack) showing active push, pop, and backtracking steps.
- **Optimization Solvers**:
  - **Dijkstra's Shortest Path**: Highlights relaxation steps, tentative distance table updates, and paths discovered.
  - **Prim's Minimum Spanning Tree (MST)**: Progressively selects minimal cut edges and turns optimal edges **GREEN** in real time.

### 4. The Hash Mapper
- Demonstrates **Separate Chaining Collision Resolution**.
- Visual hash formula: $\text{hash}(key) = key \pmod 7$.
- Collisions are dynamically chained into linked-list buckets with collision tracking.
- Interactive Search, Insert, Delete, and a one-click **Demo Collisions** preset.

---

## 🏗️ Architecture: The "Record & Replay" Engine

To deliver lag-free, deterministic 60 FPS animations:
1. **Simulation Layer (Python Engine)**:
   - When an operation runs, the algorithm completes in microseconds in Python.
   - Every pointer move, comparison, swap, and balance check is recorded as an atomic JSON trace event.
2. **Presentation Layer (HTML5 Canvas & JavaScript Player)**:
   - Plays back the trace frame-by-frame with full controls: **Play, Pause, Step Forward, Step Backward, Speed Slider, and Timeline Scrubber**.
   - Dual-synchronized linear memory blocks and custom data structure inspectors.

---

## 🚀 Running the Visualizer

The project uses only standard Python 3 libraries (`http.server`, `json`, `urllib`), so **no pip installation or external dependencies are required**.

### Step 1: Start the Server
```bash
cd /home/anas-ali/Videos/dsa-visualizer
python3 server.py
```

### Step 2: Open in your Browser
Open:
```
http://localhost:8000
```
