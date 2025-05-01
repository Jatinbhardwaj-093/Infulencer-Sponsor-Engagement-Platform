/**
 * Main JavaScript file for the Influencer Engagement Platform
 * Handles notifications, charts, and other dynamic features
 */

document.addEventListener("DOMContentLoaded", function () {
  // Initialize all tooltips
  initTooltips();

  // Initialize notification system
  initNotifications();

  // Initialize charts if they exist on the page
  initCharts();

  // Initialize search functionality
  initSearch();

  // Initialize form validation
  initFormValidation();
});

/**
 * Initialize Bootstrap tooltips
 */
function initTooltips() {
  const tooltipTriggerList = document.querySelectorAll(
    '[data-bs-toggle="tooltip"]'
  );
  [...tooltipTriggerList].map(
    (tooltipTriggerEl) => new bootstrap.Tooltip(tooltipTriggerEl)
  );
}

/**
 * Initialize notification system
 */
function initNotifications() {
  const notificationDropdown = document.getElementById("notificationDropdown");
  const notificationsList = document.getElementById("notificationsList");
  const notificationBadge = document.getElementById("notificationBadge");
  const markAllReadBtn = document.getElementById("markAllRead");

  // If notification elements don't exist, return
  if (!notificationDropdown) return;

  // Load notifications when dropdown is opened
  notificationDropdown.addEventListener("shown.bs.dropdown", loadNotifications);

  // Handle mark all as read button
  if (markAllReadBtn) {
    markAllReadBtn.addEventListener("click", markAllNotificationsAsRead);
  }

  // Initial load of notification count
  updateNotificationCount();

  // Auto refresh notifications every 60 seconds
  setInterval(updateNotificationCount, 60000);
}

/**
 * Load notifications from the server
 */
function loadNotifications() {
  const notificationsList = document.getElementById("notificationsList");
  if (!notificationsList) return;

  // Show loading indicator
  notificationsList.innerHTML =
    '<div class="text-center py-3"><div class="spinner-border text-primary" role="status"><span class="visually-hidden">Loading...</span></div></div>';

  // Fetch notifications from API
  fetch("/api/notifications?limit=5")
    .then((response) => {
      if (!response.ok) {
        throw new Error("Failed to load notifications");
      }
      return response.json();
    })
    .then((data) => {
      renderNotifications(data.notifications, notificationsList);
    })
    .catch((error) => {
      console.error("Error loading notifications:", error);
      notificationsList.innerHTML =
        '<div class="text-center text-danger py-3">Failed to load notifications</div>';
    });
}

/**
 * Render notifications in the dropdown
 */
function renderNotifications(notifications, container) {
  if (!notifications || notifications.length === 0) {
    container.innerHTML =
      '<div class="text-center py-3 text-muted">No notifications</div>';
    return;
  }

  let html = "";

  notifications.forEach((notification) => {
    const isRead = notification.is_read ? "bg-light" : "bg-light-hover fw-bold";
    const icon = getNotificationIcon(notification.type);
    const timeAgo = formatTimeAgo(new Date(notification.created_at));

    html += `
            <div class="dropdown-item notification-item ${isRead}" data-id="${notification.id}">
                <div class="d-flex">
                    <div class="notification-icon bg-${notification.type} text-white">
                        <i class="${icon}"></i>
                    </div>
                    <div class="notification-content ms-3">
                        <h6 class="notification-title mb-1">${notification.title}</h6>
                        <p class="notification-message mb-1 small">${notification.message}</p>
                        <div class="notification-time text-muted small">
                            <i class="fas fa-clock me-1"></i> ${timeAgo}
                        </div>
                    </div>
                </div>
            </div>
        `;
  });

  container.innerHTML = html;

  // Add event listeners to mark notifications as read
  document.querySelectorAll(".notification-item").forEach((item) => {
    item.addEventListener("click", function () {
      const notificationId = this.dataset.id;
      markNotificationAsRead(notificationId);

      // If there's a link, navigate to it
      const link = notifications.find((n) => n.id == notificationId).link;
      if (link) {
        window.location.href = link;
      }
    });
  });
}

/**
 * Mark a notification as read
 */
