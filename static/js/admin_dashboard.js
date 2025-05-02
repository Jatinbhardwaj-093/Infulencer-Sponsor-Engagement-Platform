/**
 * Admin Dashboard JavaScript
 * Enhances the admin dashboard with interactive features
 * For Influencer Engagement Platform
 */

document.addEventListener("DOMContentLoaded", function () {
  // Initialize all components
  initializeDataTables();
  initializeCharts();
  setupActionHandlers();
  initializeThemeToggle();
  setupExportFunctions();
  initializeCounters();
  setupNotifications();
  initializeTabNavigation(); // Add this line to initialize tab navigation

  // Show dashboard is ready
  showToast("Dashboard loaded successfully", "success");
});

/**
 * Initialize DataTables for better table management
 */
function initializeDataTables() {
  const tables = document.querySelectorAll(".data-table");

  tables.forEach((table) => {
    const tableId = table.id;
    const dataTable = new DataTable(`#${tableId}`, {
      responsive: true,
      pageLength: 10,
      lengthMenu: [5, 10, 25, 50],
      dom: "Bfrtip",
      buttons: ["copy", "csv", "excel", "pdf"],
      language: {
        search: "Filter records:",
        zeroRecords: "No matching records found",
        info: "Showing _START_ to _END_ of _TOTAL_ entries",
        infoEmpty: "Showing 0 to 0 of 0 entries",
      },
      initComplete: function () {
        // Add custom filter inputs for specific columns
        this.api()
          .columns()
          .every(function () {
            const column = this;
            if ($(column.header()).hasClass("filterable")) {
              const title = $(column.header()).text();
              const select = $(
                '<select class="form-select form-select-sm"><option value="">All ' +
                  title +
                  "</option></select>"
              )
                .appendTo($(column.footer()).empty())
                .on("change", function () {
                  const val = $.fn.dataTable.util.escapeRegex($(this).val());
                  column.search(val ? "^" + val + "$" : "", true, false).draw();
                });

              column
                .data()
                .unique()
                .sort()
                .each(function (d, j) {
                  if (d) {
                    select.append(
                      '<option value="' + d + '">' + d + "</option>"
                    );
                  }
                });
            }
          });
      },
    });

    // Add search functionality to each table
    const searchInput = document.querySelector(`#search-${tableId}`);
    if (searchInput) {
      searchInput.addEventListener("keyup", function (e) {
        dataTable.search(this.value).draw();
      });
    }
  });
}

/**
 * Initialize Charts for Analytics
 */
function initializeCharts() {
  // Check if Chart.js is loaded and charts container exists
  if (
    typeof Chart === "undefined" ||
    !document.getElementById("analyticsCharts")
  ) {
    return;
  }

  // Sample chart configurations
  createUserGrowthChart();
  createCampaignStatusChart();
  createInfluencerGenreChart();
  createMonthlyActivityChart();
}

