/**
 * Visualizer Presentation Layer (HTML5 Canvas + Record & Replay Player)
 * Renders Binary Heap (Dual tree & array), AVL Tree (with 4 rotations),
 * Graph Navigator (BFS, DFS, Dijkstra, Prim MST), and Hash Table (Separate Chaining).
 */

class VisualizerApp {
  constructor() {
    this.activeModule = "heap"; // 'heap' | 'avl' | 'graph' | 'hash'
    this.canvas = document.getElementById("mainCanvas");
    this.ctx = this.canvas.getContext("2d");

    // Trace playback engine state
    this.trace = [];
    this.currentStepIdx = 0;
    this.isPlaying = false;
    this.playbackTimer = null;
    this.speed = 700; // ms

    // Active visual state snapshots
    this.heapState = { mode: "min", array: [] };
    this.avlState = null;
    this.graphState = { nodes: [], edges: [], positions: {}, directed: false };
    this.hashState = [];

    // Animation highlights
    this.activeHighlights = {
      compare: [],
      swap: [],
      mstEdges: [],
      visitedNodes: [],
      activeNodes: [],
      activeEdge: null,
      activeBucket: null,
      activeChainPos: null,
      balanceFactors: true
    };

    this.initCanvasSize();
    this.bindEvents();
    this.fetchInitialState();
  }

  initCanvasSize() {
    const wrapper = document.getElementById("canvasWrapper");
    const dpr = window.devicePixelRatio || 1;
    this.width = wrapper.clientWidth;
    this.height = wrapper.clientHeight;
    this.canvas.width = this.width * dpr;
    this.canvas.height = this.height * dpr;
    this.ctx.scale(dpr, dpr);
    window.addEventListener("resize", () => {
      this.width = wrapper.clientWidth;
      this.height = wrapper.clientHeight;
      this.canvas.width = this.width * (window.devicePixelRatio || 1);
      this.canvas.height = this.height * (window.devicePixelRatio || 1);
      this.ctx.scale(window.devicePixelRatio || 1, window.devicePixelRatio || 1);
      this.render();
    });
  }