function markNotificationAsRead(notificationId) {
  fetch(`/api/notifications/read/${notificationId}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": getCsrfToken(),
    },
  })
    .then((response) => {
      if (!response.ok) {
        throw new Error("Failed to mark notification as read");
      }
      return response.json();
    })
    .then((data) => {
      // Update notification count
      updateNotificationCount();
    })
    .catch((error) => {
      console.error("Error marking notification as read:", error);
    });
}

/**
 * Mark all notifications as read
 */
function markAllNotificationsAsRead() {
  fetch("/api/notifications/read-all", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": getCsrfToken(),
    },
  })
    .then((response) => {
      if (!response.ok) {
        throw new Error("Failed to mark all notifications as read");
      }
      return response.json();
    })
    .then((data) => {
      // Reload notifications
      loadNotifications();

      // Update notification count
      updateNotificationCount();
    })
    .catch((error) => {
      console.error("Error marking all notifications as read:", error);
    });
}

/**
 * Update the notification count badge
 */
function updateNotificationCount() {
  const notificationBadge = document.getElementById("notificationBadge");
  if (!notificationBadge) return;

  fetch("/api/notifications?unread_only=true&limit=0")
    .then((response) => {
      if (!response.ok) {
        throw new Error("Failed to get notification count");
      }
      return response.json();
    })
    .then((data) => {
      const count = data.unread_count;

      if (count > 0) {
        notificationBadge.textContent = count > 9 ? "9+" : count;
        notificationBadge.classList.remove("d-none");
      } else {
        notificationBadge.classList.add("d-none");
      }
    })
    .catch((error) => {
      console.error("Error updating notification count:", error);
    });
}

/**
 * Get appropriate icon for notification type
 */
function getNotificationIcon(type) {
  switch (type) {
    case "info":
      return "fas fa-info-circle";
    case "success":
      return "fas fa-check-circle";
    case "warning":
      return "fas fa-exclamation-triangle";
    case "danger":
      return "fas fa-times-circle";
    default:
      return "fas fa-bell";
  }
}

/**
 * Format date to relative time (e.g., "2 hours ago")
 */
function formatTimeAgo(date) {
  const now = new Date();
  const diffInSeconds = Math.floor((now - date) / 1000);

  if (diffInSeconds < 60) {
    return "Just now";
  }

  const diffInMinutes = Math.floor(diffInSeconds / 60);
  if (diffInMinutes < 60) {
    return `${diffInMinutes} minute${diffInMinutes > 1 ? "s" : ""} ago`;
  }

  const diffInHours = Math.floor(diffInMinutes / 60);
  if (diffInHours < 24) {
    return `${diffInHours} hour${diffInHours > 1 ? "s" : ""} ago`;
  }

  const diffInDays = Math.floor(diffInHours / 24);
  if (diffInDays < 30) {
    return `${diffInDays} day${diffInDays > 1 ? "s" : ""} ago`;
  }

  const diffInMonths = Math.floor(diffInDays / 30);
  if (diffInMonths < 12) {
    return `${diffInMonths} month${diffInMonths > 1 ? "s" : ""} ago`;
  }

  const diffInYears = Math.floor(diffInMonths / 12);
  return `${diffInYears} year${diffInYears > 1 ? "s" : ""} ago`;
}

/**
 * Initialize Chart.js charts on dashboard
 */
function initCharts() {
  // Platform Growth Chart
  const platformGrowthCanvas = document.getElementById("platformGrowthChart");
  if (platformGrowthCanvas) {
    const ctx = platformGrowthCanvas.getContext("2d");
    const chartData = JSON.parse(platformGrowthCanvas.dataset.chart);

    new Chart(ctx, {
      type: "line",
      data: {
        labels: chartData.labels,
        datasets: [
          {
            label: "Influencers",
            data: chartData.influencer_data,
            borderColor: "#4e73df",
            backgroundColor: "rgba(78, 115, 223, 0.1)",
            borderWidth: 2,
            pointBackgroundColor: "#4e73df",
            pointBorderColor: "#fff",
            pointHoverRadius: 5,
            pointHoverBackgroundColor: "#4e73df",
            tension: 0.3,
            fill: true,
          },
          {
            label: "Sponsors",
            data: chartData.sponsor_data,
            borderColor: "#1cc88a",
            backgroundColor: "rgba(28, 200, 138, 0.1)",
            borderWidth: 2,
            pointBackgroundColor: "#1cc88a",
            pointBorderColor: "#fff",
            pointHoverRadius: 5,
            pointHoverBackgroundColor: "#1cc88a",
            tension: 0.3,
            fill: true,
          },
        ],
      },
      options: {
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: "bottom",
            labels: {
              usePointStyle: true,
              padding: 20,
            },
          },
          tooltip: {
            mode: "index",
            intersect: false,
          },
        },
        scales: {
          x: {
            grid: {
              display: false,
            },
            ticks: {
              maxTicksLimit: 7,
            },
          },
          y: {
            beginAtZero: true,
            grid: {
              color: "rgba(0, 0, 0, 0.05)",
            },
            ticks: {
              maxTicksLimit: 5,
              precision: 0,
            },
          },
        },
      },
    });
  }

  // Genre Distribution Chart
  const genreDistributionCanvas = document.getElementById(
    "genreDistributionChart"
  );
  if (genreDistributionCanvas) {
    const ctx = genreDistributionCanvas.getContext("2d");
    const chartData = JSON.parse(genreDistributionCanvas.dataset.chart);

    new Chart(ctx, {
      type: "doughnut",
      data: {
        labels: chartData.labels,
        datasets: [
          {
            data: chartData.data,
            backgroundColor: [
              "#4e73df",
              "#1cc88a",
              "#36b9cc",
              "#f6c23e",
              "#e74a3b",
              "#5a5c69",
              "#858796",
              "#6f42c1",
              "#20c9a6",
              "#27a8dc",
              "#e36a77",
            ],
            borderWidth: 1,
            hoverOffset: 5,
          },
        ],
      },
      options: {
        maintainAspectRatio: false,
        cutout: "70%",
        plugins: {
          legend: {
            position: "bottom",
            display: true,
          },
        },
      },
    });
  }

  // Platform Distribution Chart
  const platformDistributionCanvas = document.getElementById(
    "platformDistributionChart"
  );
  if (platformDistributionCanvas) {
    const ctx = platformDistributionCanvas.getContext("2d");
    const chartData = JSON.parse(platformDistributionCanvas.dataset.chart);

    new Chart(ctx, {
      type: "pie",
      data: {
        labels: chartData.labels,
        datasets: [
          {
            data: chartData.data,
            backgroundColor: [
              "#4267B2",
              "#1DA1F2",
              "#E1306C",
              "#FF0000",
              "#2867B2",
              "#00B489",
              "#1DB954",
              "#25D366",
              "#06454c",
              "#120b28",
              "#ed6926",
            ],
            borderWidth: 1,
            hoverOffset: 5,
          },
        ],
      },
      options: {
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: "bottom",
            display: true,
          },
        },
      },
    });
  }

  // Campaign Timeline Chart
  const campaignTimelineCanvas = document.getElementById(
    "campaignTimelineChart"
  );
  if (campaignTimelineCanvas) {
    const ctx = campaignTimelineCanvas.getContext("2d");
    const chartData = JSON.parse(campaignTimelineCanvas.dataset.chart);

    new Chart(ctx, {
      type: "bar",
      data: {
        labels: chartData.labels,
        datasets: [
          {
            label: "New Campaigns",
            data: chartData.data,
            backgroundColor: "rgba(28, 200, 138, 0.7)",
            borderColor: "#1cc88a",
            borderWidth: 1,
          },
        ],
      },
      options: {
        maintainAspectRatio: false,
        plugins: {
          legend: {
            display: false,
          },
        },
        scales: {
          x: {
            grid: {
              display: false,
            },
            ticks: {
              maxTicksLimit: 7,
            },
          },
          y: {
            beginAtZero: true,
            grid: {
              color: "rgba(0, 0, 0, 0.05)",
            },
            ticks: {
              maxTicksLimit: 5,
              precision: 0,
            },
          },
        },
      },
    });
  }
}

/**
 * Initialize search functionality
 */
function initSearch() {
  const campaignSearchInput = document.getElementById("campaignSearch");
  const influencerSearchInput = document.getElementById("influencerSearch");

  if (campaignSearchInput) {
    campaignSearchInput.addEventListener(
      "input",
      debounce(function () {
        searchCampaigns(campaignSearchInput.value);
      }, 500)
    );
  }

  if (influencerSearchInput) {
    influencerSearchInput.addEventListener(
      "input",
      debounce(function () {
        searchInfluencers(influencerSearchInput.value);
      }, 500)
    );
  }

  // Initialize search filters
  const filterForms = document.querySelectorAll(".search-filter-form");
  filterForms.forEach((form) => {
    form.addEventListener("submit", function (event) {
      event.preventDefault();

      const formData = new FormData(form);
      const urlParams = new URLSearchParams();

      for (let pair of formData.entries()) {
        if (pair[1]) {
          urlParams.append(pair[0], pair[1]);
        }
      }

      // Get the current page
      const currentPage = form.dataset.searchType || "campaigns";

      // Redirect with search params
      window.location.href = `/${currentPage}/search?${urlParams.toString()}`;
    });
  });
}

/**
 * Search campaigns
 */
function searchCampaigns(query) {
  // Show loading state
  const resultsContainer = document.getElementById("campaignResults");
  if (resultsContainer) {
    resultsContainer.innerHTML =
      '<div class="text-center py-4"><div class="spinner-border text-primary" role="status"><span class="visually-hidden">Loading...</span></div></div>';
  }

  // Get filter values
  const genre = document.getElementById("genreFilter")?.value || "";
  const status = document.getElementById("statusFilter")?.value || "";

  // Build query string
  let queryString = `query=${encodeURIComponent(query)}`;
  if (genre) queryString += `&genre=${encodeURIComponent(genre)}`;
  if (status) queryString += `&status=${encodeURIComponent(status)}`;

  // Fetch results
  fetch(`/api/campaigns/search?${queryString}`)
    .then((response) => {
      if (!response.ok) {
        throw new Error("Search failed");
      }
      return response.json();
    })
    .then((data) => {
      renderCampaignResults(data, resultsContainer);
    })
    .catch((error) => {
      console.error("Error searching campaigns:", error);
      if (resultsContainer) {
        resultsContainer.innerHTML =
          '<div class="alert alert-danger">Error searching campaigns. Please try again.</div>';
      }
    });
}

/**
 * Render campaign search results
 */
function renderCampaignResults(campaigns, container) {
  if (!container) return;

  if (campaigns.length === 0) {
    container.innerHTML =
      '<div class="text-center py-4"><i class="fas fa-search fa-3x text-muted mb-3"></i><p class="text-muted">No campaigns found. Try a different search term.</p></div>';
    return;
  }

  let html = '<div class="row">';

  campaigns.forEach((campaign) => {
    html += `
            <div class="col-md-6 col-lg-4 mb-4">
                <div class="card campaign-card h-100 shadow-sm">
                    <div class="card-body">
                        <h5 class="card-title text-truncate">
                            <a href="/campaign/${
                              campaign.campaign_id
                            }" class="text-decoration-none">${
      campaign.campaign_name
    }</a>
                        </h5>
                        <p class="campaign-meta mb-2">
                            <span class="text-muted"><i class="fas fa-building me-1"></i> ${
                              campaign.sponsor_name
                            }</span>
                            <span class="ms-2 badge bg-${getStatusColor(
                              campaign.status
                            )}">${campaign.status}</span>
                        </p>
                        <p class="card-text text-truncate">${
                          campaign.description
                        }</p>
                        <div class="d-flex justify-content-between align-items-center mt-3">
                            <div>
                                <span class="badge bg-light text-dark">
                                    <i class="fas fa-tag me-1"></i> ${
                                      campaign.genre
                                    }
                                </span>
                            </div>
                            <div>
                                <span class="text-success fw-bold">$${
                                  campaign.budget
                                }</span>
                            </div>
                        </div>
                    </div>
                    <div class="card-footer bg-white border-top-0">
                        <div class="d-flex justify-content-between align-items-center">
                            <small class="text-muted">
                                ${formatDateRange(
                                  campaign.start_date,
                                  campaign.end_date
                                )}
                            </small>
                            <a href="/campaign/${
                              campaign.campaign_id
                            }" class="btn btn-sm btn-outline-primary">View Details</a>
                        </div>
                    </div>
                </div>
            </div>
        `;
  });

  html += "</div>";
  container.innerHTML = html;
}

/**
 * Search influencers
 */
function searchInfluencers(query) {
  // Show loading state
  const resultsContainer = document.getElementById("influencerResults");
  if (resultsContainer) {
    resultsContainer.innerHTML =
      '<div class="text-center py-4"><div class="spinner-border text-primary" role="status"><span class="visually-hidden">Loading...</span></div></div>';
  }

  // Get filter values
  const platform = document.getElementById("platformFilter")?.value || "";
  const genre = document.getElementById("genreFilter")?.value || "";
  const popularity = document.getElementById("popularityFilter")?.value || "";

  // Build query string
  let queryString = `query=${encodeURIComponent(query)}`;
  if (platform) queryString += `&platform=${encodeURIComponent(platform)}`;
  if (genre) queryString += `&genre=${encodeURIComponent(genre)}`;
  if (popularity)
    queryString += `&popularity=${encodeURIComponent(popularity)}`;

  // Fetch results
  fetch(`/api/influencers/search?${queryString}`)
    .then((response) => {
      if (!response.ok) {
        throw new Error("Search failed");
      }
      return response.json();
    })
    .then((data) => {
      renderInfluencerResults(data, resultsContainer);
    })
    .catch((error) => {
      console.error("Error searching influencers:", error);
      if (resultsContainer) {
        resultsContainer.innerHTML =
          '<div class="alert alert-danger">Error searching influencers. Please try again.</div>';
      }
    });
}

/**
 * Render influencer search results
 */
function renderInfluencerResults(influencers, container) {
  if (!container) return;

  if (influencers.length === 0) {
    container.innerHTML =
      '<div class="text-center py-4"><i class="fas fa-search fa-3x text-muted mb-3"></i><p class="text-muted">No influencers found. Try a different search term.</p></div>';
    return;
  }

  let html = '<div class="row">';

  influencers.forEach((influencer) => {
    html += `
            <div class="col-md-6 col-lg-4 mb-4">
                <div class="card h-100 shadow-sm">
                    <div class="card-body">
                        <div class="d-flex align-items-center mb-3">
                            <div class="influencer-avatar bg-${getPlatformColor(
                              influencer.platform
                            )} me-3">
                                <i class="${getPlatformIcon(
                                  influencer.platform
                                )}"></i>
                            </div>
                            <div>
                                <h5 class="mb-0">${influencer.username}</h5>
                                <span class="text-muted small">${
                                  influencer.platform
                                }</span>
                            </div>
                        </div>
                        <div class="mb-3">
                            <span class="badge bg-light text-dark me-1">
                                <i class="fas fa-tag me-1"></i> ${
                                  influencer.genre
                                }
                            </span>
                            <span class="badge ${getPopularityBadge(
                              influencer.popularity
                            )}">
                                ${influencer.popularity}
                            </span>
                        </div>
                        <p class="card-text text-truncate">${
                          influencer.bio || "No bio available"
                        }</p>
                    </div>
                    <div class="card-footer bg-white border-top-0">
                        <div class="d-flex justify-content-end">
                            <a href="/influencer/${
                              influencer.influencer_id
                            }" class="btn btn-sm btn-outline-primary">View Profile</a>
                        </div>
                    </div>
                </div>
            </div>
        `;
  });

  html += "</div>";
  container.innerHTML = html;
}

/**
 * Initialize form validation
 */
function initFormValidation() {
  const forms = document.querySelectorAll(".needs-validation");

  Array.from(forms).forEach((form) => {
    form.addEventListener(
      "submit",
      (event) => {
        if (!form.checkValidity()) {
          event.preventDefault();
          event.stopPropagation();
        }

        form.classList.add("was-validated");
      },
      false
    );
  });

  // Password strength validation
  const passwordInputs = document.querySelectorAll(
    "input[data-password-strength]"
  );
  passwordInputs.forEach((input) => {
    const feedbackElement = document.getElementById(
      input.dataset.feedbackElement
    );

    if (feedbackElement) {
      input.addEventListener("input", () => {
        validatePasswordStrength(input.value, feedbackElement);
      });
    }
  });
}

/**
 * Validate password strength and update feedback element
 */
function validatePasswordStrength(password, feedbackElement) {
  // Reset
  feedbackElement.className = "password-strength-feedback mt-1";

  // Check strength
  let strength = 0;
  let feedback = "";

  if (password.length >= 8) {
    strength++;
  }

  if (password.match(/[A-Z]/)) {
    strength++;
  }

  if (password.match(/[a-z]/)) {
    strength++;
  }

  if (password.match(/[0-9]/)) {
    strength++;
  }

  if (password.match(/[^A-Za-z0-9]/)) {
    strength++;
  }

  // Update feedback
  switch (strength) {
    case 0:
      feedbackElement.textContent = "Password is required";
      feedbackElement.classList.add("text-danger");
      break;
    case 1:
      feedbackElement.textContent = "Password is very weak";
      feedbackElement.classList.add("text-danger");
      break;
    case 2:
      feedbackElement.textContent = "Password is weak";
      feedbackElement.classList.add("text-warning");
      break;
    case 3:
      feedbackElement.textContent = "Password is medium";
      feedbackElement.classList.add("text-info");
      break;
    case 4:
      feedbackElement.textContent = "Password is strong";
      feedbackElement.classList.add("text-success");
      break;
    case 5:
      feedbackElement.textContent = "Password is very strong";
      feedbackElement.classList.add("text-success");
      break;
  }
}

/**
 * Get the CSRF token
 */
function getCsrfToken() {
  return document
    .querySelector('meta[name="csrf-token"]')
    ?.getAttribute("content");
}

/**
 * Format date range for display
 */
function formatDateRange(startDate, endDate) {
  const start = new Date(startDate);
  const end = new Date(endDate);

  const options = { month: "short", day: "numeric" };
  return `${start.toLocaleDateString(
    "en-US",
    options
  )} - ${end.toLocaleDateString("en-US", options)}`;
}

/**
 * Get color class based on status
 */
function getStatusColor(status) {
  switch (status.toLowerCase()) {
    case "active":
      return "success";
    case "pending":
      return "warning";
    case "completed":
      return "primary";
    case "rejected":
    case "cancelled":
      return "danger";
    default:
      return "secondary";
  }
}

/**
 * Get color based on social media platform
 */
function getPlatformColor(platform) {
  switch (platform.toLowerCase()) {
    case "instagram":
      return "instagram";
    case "youtube":
      return "youtube";
    case "tiktok":
      return "tiktok";
    case "twitter":
    case "x":
      return "twitter";
    case "facebook":
      return "facebook";
    case "linkedin":
      return "linkedin";
    case "twitch":
      return "twitch";
    default:
      return "primary";
  }
}

/**
 * Get icon for social media platform
 */
function getPlatformIcon(platform) {
  switch (platform.toLowerCase()) {
    case "instagram":
      return "fab fa-instagram";
    case "youtube":
      return "fab fa-youtube";
    case "tiktok":
      return "fab fa-tiktok";
    case "twitter":
    case "x":
      return "fab fa-twitter";
    case "facebook":
      return "fab fa-facebook";
    case "linkedin":
      return "fab fa-linkedin";
    case "twitch":
      return "fab fa-twitch";
    default:
      return "fas fa-globe";
  }
}

/**
 * Get badge class for popularity
 */
function getPopularityBadge(popularity) {
  switch (popularity.toLowerCase()) {
    case "micro":
      return "bg-light text-dark";
    case "mid-tier":
      return "bg-info text-white";
    case "macro":
      return "bg-primary text-white";
    case "mega":
      return "bg-warning text-dark";
    default:
      return "bg-secondary text-white";
  }
}

/**
 * Debounce function to limit how often a function is called
 */
function debounce(func, wait) {
  let timeout;
  return function (...args) {
    clearTimeout(timeout);
    timeout = setTimeout(() => func.apply(this, args), wait);
  };
}