function createUserGrowthChart() {
  const ctx = document.getElementById("userGrowthChart").getContext("2d");

  // This would normally be populated from an API
  const data = {
    labels: ["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
    influencers: [10, 15, 20, 25, 32, 45],
    sponsors: [5, 8, 12, 15, 20, 28],
  };

  new Chart(ctx, {
    type: "line",
    data: {
      labels: data.labels,
      datasets: [
        {
          label: "Influencers",
          data: data.influencers,
          borderColor: "#4e73df",
          backgroundColor: "rgba(78, 115, 223, 0.05)",
          borderWidth: 2,
          pointBackgroundColor: "#4e73df",
          tension: 0.1,
          fill: true,
        },
        {
          label: "Sponsors",
          data: data.sponsors,
          borderColor: "#36b9cc",
          backgroundColor: "rgba(54, 185, 204, 0.05)",
          borderWidth: 2,
          pointBackgroundColor: "#36b9cc",
          tension: 0.1,
          fill: true,
        },
      ],
    },
    options: {
      responsive: true,
      plugins: {
        legend: {
          position: "top",
        },
        tooltip: {
          mode: "index",
          intersect: false,
        },
      },
      scales: {
        y: {
          beginAtZero: true,
          title: {
            display: true,
            text: "Number of Users",
          },
        },
      },
    },
  });
}

function createCampaignStatusChart() {
  const ctx = document.getElementById("campaignStatusChart").getContext("2d");

  // This would normally be populated from an API
  const data = {
    labels: ["Active", "Pending", "Completed", "Paused"],
    values: [42, 28, 15, 5],
    colors: ["#1cc88a", "#f6c23e", "#4e73df", "#e74a3b"],
  };

  new Chart(ctx, {
    type: "doughnut",
    data: {
      labels: data.labels,
      datasets: [
        {
          data: data.values,
          backgroundColor: data.colors,
          hoverOffset: 4,
          borderWidth: 1,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: "bottom",
        },
      },
      cutout: "70%",
    },
  });
}

function createInfluencerGenreChart() {
  const ctx = document.getElementById("influencerGenreChart").getContext("2d");

  // This would normally be populated from an API
  const data = {
    labels: [
      "Fashion",
      "Gaming",
      "Tech",
      "Fitness",
      "Beauty",
      "Travel",
      "Food",
    ],
    values: [25, 18, 15, 12, 10, 8, 12],
    colors: [
      "#4e73df",
      "#1cc88a",
      "#36b9cc",
      "#f6c23e",
      "#e74a3b",
      "#6f42c1",
      "#fd7e14",
    ],
  };

  new Chart(ctx, {
    type: "bar",
    data: {
      labels: data.labels,
      datasets: [
        {
          label: "Influencers by Genre",
          data: data.values,
          backgroundColor: data.colors,
          borderWidth: 1,
        },
      ],
    },
    options: {
      responsive: true,
      plugins: {
        legend: {
          display: false,
        },
        tooltip: {
          callbacks: {
            label: function (context) {
              let label = context.dataset.label || "";
              return `${label}: ${context.parsed.y} influencers`;
            },
          },
        },
      },
      scales: {
        y: {
          beginAtZero: true,
          title: {
            display: true,
            text: "Number of Influencers",
          },
        },
      },
    },
  });
}

function createMonthlyActivityChart() {
  const ctx = document.getElementById("monthlyActivityChart").getContext("2d");

  // This would normally be populated from an API
  const data = {
    labels: ["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
    campaigns: [5, 8, 12, 15, 18, 20],
    requests: [8, 12, 18, 22, 25, 30],
    engagements: [20, 35, 45, 60, 75, 90],
  };

  new Chart(ctx, {
    type: "line",
    data: {
      labels: data.labels,
      datasets: [
        {
          label: "New Campaigns",
          data: data.campaigns,
          borderColor: "#4e73df",
          backgroundColor: "transparent",
          borderWidth: 2,
          pointBackgroundColor: "#4e73df",
        },
        {
          label: "Connection Requests",
          data: data.requests,
          borderColor: "#1cc88a",
          backgroundColor: "transparent",
          borderWidth: 2,
          pointBackgroundColor: "#1cc88a",
        },
        {
          label: "Engagements",
          data: data.engagements,
          borderColor: "#f6c23e",
          backgroundColor: "transparent",
          borderWidth: 2,
          pointBackgroundColor: "#f6c23e",
        },
      ],
    },
    options: {
      responsive: true,
      plugins: {
        legend: {
          position: "top",
        },
        tooltip: {
          mode: "index",
          intersect: false,
        },
      },
      scales: {
        y: {
          beginAtZero: true,
          title: {
            display: true,
            text: "Count",
          },
        },
      },
    },
  });
}

/**
 * Setup handlers for various admin actions
 */
function setupActionHandlers() {
  // User action handlers (flag, delete, etc.)
  document.querySelectorAll(".user-action").forEach((button) => {
    button.addEventListener("click", function (e) {
      e.preventDefault();

      const action = this.dataset.action;
      const userId = this.dataset.userId;
      const userType = this.dataset.userType;
      const userName = this.dataset.userName;

      if (action === "flag") {
        handleFlagAction(userId, userType, userName);
      } else if (action === "delete") {
        handleDeleteAction(userId, userType, userName);
      } else if (action === "view") {
        handleViewAction(userId, userType);
      }
    });
  });

  // Campaign action handlers
  document.querySelectorAll(".campaign-action").forEach((button) => {
    button.addEventListener("click", function (e) {
      e.preventDefault();

      const action = this.dataset.action;
      const campaignId = this.dataset.campaignId;
      const campaignName = this.dataset.campaignName;

      handleCampaignAction(action, campaignId, campaignName);
    });
  });
}

function handleFlagAction(userId, userType, userName) {
  if (confirm(`Are you sure you want to flag ${userType} "${userName}"?`)) {
    // AJAX request would normally be here
    console.log(`Flagging ${userType} ${userId}: ${userName}`);

    // Demo implementation to show functionality
    const formData = new FormData();
    formData.append(`${userType}_id`, userId);
    formData.append(`flag${userType === "sponsor" ? "_sponsor" : ""}`, "yes");

    fetch("/admin/actions", {
      method: "POST",
      body: formData,
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.success) {
          showToast(`${userType} "${userName}" has been flagged.`, "success");
          // Update UI to reflect the change
          updateUserStatus(userId, userType, "flagged");
        } else {
          showToast(`Failed to flag ${userType}.`, "error");
        }
      })
      .catch((error) => {
        console.error("Error:", error);
        showToast(`An error occurred while flagging ${userType}.`, "error");
      });
  }
}

function handleDeleteAction(userId, userType, userName) {
  if (
    confirm(
      `Are you sure you want to delete ${userType} "${userName}"? This action cannot be undone.`
    )
  ) {
    // AJAX request would normally be here
    console.log(`Deleting ${userType} ${userId}: ${userName}`);

    // Demo implementation to show functionality
    const formData = new FormData();
    formData.append(`${userType}_id`, userId);
    formData.append(`delete${userType === "sponsor" ? "_sponsor" : ""}`, "yes");

    fetch("/admin/actions", {
      method: "POST",
      body: formData,
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.success) {
          showToast(`${userType} "${userName}" has been deleted.`, "success");
          // Remove row from table
          document.querySelector(`#${userType}-${userId}`).remove();

          // Update counters
          updateCounters(`total_${userType}s`, -1);
        } else {
          showToast(`Failed to delete ${userType}.`, "error");
        }
      })
      .catch((error) => {
        console.error("Error:", error);
        showToast(`An error occurred while deleting ${userType}.`, "error");
      });
  }
}

