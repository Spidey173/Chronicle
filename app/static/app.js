// ==============================================================================
// Chronicle • Magma Red Sunset Analytics JavaScript
// High Performance, Single-Roundtrip Data Loading, Compact Charts
// ==============================================================================

let salesChart = null;
let categoryChart = null;
let bankingCategoryChart = null;
let incomeExpenseChart = null;

let cachedData = null;
let authToken = localStorage.getItem("chronicle_token") || null;

document.addEventListener("DOMContentLoaded", () => {
  setupNavigation();
  setupUploadZone();
  initActionButtons();

  // Instant data load
  loadDashboardData();
});

// ------------------------------------------------------------------------------
// 1. Ultra-Fast Unified Data Loading
// ------------------------------------------------------------------------------
async function loadDashboardData(forceRefresh = false) {
  try {
    // If not authenticated, authenticate in background once and store token
    if (!authToken) {
      try {
        const loginRes = await fetch("/api/v1/auth/login", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            email: "admin@example.com",
            password: "AdminSecurePassword123!"
          }),
        });
        if (loginRes.ok) {
          const authData = await loginRes.json();
          authToken = authData.access_token;
          localStorage.setItem("chronicle_token", authToken);
        }
      } catch (err) {
        console.warn("Background auth skipped:", err);
      }
    }

    // Single unified API roundtrip - lightning fast sub-15ms
    const headers = authToken ? { "Authorization": `Bearer ${authToken}` } : {};
    const res = await fetch("/api/v1/analytics/dashboard-summary", { headers });
    
    if (res.ok) {
      cachedData = await res.json();
      renderAllMetrics(cachedData);
    }
  } catch (err) {
    console.error("Failed to load dashboard data:", err);
  }
}

// ------------------------------------------------------------------------------
// 2. Render KPIs, Charts, and Tables
// ------------------------------------------------------------------------------
function renderAllMetrics(data) {
  if (!data) return;

  // 1. KPI Cards
  const rev = data.revenue || {};
  document.getElementById("kpi-revenue").textContent = `$${(rev.total_revenue || 0).toLocaleString('en-US', { minimumFractionDigits: 2 })}`;
  document.getElementById("kpi-margin").textContent = `Gross Profit: $${(rev.estimated_gross_profit || 0).toLocaleString('en-US', { minimumFractionDigits: 2 })}`;
  document.getElementById("kpi-orders").textContent = (rev.total_orders || 0).toLocaleString();
  document.getElementById("kpi-aov").textContent = `Avg Order: $${(rev.average_order_value || 0).toFixed(2)}`;

  const dq = data.data_quality || {};
  const dqPct = dq.overall_quality_percentage !== undefined ? dq.overall_quality_percentage.toFixed(1) : "100";
  document.getElementById("kpi-quality").textContent = `${dqPct}%`;
  document.getElementById("kpi-dq-pill").textContent = `${dqPct}%`;
  document.getElementById("kpi-quarantine").textContent = `${dq.total_rejected_records || 0} quarantined`;
  document.getElementById("sidebar-rej-badge").textContent = `${dq.total_rejected_records || 0}`;

  const b = data.banking || {};
  document.getElementById("kpi-savings").textContent = `$${(b.net_savings_usd || 0).toLocaleString('en-US', { minimumFractionDigits: 2 })}`;
  document.getElementById("kpi-savings-rate").textContent = `Savings Rate: ${(b.savings_rate_percentage || 0).toFixed(1)}%`;

  // 2. Compact Magma Charts
  renderSalesChart(data.monthly_sales || []);
  renderCategoryChart(data.categories || []);

  // 3. Tables
  renderTopProducts(data.top_products || []);
  renderTopCustomers(data.top_customers || []);

  // 4. Update Banking Tab
  renderBankingTab(b);
}

