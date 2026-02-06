(function () {
  const btnStartCapture = document.getElementById("btnStartCapture");
  const btnImportPcap = document.getElementById("btnImportPcap");
  const inputPcapFile = document.getElementById("inputPcapFile");
  const btnCancelCapture = document.getElementById("btnCancelCapture");
  const btnConfirmCapture = document.getElementById("btnConfirmCapture");
  const btnSearch = document.getElementById("btnSearch");
  const modalOverlay = document.getElementById("modalOverlay");
  const durationMinutes = document.getElementById("durationMinutes");
  const interfaceSelect = document.getElementById("interfaceSelect");
  const timerSection = document.getElementById("timerSection");
  const timerValue = document.getElementById("timerValue");
  const timerStatus = document.getElementById("timerStatus");
  const timerSummary = document.getElementById("timerSummary");
  const graphPlaceholder = document.getElementById("graphPlaceholder");
  const networkGraphEl = document.getElementById("networkGraph");
  const searchInput = document.getElementById("searchInput");

  let network = null;
  let nodesDataset = null;
  let edgesDataset = null;
  let countdownInterval = null;
  let currentJobId = null;
  let countdownEnd = 0;

  function showModal() {
    modalOverlay.classList.remove("hidden");
    loadInterfaces();
  }

  function hideModal() {
    modalOverlay.classList.add("hidden");
  }

  async function loadInterfaces() {
    try {
      const r = await fetch("/api/interfaces");
      const list = await r.json();
      interfaceSelect.innerHTML = '<option value="">Default (first interface)</option>';
      list.forEach((iface) => {
        const opt = document.createElement("option");
        opt.value = iface.number;
        opt.textContent = iface.label.length > 55 ? iface.label.slice(0, 52) + "…" : iface.label;
        interfaceSelect.appendChild(opt);
      });
    } catch (e) {
      console.warn("Could not load interfaces", e);
    }
  }

  function formatTime(seconds) {
    const m = Math.floor(seconds / 60);
    const s = seconds % 60;
    return m + ":" + String(s).padStart(2, "0");
  }

  function startCountdown(totalSeconds) {
    countdownEnd = Date.now() + totalSeconds * 1000;
    timerSection.classList.remove("hidden");
    timerSummary.classList.add("hidden");
    timerSummary.textContent = "";
    timerStatus.textContent = "Capturing…";

    function tick() {
      const left = Math.max(0, Math.ceil((countdownEnd - Date.now()) / 1000));
      timerValue.textContent = formatTime(left);
      if (left <= 0) {
        clearInterval(countdownInterval);
        countdownInterval = null;
        timerStatus.textContent = "Processing PCAP…";
      }
    }
    tick();
    countdownInterval = setInterval(tick, 500);
  }

  function stopCountdown() {
    if (countdownInterval) {
      clearInterval(countdownInterval);
      countdownInterval = null;
    }
    timerSection.classList.add("hidden");
    timerSummary.classList.add("hidden");
  }

  async function pollUntilDone(jobId) {
    const maxWait = 120000; // 2 min
    const start = Date.now();
    while (Date.now() - start < maxWait) {
      const r = await fetch("/api/capture/status/" + jobId);
      const data = await r.json();
      if (data.status === "completed") {
        stopCountdown();
        return data;
      }
      if (data.status === "error") {
        stopCountdown();
        timerStatus.textContent = "Error: " + (data.error || "Unknown");
        setTimeout(() => stopCountdown(), 3000);
        throw new Error(data.error || "Capture failed");
      }
      await new Promise((res) => setTimeout(res, 1000));
    }
    stopCountdown();
    throw new Error("Capture timed out");
  }

  function drawGraph(nodes, edges) {
    graphPlaceholder.classList.add("hidden");
    networkGraphEl.classList.remove("hidden");

    const container = networkGraphEl;
    const options = {
      nodes: {
        shape: "box",
        font: { color: "#e6edf3", size: 14 },
        borderWidth: 2,
        color: { background: "#1a2332", border: "#58a6ff" },
        margin: 10,
      },
      edges: {
        color: { color: "#58a6ff" },
        width: 2,
        arrows: {
          to: {
            enabled: true,
            scaleFactor: 1.2,
          },
        },
        font: {
          color: "#8b949e",
          size: 12,
          background: "rgba(26,35,50,0.9)",
          strokeWidth: 2,
          align: "middle",
        },
        smooth: { type: "cubicBezier", roundness: 0.2 },
      },
      physics: {
        enabled: true,
        solver: "forceAtlas2Based",
        forceAtlas2Based: {
          gravitationalConstant: -50,
          centralGravity: 0.01,
          springLength: 150,
          springConstant: 0.08,
        },
      },
      interaction: { hover: true },
    };

    const visNodes = nodes.map((n) => ({ id: n.id, label: n.label }));
    const visEdges = edges.map((e, i) => ({
      id: "e" + i,
      from: e.from,
      to: e.to,
      label: "SRC → DST",
      title: e.title || (e.from + " → " + e.to),
    }));

    if (!nodesDataset) {
      nodesDataset = new vis.DataSet(visNodes);
      edgesDataset = new vis.DataSet(visEdges);
      const data = { nodes: nodesDataset, edges: edgesDataset };
      network = new vis.Network(container, data, options);
    } else {
      nodesDataset.clear();
      edgesDataset.clear();
      nodesDataset.add(visNodes);
      edgesDataset.add(visEdges);
    }
  }

  function searchAndHighlight(query) {
    if (!network || !nodesDataset) return;
    const q = (query || "").trim().toLowerCase();
    const ids = nodesDataset.getIds();
    const matchIds = q
      ? ids.filter((id) => String(id).toLowerCase().includes(q))
      : [];

    nodesDataset.forEach((node) => {
      const match = matchIds.includes(node.id);
      nodesDataset.update({
        id: node.id,
        font: {
          color: "#e6edf3",
          size: 14,
          face: "sans-serif",
          bold: match,
        },
        color: {
          background: match ? "#2d1f1f" : "#1a2332",
          border: match ? "#f85149" : "#58a6ff",
        },
        borderWidth: match ? 3 : 2,
      });
    });

    if (matchIds.length === 1) {
      network.focus(matchIds[0], { scale: 1.2, animation: true });
    } else if (matchIds.length > 0) {
      network.fit({ nodes: matchIds, animation: true });
    }
  }

  btnStartCapture.addEventListener("click", showModal);

  btnImportPcap.addEventListener("click", () => {
    inputPcapFile.value = "";
    inputPcapFile.click();
  });

  inputPcapFile.addEventListener("change", async () => {
    const file = inputPcapFile.files && inputPcapFile.files[0];
    if (!file) return;
    timerSection.classList.remove("hidden");
    timerValue.textContent = "—";
    timerSummary.classList.add("hidden");
    timerStatus.textContent = "Parsing PCAP file…";
    try {
      const form = new FormData();
      form.append("file", file);
      const r = await fetch("/api/import-pcap", {
        method: "POST",
        body: form,
      });
      const result = await r.json();
      if (!r.ok) throw new Error(result.error || "Import failed");
      const hostCount = result.host_count ?? result.nodes.length;
      const connCount = result.connection_count ?? result.edges.length;
      timerStatus.textContent = "Parsing complete.";
      timerSummary.classList.remove("hidden");
      timerSummary.textContent =
        `${hostCount} host(s), ${connCount} connection(s) — map updated below.`;
      if (hostCount === 0) {
        graphPlaceholder.classList.remove("hidden");
        graphPlaceholder.textContent =
          "No IP addresses found in file. Try a different PCAP.";
        networkGraphEl.classList.add("hidden");
        if (nodesDataset) {
          nodesDataset.clear();
          edgesDataset.clear();
        }
      } else {
        drawGraph(result.nodes, result.edges);
      }
      setTimeout(stopCountdown, 4000);
    } catch (e) {
      console.error(e);
      timerStatus.textContent = "Error: " + (e.message || "Import failed");
      setTimeout(stopCountdown, 3000);
      alert("Error: " + (e.message || "Import failed"));
    }
  });

  btnCancelCapture.addEventListener("click", () => {
    hideModal();
  });

  btnConfirmCapture.addEventListener("click", async () => {
    const minutes = Math.max(1, Math.min(60, parseInt(durationMinutes.value, 10) || 2));
    const durationSeconds = minutes * 60;
    const interfaceVal = interfaceSelect.value || null;
    hideModal();

    try {
      const r = await fetch("/api/capture/start", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          duration_seconds: durationSeconds,
          interface: interfaceVal,
        }),
      });
      const data = await r.json();
      if (!r.ok) throw new Error(data.error || "Failed to start");
      currentJobId = data.job_id;
      startCountdown(data.duration_seconds);
      await pollUntilDone(data.job_id);
      const res = await fetch("/api/capture/result/" + data.job_id);
      const result = await res.json();
      if (!res.ok) throw new Error(result.error || "No result");

      const hostCount = result.host_count ?? result.nodes.length;
      const connCount = result.connection_count ?? result.edges.length;
      timerStatus.textContent = "Parsing complete.";
      timerSummary.classList.remove("hidden");
      timerSummary.textContent = result.parsed
        ? `${hostCount} host(s), ${connCount} connection(s) — map updated below.`
        : "Map updated below.";

      if (hostCount === 0) {
        graphPlaceholder.classList.remove("hidden");
        graphPlaceholder.textContent =
          "No IP addresses found in capture. Try a longer duration or ensure there is traffic (e.g. browse or ping).";
        networkGraphEl.classList.add("hidden");
        if (nodesDataset) {
          nodesDataset.clear();
          edgesDataset.clear();
        }
      } else {
        drawGraph(result.nodes, result.edges);
      }
      setTimeout(stopCountdown, 4000);
    } catch (e) {
      console.error(e);
      alert("Error: " + (e.message || "Capture failed. Is tshark installed and are you running as Administrator?"));
    }
  });

  btnSearch.addEventListener("click", () => {
    searchAndHighlight(searchInput.value);
  });

  searchInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter") searchAndHighlight(searchInput.value);
  });

  searchInput.addEventListener("input", () => {
    if (searchInput.value.trim() === "") searchAndHighlight("");
  });
})();