function handleViewAction(userId, userType) {
  // Open modal with user details
  console.log(`Viewing ${userType} ${userId} details`);

  // AJAX request to fetch user details
  fetch(`/admin/user/${userType}/${userId}`)
    .then((response) => response.json())
    .then((data) => {
      if (data.success) {
        populateUserModal(data.user, userType);
        // Show modal using Bootstrap
        new bootstrap.Modal(document.getElementById("userDetailModal")).show();
      } else {
        showToast(`Failed to load ${userType} details.`, "error");
      }
    })
    .catch((error) => {
      console.error("Error:", error);
      showToast(
        `An error occurred while loading ${userType} details.`,
        "error"
      );
    });
}

function populateUserModal(user, userType) {
  const modal = document.getElementById("userDetailModal");
  const title = modal.querySelector(".modal-title");
  const body = modal.querySelector(".modal-body");

  title.textContent = `${
    userType.charAt(0).toUpperCase() + userType.slice(1)
  } Details: ${user.username}`;

  // Clear previous content
  body.innerHTML = "";

  // Create user detail fields
  const fields = Object.entries(user).filter(([key]) => key !== "password");

  const table = document.createElement("table");
  table.className = "table table-striped";

  fields.forEach(([key, value]) => {
    const row = table.insertRow();
    const keyCell = row.insertCell(0);
    const valueCell = row.insertCell(1);

    keyCell.innerHTML = `<strong>${key
      .replace("_", " ")
      .toUpperCase()}</strong>`;

    if (key === "profile_image" && value) {
      valueCell.innerHTML = `<img src="${value}" alt="Profile" class="img-fluid rounded" style="max-height: 100px">`;
    } else if (key === "flag") {
      valueCell.innerHTML =
        value === "yes"
          ? '<span class="badge bg-danger">Flagged</span>'
          : '<span class="badge bg-success">Good Standing</span>';
    } else if (key === "created_at" || key === "updated_at") {
      valueCell.textContent = new Date(value).toLocaleString();
    } else {
      valueCell.textContent = value || "N/A";
    }
  });

  body.appendChild(table);
}