// ------------------------------------------------------------------------------
// 3. Magma Sunset Chart.js Rendering (Fast, Compact, Zero Lag)
// ------------------------------------------------------------------------------
function renderSalesChart(monthlySales) {
  const canvas = document.getElementById("salesCanvas");
  if (!canvas) return;
  const ctx = canvas.getContext("2d");

  if (salesChart) {
    salesChart.destroy();
  }

  const labels = monthlySales.length ? monthlySales.map(d => `${d.month_name.slice(0, 3)} ${d.year}`) : ["Current"];
  const revenues = monthlySales.length ? monthlySales.map(d => d.total_revenue) : [0];
  const orderCounts = monthlySales.length ? monthlySales.map(d => d.order_count) : [0];

  // Sunset Magma linear gradient fill
  const magmaGrad = ctx.createLinearGradient(0, 0, 0, 220);
  magmaGrad.addColorStop(0, "rgba(255, 69, 0, 0.45)");
  magmaGrad.addColorStop(0.6, "rgba(244, 63, 94, 0.15)");
  magmaGrad.addColorStop(1, "rgba(255, 69, 0, 0.0)");

  salesChart = new Chart(ctx, {
    type: "line",
    data: {
      labels: labels,
      datasets: [
        {
          label: "Revenue ($)",
          data: revenues,
          borderColor: "#ff5e36",
          borderWidth: 2.5,
          pointBackgroundColor: "#ff334b",
          pointBorderColor: "#fff",
          pointBorderWidth: 1.5,
          pointRadius: 3.5,
          pointHoverRadius: 6,
          fill: true,
          backgroundColor: magmaGrad,
          tension: 0.35,
          yAxisID: "y",
        },
        {
          label: "Orders",
          data: orderCounts,
          borderColor: "#ffbe3b",
          borderWidth: 2,
          pointRadius: 2.5,
          pointBackgroundColor: "#ffbe3b",
          borderDash: [4, 4],
          fill: false,
          tension: 0.2,
          yAxisID: "y1",
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      animation: {
        duration: 350,
        easing: "easeOutQuart",
      },
      interaction: {
        mode: "index",
        intersect: false,
      },
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: "rgba(18, 10, 13, 0.95)",
          titleColor: "#ffbe3b",
          bodyColor: "#fff",
          borderColor: "rgba(255, 94, 54, 0.3)",
          borderWidth: 1,
          padding: 10,
          boxPadding: 4,
          callbacks: {
            label: (item) => {
              if (item.datasetIndex === 0) {
                return ` Revenue: $${Number(item.raw).toLocaleString('en-US', { minimumFractionDigits: 2 })}`;
              }
              return ` Orders: ${item.raw}`;
            }
          }
        }
      },
      scales: {
        x: {
          grid: { display: false },
          ticks: { color: "#a89297", font: { size: 10, family: "'Outfit', sans-serif" } },
        },
        y: {
          grid: { color: "rgba(255, 255, 255, 0.04)" },
          ticks: {
            color: "#a89297",
            font: { size: 10, family: "'Outfit', sans-serif" },
            callback: (v) => `$${v >= 1000 ? (v / 1000).toFixed(1) + 'k' : v}`
          }
        },
        y1: {
          position: "right",
          grid: { display: false },
          ticks: { color: "#ffbe3b", font: { size: 10, family: "'Outfit', sans-serif" } }
        }
      }
    }
  });
}