  bindEvents() {
    // Navigation Tabs
    document.querySelectorAll(".nav-tab").forEach(tab => {
      tab.addEventListener("click", () => {
        document.querySelectorAll(".nav-tab").forEach(t => t.classList.remove("active"));
        tab.classList.add("active");
        this.switchModule(tab.dataset.module);
      });
    });

    // Theme Toggle
    document.getElementById("themeToggleBtn").addEventListener("click", () => {
      document.body.classList.toggle("theme-light");
      document.body.classList.toggle("theme-dark");
      this.render();
    });

    // Playback Controls
    document.getElementById("playBtn").addEventListener("click", () => this.play());
    document.getElementById("pauseBtn").addEventListener("click", () => this.pause());
    document.getElementById("stepForwardBtn").addEventListener("click", () => this.stepForward());
    document.getElementById("stepBackBtn").addEventListener("click", () => this.stepBackward());
    document.getElementById("resetAnimBtn").addEventListener("click", () => this.jumpToStep(0));

    const scrubber = document.getElementById("traceScrubber");
    scrubber.addEventListener("input", (e) => {
      this.pause();
      this.jumpToStep(parseInt(e.target.value, 10));
    });

    const speedSlider = document.getElementById("speedSlider");
    speedSlider.addEventListener("input", (e) => {
      this.speed = parseInt(e.target.value, 10);
      document.getElementById("speedDisplay").innerText = `${this.speed}ms`;
      if (this.isPlaying) {
        this.pause();
        this.play();
      }
    });

    // Heap Events
    document.querySelectorAll("input[name='heapMode']").forEach(radio => {
      radio.addEventListener("change", (e) => this.toggleHeapMode(e.target.value));
    });
    document.getElementById("heapInsertBtn").addEventListener("click", () => {
      const inp = document.getElementById("heapInput");
      const val = parseInt(inp.value, 10);
      if (!isNaN(val)) {
        this.postAPI("/api/heap/insert", { val });
        inp.value = "";
      }
    });
    document.getElementById("heapExtractBtn").addEventListener("click", () => {
      this.postAPI("/api/heap/extract", {});
    });
    document.getElementById("heapRandomBtn").addEventListener("click", () => {
      const randVal = Math.floor(Math.random() * 90) + 10;
      this.postAPI("/api/heap/insert", { val: randVal });
    });
    document.getElementById("heapClearBtn").addEventListener("click", () => {
      const mode = document.querySelector("input[name='heapMode']:checked").value;
      this.postAPI("/api/heap/reset", { mode });
    });

    // AVL Events
    document.getElementById("avlInsertBtn").addEventListener("click", () => {
      const inp = document.getElementById("avlInput");
      const val = parseInt(inp.value, 10);
      if (!isNaN(val)) {
        this.postAPI("/api/avl/insert", { key: val });
        inp.value = "";
      }
    });
    document.getElementById("avlDeleteBtn").addEventListener("click", () => {
      const inp = document.getElementById("avlDeleteInput");
      const val = parseInt(inp.value, 10);
      if (!isNaN(val)) {
        this.postAPI("/api/avl/delete", { key: val });
        inp.value = "";
      }
    });
    document.getElementById("avlRandomBtn").addEventListener("click", () => {
      const randVal = Math.floor(Math.random() * 90) + 10;
      this.postAPI("/api/avl/insert", { key: randVal });
    });
    document.getElementById("avlPresetLLBtn").addEventListener("click", async () => {
      await this.postAPI("/api/avl/reset", {});
      await this.postAPI("/api/avl/insert", { key: 30 });
      await this.postAPI("/api/avl/insert", { key: 20 });
      await this.postAPI("/api/avl/insert", { key: 10 }); // triggers LL
    });
    document.getElementById("avlPresetLRBtn").addEventListener("click", async () => {
      await this.postAPI("/api/avl/reset", {});
      await this.postAPI("/api/avl/insert", { key: 30 });
      await this.postAPI("/api/avl/insert", { key: 10 });
      await this.postAPI("/api/avl/insert", { key: 20 }); // triggers LR
    });
    document.getElementById("avlClearBtn").addEventListener("click", () => {
      this.postAPI("/api/avl/reset", {});
    });

    // Graph Events
    document.getElementById("graphBfsBtn").addEventListener("click", () => {
      const start = document.getElementById("graphStartSelect").value;
      this.postAPI("/api/graph/bfs", { start });
    });
    document.getElementById("graphDfsBtn").addEventListener("click", () => {
      const start = document.getElementById("graphStartSelect").value;
      this.postAPI("/api/graph/dfs", { start });
    });
    document.getElementById("graphDijkstraBtn").addEventListener("click", () => {
      const start = document.getElementById("graphStartSelect").value;
      this.postAPI("/api/graph/dijkstra", { start });
    });
    document.getElementById("graphPrimBtn").addEventListener("click", () => {
      const start = document.getElementById("graphStartSelect").value;
      this.postAPI("/api/graph/prim", { start });
    });
    document.getElementById("addNodeBtn").addEventListener("click", () => {
      const node = document.getElementById("newNodeName").value;
      if (node) {
        const x = Math.random() * (this.width - 200) + 100;
        const y = Math.random() * (this.height - 200) + 80;
        this.postAPI("/api/graph/add_node", { node, x, y });
        document.getElementById("newNodeName").value = "";
      }
    });
    document.getElementById("addEdgeBtn").addEventListener("click", () => {
      const u = document.getElementById("edgeU").value;
      const v = document.getElementById("edgeV").value;
      const w = parseFloat(document.getElementById("edgeWeight").value) || 1.0;
      if (u && v) {
        this.postAPI("/api/graph/add_edge", { u, v, weight: w });
      }
    });
    document.getElementById("graphResetBtn").addEventListener("click", () => {
      this.postAPI("/api/graph/reset", {});
    });

    // Hash Table Events
    document.getElementById("hashInsertBtn").addEventListener("click", () => {
      const k = parseInt(document.getElementById("hashKeyInput").value, 10);
      const v = document.getElementById("hashValInput").value || `${k}`;
      if (!isNaN(k)) {
        this.postAPI("/api/hash/insert", { key: k, val: v });
      }
    });
    document.getElementById("hashSearchBtn").addEventListener("click", () => {
      const k = parseInt(document.getElementById("hashSearchInput").value, 10);
      if (!isNaN(k)) {
        this.postAPI("/api/hash/search", { key: k });
      }
    });
    document.getElementById("hashDeleteBtn").addEventListener("click", () => {
      const k = parseInt(document.getElementById("hashDeleteInput").value, 10);
      if (!isNaN(k)) {
        this.postAPI("/api/hash/delete", { key: k });
      }
    });
    document.getElementById("hashCollisionPreset").addEventListener("click", async () => {
      // 10, 17, 24 all have modulo 7 = 3
      await this.postAPI("/api/hash/insert", { key: 10, val: "A" });
      await this.postAPI("/api/hash/insert", { key: 17, val: "B" });
      await this.postAPI("/api/hash/insert", { key: 24, val: "C" });
    });
    document.getElementById("hashResetBtn").addEventListener("click", () => {
      this.postAPI("/api/hash/reset", { capacity: 7 });
    });
  }