function handleCampaignAction(action, campaignId, campaignName) {
  const actionLabels = {
    approve: "approve",
    pause: "pause",
    complete: "mark as completed",
    delete: "delete",
  };

  const actionLabel = actionLabels[action] || action;

  if (
    confirm(
      `Are you sure you want to ${actionLabel} campaign "${campaignName}"?`
    )
  ) {
    console.log(`${action} campaign ${campaignId}: ${campaignName}`);

    // Demo implementation to show functionality
    const formData = new FormData();
    formData.append("campaign_id", campaignId);
    formData.append("campaign_action", action);

    fetch("/admin/actions", {
      method: "POST",
      body: formData,
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.success) {
          showToast(
            `Campaign "${campaignName}" has been ${action}d.`,
            "success"
          );

          // Update UI based on action
          if (action === "delete") {
            document.querySelector(`#campaign-${campaignId}`).remove();
            updateCounters("total_campaigns", -1);
          } else {
            updateCampaignStatus(campaignId, action);

            // Update active campaign counter if needed
            if (action === "approve") {
              updateCounters("active_campaigns", 1);
            } else if (action === "pause" || action === "complete") {
              updateCounters("active_campaigns", -1);
            }
          }
        } else {
          showToast(`Failed to ${action} campaign.`, "error");
        }
      })
      .catch((error) => {
        console.error("Error:", error);
        showToast(`An error occurred while updating campaign.`, "error");
      });
  }
}

function updateUserStatus(userId, userType, status) {
  const userRow = document.querySelector(`#${userType}-${userId}`);
  if (userRow) {
    const statusCell = userRow.querySelector(".status-cell");
    if (statusCell) {
      if (status === "flagged") {
        statusCell.innerHTML = '<span class="badge bg-danger">Flagged</span>';
      } else {
        statusCell.innerHTML =
          '<span class="badge bg-success">Good Standing</span>';
      }
    }

    // Also update the action button
    const flagBtn = userRow.querySelector(`.user-action[data-action="flag"]`);
    if (flagBtn) {
      if (status === "flagged") {
        flagBtn.textContent = "Unflag";
        flagBtn.classList.remove("btn-warning");
        flagBtn.classList.add("btn-outline-warning");
      } else {
        flagBtn.textContent = "Flag";
        flagBtn.classList.remove("btn-outline-warning");
        flagBtn.classList.add("btn-warning");
      }
    }
  }
}

function updateCampaignStatus(campaignId, action) {
  const campaignRow = document.querySelector(`#campaign-${campaignId}`);
  if (campaignRow) {
    const statusCell = campaignRow.querySelector(".status-cell");
    if (statusCell) {
      const statusMap = {
        approve: '<span class="badge bg-success">Active</span>',
        pause: '<span class="badge bg-warning">Paused</span>',
        complete: '<span class="badge bg-primary">Completed</span>',
      };

      statusCell.innerHTML = statusMap[action] || statusCell.innerHTML;
    }
  }
}

/**
 * Theme toggling functionality
 */
function initializeThemeToggle() {
  const themeToggler = document.getElementById("themeToggler");
  if (!themeToggler) return;

  // Check for saved theme preference or respect OS setting
  const savedTheme = localStorage.getItem("admin-theme");
  const prefersDark =
    window.matchMedia &&
    window.matchMedia("(prefers-color-scheme: dark)").matches;

  // Apply theme based on saved preference or OS setting
  if (savedTheme === "dark" || (!savedTheme && prefersDark)) {
    document.body.classList.add("dark-theme");
    themeToggler.checked = true;
  }

  // Toggle theme when switch is clicked
  themeToggler.addEventListener("change", function () {
    if (this.checked) {
      document.body.classList.add("dark-theme");
      localStorage.setItem("admin-theme", "dark");
    } else {
      document.body.classList.remove("dark-theme");
      localStorage.setItem("admin-theme", "light");
    }
  });
}

/**
 * Export functionality for reports
 */
