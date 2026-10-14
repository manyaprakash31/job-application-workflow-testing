/**
 * JobStream Career Portal - Client Script
 * Handles job fetching, dynamic DOM rendering, client-side validation,
 * asynchronous application submission, and error handling.
 */

// Regex validators
const EMAIL_REGEX = /^[\w\.-]+@[\w\.-]+\.\w+$/;
const PHONE_REGEX = /^\+?[\d\s\-\(\)]{10,20}$/;
const URL_REGEX = /^https?:\/\/.+/i;
const ALLOWED_EXTENSIONS = [".pdf", ".docx", ".doc", ".txt"];

/**
 * Load and display all open positions on index.html
 */
async function loadJobListings() {
  const container = document.getElementById("jobs-container");
  const countLabel = document.getElementById("jobs-count");
  const searchInput = document.getElementById("search-input");

  if (!container) return;

  try {
    const res = await fetch("/api/jobs");
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    const jobs = data.jobs || [];

    function render(jobsList) {
      container.innerHTML = "";
      if (jobsList.length === 0) {
        container.innerHTML = `<div style="grid-column: 1 / -1; text-align: center; padding: 3rem; color: var(--text-muted);" data-testid="no-jobs-found">No job positions match your criteria.</div>`;
        if (countLabel) countLabel.textContent = "0 open positions";
        return;
      }

      if (countLabel) {
        countLabel.textContent = `${jobsList.length} open position${jobsList.length > 1 ? "s" : ""}`;
      }

      jobsList.forEach((job) => {
        const card = document.createElement("div");
        card.className = "job-card";
        card.setAttribute("data-testid", `job-card-${job.id}`);

        card.innerHTML = `
          <span class="job-badge" data-testid="job-department">${escapeHtml(job.department)}</span>
          <h3 class="job-title" data-testid="job-title">${escapeHtml(job.title)}</h3>
          <div class="job-meta">
            <div class="job-meta-item">
              <span class="meta-label">Location:</span>
              <span data-testid="job-location">${escapeHtml(job.location)}</span>
            </div>
            <div class="job-meta-item">
              <span class="meta-label">Salary:</span>
              <span class="job-salary" data-testid="job-salary">${escapeHtml(job.salary)}</span>
            </div>
            <div class="job-meta-item">
              <span class="meta-label">Experience:</span>
              <span class="job-experience" data-testid="job-experience">${escapeHtml(job.experience)}</span>
            </div>
          </div>
          <p class="job-description" data-testid="job-description">${escapeHtml(job.description)}</p>
          <a href="job.html?id=${encodeURIComponent(job.id)}" class="btn btn-primary" data-testid="apply-btn-${job.id}">
            Apply Now &rarr;
          </a>
        `;
        container.appendChild(card);
      });
    }

    render(jobs);

    if (searchInput) {
      searchInput.addEventListener("input", (e) => {
        const q = e.target.value.toLowerCase().trim();
        const filtered = jobs.filter((j) =>
          j.title.toLowerCase().includes(q) ||
          j.department.toLowerCase().includes(q) ||
          j.location.toLowerCase().includes(q) ||
          j.description.toLowerCase().includes(q)
        );
        render(filtered);
      });
    }
  } catch (err) {
    container.innerHTML = `
      <div class="alert alert-error visible" data-testid="load-error">
        Failed to load job listings. Please ensure the backend server is running. (${err.message})
      </div>
    `;
    if (countLabel) countLabel.textContent = "Error loading jobs";
  }
}

/**
 * Load single job details on job.html
 */