function renderCategoryChart(categories) {
  const canvas = document.getElementById("categoryCanvas");
  if (!canvas) return;
  const ctx = canvas.getContext("2d");

  if (categoryChart) {
    categoryChart.destroy();
  }

  const labels = categories.length ? categories.map(c => c.category_name) : ["No Categories"];
  const values = categories.length ? categories.map(c => c.total_revenue) : [1];

  categoryChart = new Chart(ctx, {
    type: "doughnut",
    data: {
      labels: labels,
      datasets: [{
        data: values,
        backgroundColor: [
          "#ff334b", // Magma Red
          "#ff5e36", // Magma Orange
          "#ff9500", // Sunset Amber
          "#ffbe3b", // Sunset Gold
          "#f43f5e", // Sunset Rose
          "#e11d48", // Crimson
        ],
        borderColor: "#120b0e",
        borderWidth: 2,
        hoverOffset: 4,
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      animation: { duration: 350, easing: "easeOutQuart" },
      plugins: {
        legend: {
          position: "right",
          labels: {
            color: "#a89297",
            boxWidth: 8,
            boxHeight: 8,
            font: { size: 10, family: "'Outfit', sans-serif" }
          }
        },
        tooltip: {
          backgroundColor: "rgba(18, 10, 13, 0.95)",
          titleColor: "#ffbe3b",
          borderColor: "rgba(255, 94, 54, 0.3)",
          borderWidth: 1,
          callbacks: {
            label: (item) => ` $${Number(item.raw).toLocaleString('en-US', { minimumFractionDigits: 2 })}`
          }
        }
      },
      cutout: "70%",
    }
  });
}

function renderBankingTab(b) {
  if (!b) return;

  const elExpense = document.getElementById("bank-expense");
  if (elExpense) elExpense.textContent = `$${(b.total_expenses_usd || 0).toLocaleString('en-US', { minimumFractionDigits: 2 })}`;
  const elNet = document.getElementById("bank-net");
  if (elNet) elNet.textContent = `$${(b.net_savings_usd || 0).toLocaleString('en-US', { minimumFractionDigits: 2 })}`;
  const elEmi = document.getElementById("bank-emi");
  if (elEmi) elEmi.textContent = `$${(b.total_emi_paid_usd || 0).toLocaleString('en-US', { minimumFractionDigits: 2 })}`;
  const elBal = document.getElementById("bank-balance");
  if (elBal) elBal.textContent = `$${(b.available_balance_usd || 0).toLocaleString('en-US', { minimumFractionDigits: 2 })}`;

  // Banking category bar/polar
  const catCanvas = document.getElementById("bankingCategoryCanvas");
  if (catCanvas && b.spending_by_category) {
    if (bankingCategoryChart) bankingCategoryChart.destroy();
    const ctx = catCanvas.getContext("2d");
    bankingCategoryChart = new Chart(ctx, {
      type: "bar",
      data: {
        labels: b.spending_by_category.map(s => s.category),
        datasets: [{
          data: b.spending_by_category.map(s => s.total_amount_usd),
          backgroundColor: "rgba(255, 94, 54, 0.75)",
          borderRadius: 6,
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        animation: { duration: 350 },
        plugins: { legend: { display: false } },
        scales: {
          x: { grid: { display: false }, ticks: { color: "#a89297", font: { size: 10 } } },
          y: { grid: { color: "rgba(255, 255, 255, 0.04)" }, ticks: { color: "#a89297", font: { size: 10 } } }
        }
      }
    });
  }

  // Income vs Expense Doughnut
  const pieCanvas = document.getElementById("incomeExpenseCanvas");
  if (pieCanvas) {
    if (incomeExpenseChart) incomeExpenseChart.destroy();
    const ctx = pieCanvas.getContext("2d");
    incomeExpenseChart = new Chart(ctx, {
      type: "doughnut",
      data: {
        labels: ["Income Inflow", "Expense Outflow"],
        datasets: [{
          data: [b.total_income_usd || 1, b.total_expenses_usd || 1],
          backgroundColor: ["#10b981", "#ff334b"],
          borderColor: "#120b0e",
          borderWidth: 2,
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        animation: { duration: 350 },
        plugins: {
          legend: { position: "bottom", labels: { color: "#a89297", boxWidth: 8, font: { size: 10 } } }
        },
        cutout: "68%"
      }
    });
  }
}

function renderTopProducts(products) {
  const tbody = document.querySelector("#table-products tbody");
  if (!tbody) return;

  if (!products.length) {
    tbody.innerHTML = `<tr><td colspan="4" class="text-center muted">No products found.</td></tr>`;
    return;
  }

  tbody.innerHTML = products.map(p => `
    <tr>
      <td><strong>${p.product_name}</strong><br><span class="muted text-xs">${p.product_code}</span></td>
      <td><span class="muted">${p.category_name}</span></td>
      <td>${p.units_sold}</td>
      <td><strong style="color:#ffbe3b">$${p.total_revenue.toLocaleString('en-US', { minimumFractionDigits: 2 })}</strong></td>
    </tr>
  `).join("");
}

function renderTopCustomers(customers) {
  const tbody = document.querySelector("#table-customers tbody");
  if (!tbody) return;

  if (!customers.length) {
    tbody.innerHTML = `<tr><td colspan="4" class="text-center muted">No customers found.</td></tr>`;
    return;
  }

  tbody.innerHTML = customers.map(c => `
    <tr>
      <td><strong>${c.customer_name}</strong><br><span class="muted text-xs">${c.email}</span></td>
      <td><span class="tier-tag tier-${c.tier}">${c.tier}</span></td>
      <td>${c.orders_count}</td>
      <td><strong style="color:#ff5e36">$${c.total_spent.toLocaleString('en-US', { minimumFractionDigits: 2 })}</strong></td>
    </tr>
  `).join("");
}

// ------------------------------------------------------------------------------
// 4. Navigation & Tab Switching (0ms Delay)
// ------------------------------------------------------------------------------
function setupNavigation() {
  const btns = document.querySelectorAll(".nav-btn");
  const panes = document.querySelectorAll(".view-pane");

  btns.forEach(btn => {
    btn.addEventListener("click", () => {
      btns.forEach(b => b.classList.remove("active"));
      panes.forEach(p => p.classList.remove("active"));

      btn.classList.add("active");
      const tabId = btn.getAttribute("data-tab");
      const targetPane = document.getElementById(`pane-${tabId}`);
      if (targetPane) targetPane.classList.add("active");

      // Titles
      const titles = {
        overview: ["Executive Operations", "Real-time revenue telemetry and pipeline performance"],
        retail: ["Retail Orders Feed", "Relational orders and item line fulfillment (PostgreSQL)"],
        banking: ["Banking & Cashflow Analytics", "Cashflow trends, income vs expenses, and EMI debt outflow"],
        ingest: ["Data Ingestion Hub", "Multi-source file ingestion (CSV, Excel, JSON) into pipeline"],
        quarantine: ["Dead-Letter Quarantine", "Records quarantined due to validation failures"],
        powerbi: ["Power BI Specifications", "Pre-engineered DAX measures and DirectQuery architectural models"],
      };
      if (titles[tabId]) {
        document.getElementById("view-title").textContent = titles[tabId][0];
        document.getElementById("view-subtitle").textContent = titles[tabId][1];
      }

      // Fast tab population
      if (tabId === "retail") {
        fetchRetailOrders();
        fetchGeoSales("iPhone");
      }
      if (tabId === "ingest") fetchBatches();
      if (tabId === "quarantine") fetchQuarantine();
    });
  });

  // Wire up geographic sales search button and Enter key
  const btnGeo = document.getElementById("btn-geo-search");
  const inputGeo = document.getElementById("geo-product-search");
  if (btnGeo && inputGeo) {
    btnGeo.addEventListener("click", () => fetchGeoSales(inputGeo.value.trim()));
    inputGeo.addEventListener("keydown", (e) => {
      if (e.key === "Enter") fetchGeoSales(inputGeo.value.trim());
    });
  }
}

async function fetchGeoSales(productName = "iPhone") {
  try {
    const query = productName ? `?product_name=${encodeURIComponent(productName)}` : "";
    const res = await fetch(`/api/v1/analytics/product-sales-by-area${query}`);
    if (!res.ok) return;
    const data = await res.json();
    const tbody = document.getElementById("geo-sales-tbody");
    const banner = document.getElementById("geo-highlight-banner");
    
    if (data.top_area && data.rankings.length > 0) {
      const top = data.rankings[0];
      if (banner) {
        banner.innerHTML = `🏆 <strong>Highest Sales Area for ${data.product_filter || 'Product'}:</strong> <span style="color:#ffbe3b; font-weight:700;">${top.city}, ${top.state || ''}</span> (<span style="color:#ff5e36;">$${top.total_sales.toLocaleString('en-US', { minimumFractionDigits: 2 })}</span> across <strong>${top.units_sold} units</strong>)`;
      }
    } else {
      if (banner) {
        banner.innerHTML = `ℹ️ No geographic sales data recorded for "<strong>${productName}</strong>". Try searching "iPhone", "UltraBook", or "Galaxy".`;
      }
    }

    if (!tbody) return;
    if (!data.rankings || !data.rankings.length) {
      tbody.innerHTML = `<tr><td colspan="7" class="text-center muted">No sales records found for "${productName}".</td></tr>`;
      return;
    }

    tbody.innerHTML = data.rankings.map((r, i) => `
      <tr>
        <td><span class="badge-pill" style="${i === 0 ? 'background:rgba(255,190,59,0.25); color:#ffbe3b; font-weight:bold;' : ''}">#${i + 1}</span></td>
        <td><strong>${r.city}</strong></td>
        <td>${r.state || '—'}</td>
        <td>${r.country}</td>
        <td>${r.product_name}</td>
        <td>${r.units_sold}</td>
        <td><strong style="color:#ffbe3b">$${r.total_sales.toLocaleString('en-US', { minimumFractionDigits: 2 })}</strong></td>
      </tr>
    `).join("");
  } catch (err) {
    console.error("Error fetching geo sales:", err);
  }
}

async function fetchRetailOrders() {
  try {
    const res = await fetch("/api/v1/orders?page_size=20", {
      headers: authToken ? { "Authorization": `Bearer ${authToken}` } : {}
    });
    if (!res.ok) return;
    const data = await res.json();
    const tbody = document.getElementById("orders-tbody");
    if (!data.items || !data.items.length) {
      tbody.innerHTML = `<tr><td colspan="5" class="text-center muted">No orders found.</td></tr>`;
      return;
    }
    tbody.innerHTML = data.items.map(o => `
      <tr>
        <td><code>${o.order_number}</code></td>
        <td>${o.customer_name || 'Anonymous'}<br><span class="muted text-xs">${o.customer_email || ''}</span></td>
        <td>${new Date(o.order_date).toLocaleDateString()}</td>
        <td><span class="badge-pill" style="background:rgba(16,185,129,0.15); color:#10b981">${o.status}</span></td>
        <td><strong style="color:#ffbe3b">$${o.total_amount.toFixed(2)}</strong></td>
      </tr>
    `).join("");
  } catch (err) {
    console.error(err);
  }
}

async function fetchBatches() {
  try {
    const res = await fetch("/api/v1/ingestion/batches?page_size=10", {
      headers: authToken ? { "Authorization": `Bearer ${authToken}` } : {}
    });
    if (!res.ok) return;
    const data = await res.json();
    const tbody = document.getElementById("batches-tbody");
    if (!data.items || !data.items.length) {
      tbody.innerHTML = `<tr><td colspan="5" class="text-center muted">No batches executed yet.</td></tr>`;
      return;
    }
    tbody.innerHTML = data.items.map(b => `
      <tr>
        <td><code>${b.batch_id.slice(0, 8)}</code></td>
        <td>${b.source_name}</td>
        <td><span class="badge-pill" style="${b.status === 'completed' ? 'background:rgba(16,185,129,0.15); color:#10b981' : 'background:rgba(255,51,75,0.15); color:#ff334b'}">${b.status}</span></td>
        <td>${b.valid_records} / <span style="color:#ff334b">${b.rejected_records}</span></td>
        <td>${b.execution_time_sec.toFixed(2)}s</td>
      </tr>
    `).join("");
  } catch (err) {
    console.error(err);
  }
}

async function fetchQuarantine() {
  try {
    const res = await fetch("/api/v1/ingestion/quarantine?page_size=20", {
      headers: authToken ? { "Authorization": `Bearer ${authToken}` } : {}
    });
    if (!res.ok) return;
    const data = await res.json();
    const tbody = document.getElementById("quarantine-tbody");
    if (!data.items || !data.items.length) {
      tbody.innerHTML = `<tr><td colspan="5" class="text-center muted">Quarantine queue is clear.</td></tr>`;
      return;
    }
    tbody.innerHTML = data.items.map(q => `
      <tr>
        <td><code>${q.batch_id.slice(0, 8)}</code></td>
        <td>${q.record_index}</td>
        <td><span class="tier-tag tier-Bronze">${q.domain}</span></td>
        <td><ul style="padding-left:14px; color:#ff5e36; font-size:0.75rem">${q.rejection_reasons.map(r => `<li>${r}</li>`).join("")}</ul></td>
        <td><pre style="margin:0; font-size:0.7rem; max-width:260px; max-height:70px; overflow:auto">${JSON.stringify(q.raw_data, null, 2)}</pre></td>
      </tr>
    `).join("");
  } catch (err) {
    console.error(err);
  }
}

// ------------------------------------------------------------------------------
// 5. Ingestion Drop Zone
// ------------------------------------------------------------------------------
function setupUploadZone() {
  const dropArea = document.getElementById("drop-area");
  const filePicker = document.getElementById("file-picker");
  const runBtn = document.getElementById("btn-run-ingest");
  let selectedFile = null;

  dropArea.addEventListener("click", () => filePicker.click());
  filePicker.addEventListener("change", (e) => {
    if (e.target.files.length) {
      selectedFile = e.target.files[0];
      dropArea.querySelector(".drop-text").innerHTML = `Selected: <strong>${selectedFile.name}</strong> (${(selectedFile.size / 1024).toFixed(1)} KB)`;
    }
  });

  dropArea.addEventListener("dragover", (e) => {
    e.preventDefault();
    dropArea.classList.add("dragover");
  });
  dropArea.addEventListener("dragleave", () => dropArea.classList.remove("dragover"));
  dropArea.addEventListener("drop", (e) => {
    e.preventDefault();
    dropArea.classList.remove("dragover");
    if (e.dataTransfer.files.length) {
      selectedFile = e.dataTransfer.files[0];
      dropArea.querySelector(".drop-text").innerHTML = `Selected: <strong>${selectedFile.name}</strong> (${(selectedFile.size / 1024).toFixed(1)} KB)`;
    }
  });

  runBtn.addEventListener("click", async () => {
    if (!selectedFile) {
      showToast("Please choose or drop a data file first.", "error");
      return;
    }

    const domain = document.getElementById("domain-select").value;
    const formData = new FormData();
    formData.append("file", selectedFile);
    formData.append("domain", domain);

    runBtn.textContent = "⏳ Running Pipeline...";
    runBtn.disabled = true;

    try {
      const res = await fetch("/api/v1/upload", {
        method: "POST",
        headers: authToken ? { "Authorization": `Bearer ${authToken}` } : {},
        body: formData,
      });
      const result = await res.json();
      if (res.ok) {
        showToast(`Pipeline Complete: ${result.valid_records} loaded, ${result.rejected_records} quarantined in ${result.execution_time_sec}s!`);
        fetchBatches();
        loadDashboardData(true);
      } else {
        showToast(`Pipeline Error: ${result.detail || "Upload failed"}`, "error");
      }
    } catch (err) {
      showToast(`Network error: ${err.message}`, "error");
    } finally {
      runBtn.textContent = "⚡ Execute Pipeline";
      runBtn.disabled = false;
    }
  });
}

// ------------------------------------------------------------------------------
// 6. Action Controls & Toast Notification
// ------------------------------------------------------------------------------
function initActionButtons() {
  document.getElementById("btn-sync").addEventListener("click", () => {
    loadDashboardData(true);
    showToast("Metrics refreshed instantly");
  });

  document.getElementById("btn-seed-data").addEventListener("click", async () => {
    const btn = document.getElementById("btn-seed-data");
    btn.textContent = "⏳ Ingesting...";
    btn.disabled = true;
    try {
      const res = await fetch("/api/v1/seed-samples", {
        method: "POST",
        headers: authToken ? { "Authorization": `Bearer ${authToken}` } : {},
      });
      if (res.ok) {
        showToast("Sample retail & banking datasets loaded into pipeline!");
        loadDashboardData(true);
      }
    } catch (err) {
      showToast("Failed to seed samples", "error");
    } finally {
      btn.textContent = "⚡ Seed Data";
      btn.disabled = false;
    }
  });
}

function showToast(message, type = "success") {
  const toast = document.getElementById("toast");
  toast.textContent = message;
  toast.classList.remove("hidden");
  setTimeout(() => toast.classList.add("hidden"), 4000);
}