function setupExportFunctions() {
  const exportButtons = document.querySelectorAll(".export-data");

  exportButtons.forEach((button) => {
    button.addEventListener("click", function (e) {
      e.preventDefault();

      const format = this.dataset.format;
      const target = this.dataset.target;

      console.log(`Exporting ${target} in ${format} format`);

      // Get data to export
      const data = getExportData(target);

      if (format === "csv") {
        exportCSV(data, `${target}_export_${getFormattedDate()}`);
      } else if (format === "pdf") {
        exportPDF(data, `${target}_export_${getFormattedDate()}`);
      } else if (format === "excel") {
        exportExcel(data, `${target}_export_${getFormattedDate()}`);
      }
    });
  });
}

function getExportData(target) {
  // In a real application, this would fetch the actual data
  // For demo purposes, we'll return placeholder data
  switch (target) {
    case "influencers":
      return [
        [
          "ID",
          "Username",
          "Email",
          "Genre",
          "Platform",
          "Status",
          "Joined Date",
        ],
        [
          1,
          "influencer1",
          "inf1@example.com",
          "Fashion",
          "Instagram",
          "Active",
          "2024-01-15",
        ],
        [
          2,
          "influencer2",
          "inf2@example.com",
          "Gaming",
          "YouTube",
          "Active",
          "2024-02-20",
        ],
        [
          3,
          "influencer3",
          "inf3@example.com",
          "Tech",
          "TikTok",
          "Flagged",
          "2024-03-05",
        ],
      ];

    case "sponsors":
      return [
        [
          "ID",
          "Company",
          "Contact",
          "Email",
          "Industry",
          "Status",
          "Joined Date",
        ],
        [
          1,
          "ABC Corp",
          "John Doe",
          "john@abccorp.com",
          "Fashion",
          "Active",
          "2024-01-10",
        ],
        [
          2,
          "XYZ Inc",
          "Jane Smith",
          "jane@xyzinc.com",
          "Technology",
          "Active",
          "2024-02-15",
        ],
        [
          3,
          "Acme LLC",
          "Bob Johnson",
          "bob@acme.com",
          "Food",
          "Flagged",
          "2024-03-20",
        ],
      ];

    case "campaigns":
      return [
        [
          "ID",
          "Campaign Name",
          "Sponsor",
          "Budget",
          "Status",
          "Start Date",
          "End Date",
        ],
        [
          1,
          "Summer Fashion",
          "ABC Corp",
          "$5000",
          "Active",
          "2024-05-01",
          "2024-06-30",
        ],
        [
          2,
          "Gaming Launch",
          "XYZ Inc",
          "$8000",
          "Pending",
          "2024-06-15",
          "2024-07-15",
        ],
        [
          3,
          "Food Review",
          "Acme LLC",
          "$3000",
          "Completed",
          "2024-04-01",
          "2024-04-30",
        ],
      ];

    default:
      return [["No data available"]];
  }
}

function exportCSV(data, filename) {
  const csvContent = data
    .map((row) =>
      row
        .map((cell) =>
          typeof cell === "string" && cell.includes(",") ? `"${cell}"` : cell
        )
        .join(",")
    )
    .join("\n");

  const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
  const link = document.createElement("a");

  const url = URL.createObjectURL(blob);
  link.setAttribute("href", url);
  link.setAttribute("download", `${filename}.csv`);
  link.style.visibility = "hidden";

  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);

  showToast("CSV exported successfully", "success");
}

function exportPDF(data, filename) {
  // In a real application, this would use a library like jsPDF
  console.log("PDF export would be implemented with a library like jsPDF");
  console.log("Data to export:", data);

  showToast("PDF export feature coming soon", "info");
}

function exportExcel(data, filename) {
  // In a real application, this would use a library like SheetJS
  console.log("Excel export would be implemented with a library like SheetJS");
  console.log("Data to export:", data);

  showToast("Excel export feature coming soon", "info");
}

function getFormattedDate() {
  const now = new Date();
  return `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(
    2,
    "0"
  )}-${String(now.getDate()).padStart(2, "0")}`;
}

/**
 * Initialize animated counters
 */
function initializeCounters() {
  const counters = document.querySelectorAll(".counter-value");

  counters.forEach((counter) => {
    const target = parseInt(counter.getAttribute("data-target"));
    const duration = 1000; // ms
    const steps = 50;
    const stepValue = target / steps;
    let current = 0;

    const updateCounter = () => {
      if (current < target) {
        current += stepValue;
        counter.textContent = Math.ceil(current);
        setTimeout(updateCounter, duration / steps);
      } else {
        counter.textContent = target;
      }
    };

    updateCounter();
  });
}