  async fetchInitialState() {
    try {
      const res = await fetch("/api/state");
      const data = await res.json();
      this.heapState = data.heap;
      this.avlState = data.avl;
      this.graphState = data.graph;
      this.hashState = data.hash;
      this.populateGraphSelect();
      this.render();
      this.updateDock();
      this.updateMetrics();
    } catch (e) {
      console.warn("Could not load initial state:", e);
    }
  }

  async postAPI(endpoint, payload) {
    try {
      this.pause();
      const res = await fetch(endpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
      const data = await res.json();

      if (data.state) this.heapState = data.state;
      if (data.tree !== undefined) this.avlState = data.tree;
      if (data.graph) {
        this.graphState = data.graph;
        this.populateGraphSelect();
      }
      if (data.table) this.hashState = data.table;

      if (data.trace && data.trace.length > 0) {
        this.loadTrace(data.trace);
      } else {
        this.render();
        this.updateDock();
        this.updateMetrics();
      }
    } catch (err) {
      console.error("API error:", err);
    }
  }

  switchModule(moduleName) {
    this.activeModule = moduleName;
    this.pause();
    this.trace = [];
    this.currentStepIdx = 0;
    this.resetHighlights();

    // Toggle control panels
    document.getElementById("heapControls").classList.toggle("hidden", moduleName !== "heap");
    document.getElementById("avlControls").classList.toggle("hidden", moduleName !== "avl");
    document.getElementById("graphControls").classList.toggle("hidden", moduleName !== "graph");
    document.getElementById("hashControls").classList.toggle("hidden", moduleName !== "hash");

    // Dock titles
    const dockTitle = document.getElementById("dockTitle");
    const dockInfo = document.getElementById("dockInfo");
    if (moduleName === "heap") {
      dockTitle.innerText = "Linear Array Representation (Memory Buffer)";
      dockInfo.innerText = "Simultaneously rendered with logical tree";
    } else if (moduleName === "avl") {
      dockTitle.innerText = "Tree Balance & Node Properties";
      dockInfo.innerText = "Inorder Sequence & Balance Factors";
    } else if (moduleName === "graph") {
      dockTitle.innerText = "Graph Frontier / Traversal State";
      dockInfo.innerText = "Shortest distances / MST weights";
    } else if (moduleName === "hash") {
      dockTitle.innerText = "Bucket Array (Static Storage Buffer)";
      dockInfo.innerText = "Separate Chaining Collision Buckets";
    }

    this.render();
    this.updateDock();
    this.updateMetrics();
  }

  loadTrace(trace) {
    this.trace = trace;
    this.currentStepIdx = 0;
    const scrubber = document.getElementById("traceScrubber");
    scrubber.max = trace.length - 1;
    scrubber.value = 0;
    this.populateTraceLog();
    this.jumpToStep(0);
    this.play();
  }

  play() {
    if (this.trace.length === 0) return;
    this.isPlaying = true;
    document.getElementById("playBtn").classList.add("btn-accent");
    clearInterval(this.playbackTimer);
    this.playbackTimer = setInterval(() => {
      if (this.currentStepIdx < this.trace.length - 1) {
        this.stepForward();
      } else {
        this.pause();
      }
    }, this.speed);
  }

  pause() {
    this.isPlaying = false;
    document.getElementById("playBtn").classList.remove("btn-accent");
    clearInterval(this.playbackTimer);
  }

  stepForward() {
    if (this.currentStepIdx < this.trace.length - 1) {
      this.jumpToStep(this.currentStepIdx + 1);
    }
  }

  stepBackward() {
    if (this.currentStepIdx > 0) {
      this.jumpToStep(this.currentStepIdx - 1);
    }
  }

  jumpToStep(idx) {
    this.currentStepIdx = idx;
    document.getElementById("traceScrubber").value = idx;
    document.getElementById("stepCounter").innerText = `Step ${idx + 1} / ${this.trace.length}`;

    const step = this.trace[idx];
    if (step) {
      this.applyStep(step);
    }
    this.highlightLogStep(idx);
  }

  applyStep(step) {
    // Explainer banner
    document.getElementById("stepTypeBadge").innerText = step.type.toUpperCase();
    document.getElementById("stepDescription").innerText = step.description;

    // Reset temporary highlights
    this.resetHighlights();

    if (step.type === "compare") {
      if (step.idx1 !== undefined) this.activeHighlights.compare = [step.idx1, step.idx2];
      if (step.u && step.v) this.activeHighlights.activeEdge = { u: step.u, v: step.v };
    } else if (step.type === "swap") {
      if (step.idx1 !== undefined) this.activeHighlights.swap = [step.idx1, step.idx2];
    } else if (step.type === "highlight") {
      if (step.indices) this.activeHighlights.compare = step.indices;
      if (step.current) this.activeHighlights.activeNodes = [step.current];
    } else if (step.type === "mst_edge") {
      this.activeHighlights.mstEdges = step.mst_edges || [];
    } else if (step.type === "queue_push" || step.type === "queue_pop") {
      this.activeHighlights.activeNodes = [step.node || step.current];
      this.activeHighlights.visitedNodes = step.visited || [];
      this.renderAuxQueue(step.queue || []);
    } else if (step.type === "stack_push" || step.type === "stack_pop") {
      this.activeHighlights.activeNodes = [step.node || step.current];
      this.activeHighlights.visitedNodes = step.visited || [];
      this.renderAuxStack(step.stack || []);
    } else if (step.type === "relax") {
      this.activeHighlights.activeNodes = [step.current || step.v];
      this.renderDistanceTable(step.distances || {});
    } else if (step.type === "hash_compute" || step.type === "chain_traverse") {
      this.activeHighlights.activeBucket = step.bucket_idx;
      this.activeHighlights.activeChainPos = step.chain_pos;
    }

    // Update snapshots if step carries new data
    if (step.array) this.heapState.array = step.array;
    if (step.tree !== undefined) this.avlState = step.tree;
    if (step.table) this.hashState = step.table;

    this.render();
    this.updateDock();
    this.updateMetrics();
  }

  resetHighlights() {
    this.activeHighlights.compare = [];
    this.activeHighlights.swap = [];
    this.activeHighlights.activeNodes = [];
    this.activeHighlights.activeEdge = null;
    this.activeHighlights.activeBucket = null;
    this.activeHighlights.activeChainPos = null;
  }

  // ==================== RENDERING ENGINE ====================
  render() {
    this.ctx.clearRect(0, 0, this.width, this.height);

    if (this.activeModule === "heap") {
      this.renderHeapTree();
    } else if (this.activeModule === "avl") {
      this.renderAVLTree();
    } else if (this.activeModule === "graph") {
      this.renderGraph();
    } else if (this.activeModule === "hash") {
      this.renderHashTable();
    }
  }

  // 1. Binary Heap Tree Rendering
  renderHeapTree() {
    const arr = this.heapState.array || [];
    if (arr.length === 0) {
      this.renderEmptyNotice("Binary Heap is empty. Insert a value to build heap.");
      return;
    }

    const n = arr.length;
    // Compute tree node coordinates
    const levels = Math.floor(Math.log2(n)) + 1;
    const startY = 70;
    const levelHeight = Math.min(85, (this.height - 120) / Math.max(1, levels));

    // First draw connecting branches
    for (let i = 0; i < n; i++) {
      const left = 2 * i + 1;
      const right = 2 * i + 2;
      const pPos = this.getHeapNodePos(i, n, startY, levelHeight);

      if (left < n) {
        const cPos = this.getHeapNodePos(left, n, startY, levelHeight);
        this.drawBranch(pPos.x, pPos.y, cPos.x, cPos.y);
      }
      if (right < n) {
        const cPos = this.getHeapNodePos(right, n, startY, levelHeight);
        this.drawBranch(pPos.x, pPos.y, cPos.x, cPos.y);
      }
    }

    // Next draw nodes
    for (let i = 0; i < n; i++) {
      const pos = this.getHeapNodePos(i, n, startY, levelHeight);
      let color = "#06b6d4"; // default teal
      if (this.activeHighlights.swap.includes(i)) color = "#f43f5e"; // red
      else if (this.activeHighlights.compare.includes(i)) color = "#facc15"; // yellow

      this.drawNode(pos.x, pos.y, `${arr[i]}`, color, `[${i}]`);
    }
  }

  getHeapNodePos(index, total, startY, levelHeight) {
    const level = Math.floor(Math.log2(index + 1));
    const itemsInLevel = Math.pow(2, level);
    const indexInLevel = index - (itemsInLevel - 1);
    const slotWidth = this.width / (itemsInLevel + 1);
    const x = slotWidth * (indexInLevel + 1);
    const y = startY + level * levelHeight;
    return { x, y };
  }

  // 2. AVL Tree Rendering
  renderAVLTree() {
    if (!this.avlState) {
      this.renderEmptyNotice("AVL Tree is empty. Insert a key to begin.");
      return;
    }

    const tree = this.avlState;
    // Calculate layout with dynamic horizontal spacing based on depth
    const startY = 60;
    const initialSpread = Math.min(this.width * 0.42, 280);

    const drawSubtree = (node, x, y, spread) => {
      if (!node) return;

      const nextSpread = spread * 0.52;
      const nextY = y + 75;

      if (node.left) {
        this.drawBranch(x, y, x - spread, nextY);
        drawSubtree(node.left, x - spread, nextY, nextSpread);
      }
      if (node.right) {
        this.drawBranch(x, y, x + spread, nextY);
        drawSubtree(node.right, x + spread, nextY, nextSpread);
      }

      // Determine balance factor color
      const isImbalanced = Math.abs(node.bf) > 1;
      const nodeColor = isImbalanced ? "#f43f5e" : "#10b981";

      this.drawNode(x, y, `${node.key}`, nodeColor, `BF:${node.bf}`);
    };

    drawSubtree(tree, this.width / 2, startY, initialSpread);
  }

  // 3. Graph Navigator Rendering
  renderGraph() {
    const { nodes, edges, positions } = this.graphState;
    if (!nodes || nodes.length === 0) {
      this.renderEmptyNotice("Graph is empty.");
      return;
    }

    // Draw edges
    edges.forEach(edge => {
      const p1 = positions[edge.u] || { x: 100, y: 100 };
      const p2 = positions[edge.v] || { x: 200, y: 200 };

      const isMst = this.activeHighlights.mstEdges.some(
        e => (e.u === edge.u && e.v === edge.v) || (e.u === edge.v && e.v === edge.u)
      );
      const isActive = this.activeHighlights.activeEdge &&
        ((this.activeHighlights.activeEdge.u === edge.u && this.activeHighlights.activeEdge.v === edge.v) ||
         (this.activeHighlights.activeEdge.u === edge.v && this.activeHighlights.activeEdge.v === edge.u));

      let strokeColor = "#334155";
      let lineWidth = 2;
      if (isMst) {
        strokeColor = "#10b981"; // MST Green
        lineWidth = 4;
      } else if (isActive) {
        strokeColor = "#facc15"; // Exploring edge
        lineWidth = 3;
      }

      this.ctx.beginPath();
      this.ctx.moveTo(p1.x, p1.y);
      this.ctx.lineTo(p2.x, p2.y);
      this.ctx.strokeStyle = strokeColor;
      this.ctx.lineWidth = lineWidth;
      this.ctx.stroke();

      // Draw edge weight badge
      const midX = (p1.x + p2.x) / 2;
      const midY = (p1.y + p2.y) / 2;
      this.drawBadge(midX, midY, `${edge.weight}`, isMst ? "#10b981" : "#475569");
    });

    // Draw graph vertices
    nodes.forEach(node => {
      const pos = positions[node] || { x: 150, y: 150 };
      let color = "#3b82f6";

      if (this.activeHighlights.activeNodes.includes(node)) {
        color = "#facc15"; // active
      } else if (this.activeHighlights.visitedNodes.includes(node)) {
        color = "#8b5cf6"; // visited
      }

      this.drawNode(pos.x, pos.y, node, color, null, 24);
    });
  }

  // 4. Hash Table (Separate Chaining) Rendering
  renderHashTable() {
    const buckets = this.hashState;
    if (!buckets || buckets.length === 0) {
      this.renderEmptyNotice("Hash table empty.");
      return;
    }

    const startX = 80;
    const startY = 50;
    const rowHeight = Math.min(50, (this.height - 80) / buckets.length);

    buckets.forEach((chain, bIdx) => {
      const y = startY + bIdx * rowHeight;
      const isBucketActive = this.activeHighlights.activeBucket === bIdx;

      // Draw Bucket Index Box
      this.ctx.fillStyle = isBucketActive ? "rgba(250, 204, 21, 0.25)" : "rgba(30, 41, 59, 0.9)";
      this.ctx.strokeStyle = isBucketActive ? "#facc15" : "#475569";
      this.ctx.lineWidth = 2;
      this.ctx.fillRect(startX, y - 16, 70, 32);
      this.ctx.strokeRect(startX, y - 16, 70, 32);

      this.ctx.fillStyle = isBucketActive ? "#facc15" : "#f8fafc";
      this.ctx.font = "bold 13px Inter";
      this.ctx.textAlign = "center";
      this.ctx.textBaseline = "middle";
      this.ctx.fillText(`[${bIdx}]`, startX + 35, y);

      // Draw linked chain items
      let currX = startX + 110;
      chain.forEach((item, cPos) => {
        // Draw pointer arrow from previous
        this.ctx.beginPath();
        this.ctx.moveTo(currX - 35, y);
        this.ctx.lineTo(currX - 5, y);
        this.ctx.strokeStyle = "#94a3b8";
        this.ctx.lineWidth = 2;
        this.ctx.stroke();

        // Arrowhead
        this.ctx.beginPath();
        this.ctx.moveTo(currX - 10, y - 4);
        this.ctx.lineTo(currX - 5, y);
        this.ctx.lineTo(currX - 10, y + 4);
        this.ctx.stroke();

        const isNodeActive = isBucketActive && (this.activeHighlights.activeChainPos === cPos);
        const nodeColor = isNodeActive ? "#f43f5e" : "#06b6d4";

        // Draw chain node capsule
        this.ctx.fillStyle = isNodeActive ? "rgba(244, 63, 94, 0.2)" : "rgba(6, 182, 212, 0.15)";
        this.ctx.strokeStyle = nodeColor;
        this.ctx.lineWidth = 2;
        this.ctx.beginPath();
        this.ctx.roundRect(currX, y - 16, 68, 32, 6);
        this.ctx.fill();
        this.ctx.stroke();

        this.ctx.fillStyle = "#fff";
        this.ctx.font = "bold 12px Inter";
        this.ctx.fillText(`${item.key}:${item.value}`, currX + 34, y);

        currX += 95;
      });

      // Draw NULL terminator
      this.ctx.fillStyle = "#64748b";
      this.ctx.font = "11px Fira Code";
      this.ctx.textAlign = "left";
      this.ctx.fillText("→ ∅", currX - 25, y + 1);
    });
  }

  // Common Canvas Drawing Helpers
  drawNode(x, y, label, color, subLabel = null, radius = 22) {
    this.ctx.save();
    this.ctx.beginPath();
    this.ctx.arc(x, y, radius, 0, 2 * Math.PI);
    this.ctx.fillStyle = color;
    this.ctx.shadowColor = "rgba(0,0,0,0.35)";
    this.ctx.shadowBlur = 8;
    this.ctx.shadowOffsetY = 3;
    this.ctx.fill();

    this.ctx.strokeStyle = "#ffffff";
    this.ctx.lineWidth = 2.5;
    this.ctx.stroke();
    this.ctx.restore();

    // Main Label
    this.ctx.fillStyle = "#0f172a";
    this.ctx.font = "bold 13px Inter";
    this.ctx.textAlign = "center";
    this.ctx.textBaseline = "middle";
    this.ctx.fillText(label, x, y);

    // Sub-label (index / BF)
    if (subLabel) {
      this.ctx.fillStyle = "#94a3b8";
      this.ctx.font = "10px Fira Code";
      this.ctx.fillText(subLabel, x, y + radius + 13);
    }
  }

  drawBranch(x1, y1, x2, y2) {
    this.ctx.beginPath();
    this.ctx.moveTo(x1, y1);
    this.ctx.lineTo(x2, y2);
    this.ctx.strokeStyle = "#475569";
    this.ctx.lineWidth = 2;
    this.ctx.stroke();
  }

  drawBadge(x, y, text, bgColor) {
    this.ctx.save();
    this.ctx.fillStyle = bgColor;
    this.ctx.beginPath();
    this.ctx.arc(x, y, 11, 0, 2 * Math.PI);
    this.ctx.fill();
    this.ctx.fillStyle = "#fff";
    this.ctx.font = "bold 11px Inter";
    this.ctx.textAlign = "center";
    this.ctx.textBaseline = "middle";
    this.ctx.fillText(text, x, y);
    this.ctx.restore();
  }

  renderEmptyNotice(msg) {
    this.ctx.fillStyle = "#64748b";
    this.ctx.font = "14px Inter";
    this.ctx.textAlign = "center";
    this.ctx.textBaseline = "middle";
    this.ctx.fillText(msg, this.width / 2, this.height / 2);
  }

  // ==================== DOCK & METRICS UPDATE ====================
  updateDock() {
    const dock = document.getElementById("dockContent");
    dock.innerHTML = "";

    if (this.activeModule === "heap") {
      const arr = this.heapState.array || [];
      if (arr.length === 0) {
        dock.innerHTML = `<span class="empty-state">No elements in heap array.</span>`;
        return;
      }
      arr.forEach((val, idx) => {
        const cell = document.createElement("div");
        cell.className = "array-cell";
        if (this.activeHighlights.swap.includes(idx)) cell.classList.add("highlight-swap");
        else if (this.activeHighlights.compare.includes(idx)) cell.classList.add("highlight-compare");

        cell.innerHTML = `
          <span class="idx">[${idx}]</span>
          <span class="val">${val}</span>
        `;
        dock.appendChild(cell);
      });
    } else if (this.activeModule === "hash") {
      const buckets = this.hashState || [];
      buckets.forEach((chain, idx) => {
        const cell = document.createElement("div");
        cell.className = "array-cell";
        if (this.activeHighlights.activeBucket === idx) cell.classList.add("highlight-compare");
        cell.innerHTML = `
          <span class="idx">B[${idx}]</span>
          <span class="val">${chain.length}</span>
        `;
        dock.appendChild(cell);
      });
    }
  }

  updateMetrics() {
    document.getElementById("metricModule").innerText = this.activeModule.toUpperCase();
    if (this.activeModule === "heap") {
      document.getElementById("metricSize").innerText = (this.heapState.array || []).length;
      document.getElementById("metricAux").innerText = `Mode: ${this.heapState.mode ? this.heapState.mode.toUpperCase() : 'MIN'}`;
    } else if (this.activeModule === "avl") {
      document.getElementById("metricSize").innerText = this.avlState ? "Active Tree" : "0";
      document.getElementById("metricAux").innerText = "AVL Self-Balanced";
    } else if (this.activeModule === "graph") {
      document.getElementById("metricSize").innerText = `${(this.graphState.nodes || []).length} vertices`;
      document.getElementById("metricAux").innerText = `${(this.graphState.edges || []).length} edges`;
    } else if (this.activeModule === "hash") {
      const count = this.hashState.reduce((acc, chain) => acc + chain.length, 0);
      document.getElementById("metricSize").innerText = `${count} keys`;
      document.getElementById("metricAux").innerText = `Cap: ${this.hashState.length}`;
    }
  }

  renderAuxQueue(queue) {
    document.getElementById("auxCardTitle").innerText = "FIFO Queue (BFS Frontier)";
    const container = document.getElementById("auxVisualizer");
    if (!queue || queue.length === 0) {
      container.innerHTML = `<div class="empty-state">Queue is currently empty.</div>`;
      return;
    }
    container.innerHTML = queue.map((node, i) => `
      <div class="aux-item"><span>Slot #${i}</span><strong>${node}</strong></div>
    `).join("");
  }

  renderAuxStack(stack) {
    document.getElementById("auxCardTitle").innerText = "LIFO Stack (DFS Backtracking)";
    const container = document.getElementById("auxVisualizer");
    if (!stack || stack.length === 0) {
      container.innerHTML = `<div class="empty-state">Stack is currently empty.</div>`;
      return;
    }
    container.innerHTML = stack.map((node, i) => `
      <div class="aux-item"><span>Top - ${i}</span><strong>${node}</strong></div>
    `).join("");
  }

  renderDistanceTable(distances) {
    document.getElementById("auxCardTitle").innerText = "Tentative Distances (Dijkstra)";
    const container = document.getElementById("auxVisualizer");
    container.innerHTML = Object.entries(distances).map(([k, d]) => `
      <div class="aux-item"><span>Vertex ${k}</span><strong>${d}</strong></div>
    `).join("");
  }

  populateTraceLog() {
    const logList = document.getElementById("traceLogList");
    logList.innerHTML = "";
    this.trace.forEach((step, idx) => {
      const item = document.createElement("div");
      item.className = "log-entry";
      item.id = `log-step-${idx}`;
      item.innerText = `${idx + 1}. [${step.type}] ${step.description}`;
      item.addEventListener("click", () => {
        this.pause();
        this.jumpToStep(idx);
      });
      logList.appendChild(item);
    });
  }

  highlightLogStep(idx) {
    document.querySelectorAll(".log-entry").forEach(el => el.classList.remove("active-step"));
    const activeEl = document.getElementById(`log-step-${idx}`);
    if (activeEl) {
      activeEl.classList.add("active-step");
      activeEl.scrollIntoView({ block: "nearest", behavior: "smooth" });
    }
  }

  populateGraphSelect() {
    const sel = document.getElementById("graphStartSelect");
    if (!sel) return;
    const currentVal = sel.value;
    sel.innerHTML = "";
    (this.graphState.nodes || []).forEach(node => {
      const opt = document.createElement("option");
      opt.value = node;
      opt.innerText = `Vertex ${node}`;
      sel.appendChild(opt);
    });
    if (currentVal && (this.graphState.nodes || []).includes(currentVal)) {
      sel.value = currentVal;
    }
  }

  toggleHeapMode(mode) {
    this.postAPI("/api/heap/toggle_mode", { mode });
  }
}

// Instantiate visualizer when DOM is ready
window.addEventListener("DOMContentLoaded", () => {
  window.app = new VisualizerApp();
});