async function loadJobDetails() {
  const params = new URLSearchParams(window.location.search);
  const jobId = params.get("id");

  const titleEl = document.getElementById("detail-title");
  const deptEl = document.getElementById("detail-dept");
  const locationEl = document.getElementById("detail-location");
  const salaryEl = document.getElementById("detail-salary");
  const expEl = document.getElementById("detail-experience");
  const descEl = document.getElementById("detail-description");
  const reqsEl = document.getElementById("detail-requirements");
  const hiddenJobId = document.getElementById("jobId");
  const form = document.getElementById("application-form");

  if (!jobId) {
    if (titleEl) titleEl.textContent = "No Job Selected";
    if (descEl) descEl.textContent = "Please return to the jobs directory to choose a position.";
    if (form) form.style.display = "none";
    return;
  }

  if (hiddenJobId) hiddenJobId.value = jobId;

  // Auto-check simulation if query param present
  if (params.get("simulate_error")) {
    const chk = document.getElementById("simulate-error");
    if (chk) chk.checked = true;
  }
  if (params.get("simulate_delay")) {
    const chk = document.getElementById("simulate-delay");
    if (chk) chk.checked = true;
  }

  try {
    const res = await fetch(`/api/jobs/${encodeURIComponent(jobId)}`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    const job = data.job;

    document.title = `${job.title} - Career Portal`;
    if (titleEl) titleEl.textContent = job.title;
    if (deptEl) deptEl.textContent = job.department;
    if (locationEl) locationEl.textContent = job.location;
    if (salaryEl) salaryEl.textContent = job.salary;
    if (expEl) expEl.textContent = job.experience;
    if (descEl) descEl.textContent = job.description;

    if (reqsEl) {
      reqsEl.innerHTML = "";
      (job.requirements || []).forEach((req) => {
        const li = document.createElement("li");
        li.textContent = req;
        reqsEl.appendChild(li);
      });
    }

    if (form) {
      form.addEventListener("submit", handleFormSubmission);
    }
  } catch (err) {
    if (titleEl) titleEl.textContent = "Position Not Found";
    if (descEl) descEl.textContent = `Unable to load details for job "${jobId}". It may have been closed or removed.`;
    if (form) form.style.display = "none";
  }
}

/**
 * Handle Application Form Submission
 */
async function handleFormSubmission(event) {
  event.preventDefault();

  const form = document.getElementById("application-form");
  const submitBtn = document.getElementById("submit-btn");
  const successAlert = document.getElementById("success-alert");
  const errorAlert = document.getElementById("error-alert");
  const errorHeading = document.getElementById("error-heading");
  const errorMessageText = document.getElementById("error-message-text");
  const successMessageText = document.getElementById("success-message-text");
  const applicationIdEl = document.getElementById("application-id");

  // Hide existing alerts
  if (successAlert) successAlert.classList.remove("visible");
  if (errorAlert) errorAlert.classList.remove("visible");

  // Clear previous errors
  clearValidationErrors();

  // Read field values
  const jobId = document.getElementById("jobId").value.trim();
  const fullName = document.getElementById("fullName").value;
  const email = document.getElementById("email").value;
  const phone = document.getElementById("phone").value;
  const resumeInput = document.getElementById("resume");
  const portfolioUrl = document.getElementById("portfolioUrl").value.trim();
  const coverNote = document.getElementById("coverNote").value.trim();

  // Validate fields
  let hasErrors = false;

  // Name validation: required, trimmed length 2-100
  const trimmedName = fullName.trim();
  if (!trimmedName) {
    setFieldError("fullName", "Full name is required.");
    hasErrors = true;
  } else if (trimmedName.length < 2 || trimmedName.length > 100) {
    setFieldError("fullName", "Full name must be between 2 and 100 characters.");
    hasErrors = true;
  }

  // Email validation: required, email regex
  const trimmedEmail = email.trim();
  if (!trimmedEmail) {
    setFieldError("email", "Email address is required.");
    hasErrors = true;
  } else if (!EMAIL_REGEX.test(trimmedEmail)) {
    setFieldError("email", "Please enter a valid email address (e.g. user@example.com).");
    hasErrors = true;
  }

  // Phone validation: required, phone regex
  const trimmedPhone = phone.trim();
  if (!trimmedPhone) {
    setFieldError("phone", "Phone number is required.");
    hasErrors = true;
  } else if (!PHONE_REGEX.test(trimmedPhone)) {
    setFieldError("phone", "Please enter a valid phone number (at least 10 digits).");
    hasErrors = true;
  }

  // Resume validation: required, file extension check
  if (!resumeInput.files || resumeInput.files.length === 0) {
    setFieldError("resume", "Resume file upload is required.");
    hasErrors = true;
  } else {
    const fileName = resumeInput.files[0].name;
    const isAllowed = ALLOWED_EXTENSIONS.some((ext) => fileName.toLowerCase().endsWith(ext));
    if (!isAllowed) {
      setFieldError("resume", "Resume must be a .pdf, .docx, .doc, or .txt file.");
      hasErrors = true;
    }
  }

  // Portfolio URL validation (optional)
  if (portfolioUrl && !URL_REGEX.test(portfolioUrl)) {
    setFieldError("portfolioUrl", "Please enter a valid URL starting with http:// or https://");
    hasErrors = true;
  }

  if (hasErrors) {
    return;
  }

  // Prepare submission payload
  const resumeFile = resumeInput.files[0];
  const payload = {
    jobId: jobId,
    fullName: trimmedName,
    email: trimmedEmail,
    phone: trimmedPhone,
    resumeFileName: resumeFile.name,
    coverNote: coverNote,
    portfolioUrl: portfolioUrl
  };

  // Check QA simulation controls
  const simulateErrorChk = document.getElementById("simulate-error");
  const simulateDelayChk = document.getElementById("simulate-delay");
  const isSimulateError = simulateErrorChk && simulateErrorChk.checked;
  const isSimulateDelay = simulateDelayChk && simulateDelayChk.checked;

  const headers = {
    "Content-Type": "application/json"
  };
  if (isSimulateError) {
    headers["X-Simulate-Error"] = "500";
  }
  if (isSimulateDelay) {
    headers["X-Simulate-Delay"] = "3";
  }

  // Disable button and show loading state to prevent rapid double-clicks
  submitBtn.disabled = true;
  const originalBtnText = submitBtn.textContent;
  submitBtn.textContent = "Submitting application...";

  try {
    const response = await fetch("/api/applications", {
      method: "POST",
      headers: headers,
      body: JSON.stringify(payload)
    });

    const result = await response.json().catch(() => ({}));

    if (response.status === 201) {
      // Success
      if (successAlert) {
        successAlert.classList.add("visible");
        if (applicationIdEl) applicationIdEl.textContent = result.applicationId;
        if (successMessageText) successMessageText.textContent = result.message;
      }
      form.reset();
      // Scroll to success banner
      successAlert.scrollIntoView({ behavior: "smooth", block: "center" });
    } else if (response.status === 409) {
      // Duplicate submission
      if (errorAlert) {
        errorAlert.classList.add("visible");
        if (errorHeading) errorHeading.textContent = "Duplicate Submission Detected";
        if (errorMessageText) {
          errorMessageText.textContent = result.message || "An application for this position has already been submitted with this email or phone number.";
        }
        errorAlert.scrollIntoView({ behavior: "smooth", block: "center" });
      }
    } else if (response.status === 422) {
      // Validation error from server
      if (result.details) {
        Object.entries(result.details).forEach(([field, msg]) => {
          setFieldError(field, msg);
        });
      }
      if (errorAlert) {
        errorAlert.classList.add("visible");
        if (errorHeading) errorHeading.textContent = "Validation Failed";
        if (errorMessageText) errorMessageText.textContent = "Please correct the highlighted errors above.";
      }
    } else {
      // Server error (500 or others)
      if (errorAlert) {
        errorAlert.classList.add("visible");
        if (errorHeading) errorHeading.textContent = `Server Error (${response.status})`;
        if (errorMessageText) {
          errorMessageText.textContent = result.error || "The server encountered an error while processing your application. Please try again later.";
        }
        errorAlert.scrollIntoView({ behavior: "smooth", block: "center" });
      }
    }
  } catch (networkError) {
    // Network failure / timeout
    if (errorAlert) {
      errorAlert.classList.add("visible");
      if (errorHeading) errorHeading.textContent = "Network Error";
      if (errorMessageText) {
        errorMessageText.textContent = "Unable to connect to the server. Please check your internet connection or verify the server status.";
      }
      errorAlert.scrollIntoView({ behavior: "smooth", block: "center" });
    }
  } finally {
    submitBtn.disabled = false;
    submitBtn.textContent = originalBtnText;
  }
}

function setFieldError(fieldId, message) {
  const input = document.getElementById(fieldId);
  const errorEl = document.getElementById(`error-${fieldId.toLowerCase()}`);
  if (input) input.classList.add("input-error");
  if (errorEl) {
    errorEl.textContent = message;
    errorEl.classList.add("visible");
  }
}

function clearValidationErrors() {
  document.querySelectorAll(".form-control").forEach((input) => {
    input.classList.remove("input-error");
  });
  document.querySelectorAll(".field-error-message").forEach((el) => {
    el.textContent = "";
    el.classList.remove("visible");
  });
}

function escapeHtml(str) {
  if (!str) return "";
  return str
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}