function updateCounters(counterId, change) {
  const counter = document.querySelector(`#${counterId}`);
  if (counter) {
    const currentValue = parseInt(counter.textContent);
    const newValue = currentValue + change;

    // Update the displayed value
    counter.textContent = newValue;

    // Update the data-target attribute for future animations
    counter.setAttribute("data-target", newValue);
  }
}

/**
 * Notification system
 */
function setupNotifications() {
  // Check for new notifications every minute
  checkForNotifications();
  setInterval(checkForNotifications, 60000);
}

function checkForNotifications() {
  // In a real app, this would be an API call
  console.log("Checking for new notifications...");

  // Demo implementation
  const hasNotification = Math.random() > 0.7; // 30% chance of notification

  if (hasNotification) {
    const messages = [
      "New influencer just registered",
      "A campaign was just created and needs approval",
      "Flagged content needs review",
      "System update available",
    ];

    const randomMessage = messages[Math.floor(Math.random() * messages.length)];
    showToast(randomMessage, "info");

    // Update notification badge
    const badge = document.getElementById("notificationBadge");
    if (badge) {
      const count = parseInt(badge.textContent || "0");
      badge.textContent = count + 1;
      badge.classList.remove("d-none");
    }
  }
}

/**
 * Toast notification helper
 */
function showToast(message, type = "info") {
  // Create toast container if it doesn't exist
  let toastContainer = document.querySelector(".toast-container");

  if (!toastContainer) {
    toastContainer = document.createElement("div");
    toastContainer.className =
      "toast-container position-fixed bottom-0 end-0 p-3";
    document.body.appendChild(toastContainer);
  }

  // Create toast element
  const toastId = `toast-${Date.now()}`;
  const bgClass =
    type === "success"
      ? "bg-success"
      : type === "error"
      ? "bg-danger"
      : type === "warning"
      ? "bg-warning"
      : "bg-info";

  const toastHtml = `
        <div id="${toastId}" class="toast align-items-center ${bgClass} text-white border-0" role="alert" aria-live="assertive" aria-atomic="true">
            <div class="d-flex">
                <div class="toast-body">
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
        </div>
    `;

  toastContainer.insertAdjacentHTML("beforeend", toastHtml);

  // Initialize and show the toast
  const toastElement = document.getElementById(toastId);
  const toast = new bootstrap.Toast(toastElement, {
    delay: 5000,
  });

  toast.show();

  // Remove toast from DOM after it's hidden
  toastElement.addEventListener("hidden.bs.toast", function () {
    toastElement.remove();
  });
}

/**
 * Initialize tab navigation for user management section
 */
function initializeTabNavigation() {
  // Find all tab navigation elements
  const tabElements = document.querySelectorAll('[data-toggle="tab"]');

  // Add click event listeners to each tab
  tabElements.forEach((tab) => {
    tab.addEventListener("click", function (event) {
      event.preventDefault();

      // Get the target tab content
      const target =
        this.getAttribute("href") || this.getAttribute("data-target");

      if (target) {
        // Deactivate all tabs and hide all tab contents
        const tabNavigation = this.closest(".nav");
        if (tabNavigation) {
          // Remove active class from all tabs
          tabNavigation.querySelectorAll(".nav-link").forEach((navLink) => {
            navLink.classList.remove("active");
          });

          // Add active class to clicked tab
          this.classList.add("active");

          // Hide all tab contents
          const tabContents = document.querySelectorAll(".tab-pane");
          tabContents.forEach((content) => {
            content.classList.remove("show", "active");
          });

          // Show the selected tab content
          const selectedContent = document.querySelector(target);
          if (selectedContent) {
            selectedContent.classList.add("show", "active");
          }
        }
      }
    });
  });

  // If there's a hash in the URL, activate that tab
  const hash = window.location.hash;
  if (hash) {
    const tab =
      document.querySelector(`[href="${hash}"]`) ||
      document.querySelector(`[data-target="${hash}"]`);
    if (tab) {
      tab.click();
    }
  }
}
