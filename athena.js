/* =========================================================
   ATHENA — SIH26093
   FRONTEND APPLICATION
========================================================= */


/* =========================================================
   CONFIG
========================================================= */

const API_BASE_URL =
    "http://localhost:8000";


/* =========================================================
   STATE
========================================================= */

const state = {

    currentPage: "overview",

    selectedLanguage: "en",

    selectedDisclosure: "full",

    recording: false,

    cases: [],

    mapCases: [],

    mediaRecorder: null,

    audioChunks: []

};


/* =========================================================
   DOM HELPERS
========================================================= */

function $(selector) {
    return document.querySelector(selector);
}

function $$(selector) {
    return document.querySelectorAll(selector);
}


/* =========================================================
   PAGE NAVIGATION
========================================================= */

function showPage(pageName) {

    $$(".page").forEach(page => {
        page.classList.remove("active-page");
    });


    const page = $(`#page-${pageName}`);

    if (page) {
        page.classList.add("active-page");
    }


    $$(".nav-item").forEach(item => {

        item.classList.remove("active");

        if (item.dataset.page === pageName) {
            item.classList.add("active");
        }

    });


    state.currentPage = pageName;

    window.scrollTo({
        top: 0,
        behavior: "smooth"
    });


    if (pageName === "overview") {
    loadDashboard();
}

if (pageName === "cases") {
    renderCasesTable();
}

if (pageName === "risk-map") {
    loadRiskMap();
}

if (pageName === "alerts") {
    renderAlerts();
}
}


/* =========================================================
   NAVIGATION EVENTS
========================================================= */

$$(".nav-item").forEach(button => {

    button.addEventListener("click", () => {

        const page = button.dataset.page;

        showPage(page);

    });

});


$$("[data-page-target]").forEach(button => {

    button.addEventListener("click", () => {

        showPage(button.dataset.pageTarget);

    });

});


/* =========================================================
   LANGUAGE
========================================================= */

$$(".report-language-btn").forEach(button => {

    button.addEventListener("click", () => {

        $$(".report-language-btn").forEach(btn => {
            btn.classList.remove("active");
        });

        button.classList.add("active");

        const text = button.textContent.trim();

        if (text === "हिंदी") {
            state.selectedLanguage = "hi";
        }

        else if (text === "తెలుగు") {
            state.selectedLanguage = "te";
        }

        else {
            state.selectedLanguage = "en";
        }

    });

});


/* =========================================================
   MICROPHONE
========================================================= */

const micButton = $("#micButton");

if (micButton) {

    micButton.addEventListener("click", async () => {

        if (state.recording) {

            stopRecording();

        } else {

            startRecording();

        }

    });

}


/* =========================================================
   START RECORDING
========================================================= */

async function startRecording() {

    try {

        const stream =
            await navigator.mediaDevices.getUserMedia({
                audio: true
            });


        state.audioChunks = [];

        state.mediaRecorder =
            new MediaRecorder(stream);


        state.mediaRecorder.ondataavailable =
            event => {

                if (event.data.size > 0) {

                    state.audioChunks.push(
                        event.data
                    );

                }

            };


        state.mediaRecorder.onstop =
            async () => {

                stream
                    .getTracks()
                    .forEach(track => track.stop());


                const audioBlob =
                    new Blob(
                        state.audioChunks,
                        {
                            type: "audio/webm"
                        }
                    );


                await sendVoiceReport(audioBlob);

            };


        state.mediaRecorder.start();

        state.recording = true;

        micButton.classList.add("recording");

        $("#micStatus").textContent =
            "Listening… Tap again when finished";

    }

    catch (error) {

        console.error(error);

        $("#micStatus").textContent =
            "Microphone permission is needed";

    }

}


/* =========================================================
   STOP RECORDING
========================================================= */

function stopRecording() {

    if (
        state.mediaRecorder &&
        state.mediaRecorder.state !== "inactive"
    ) {

        state.mediaRecorder.stop();

    }


    state.recording = false;

    micButton.classList.remove("recording");

    $("#micStatus").textContent =
        "Sending your report…";

}


/* =========================================================
   SEND VOICE
========================================================= */

async function sendVoiceReport(audioBlob) {

    /*
        Backend endpoint may be updated by the team.

        Keep this function isolated so only the endpoint
        needs to change when API_CONTRACT.md is final.
    */

    try {

        const formData = new FormData();

        formData.append(
            "audio",
            audioBlob,
            "report.webm"
        );

        formData.append(
            "language",
            state.selectedLanguage
        );

        formData.append(
            "disclosure_level",
            state.selectedDisclosure
        );


        const response =
            await fetch(
                `${API_BASE_URL}/report`,
                {
                    method: "POST",
                    body: formData
                }
            );


        if (!response.ok) {
            throw new Error(
                `Server error: ${response.status}`
            );
        }


        const data =
            await response.json();


        console.log(
            "Voice report response:",
            data
        );


        showConfirmation();

    }

    catch (error) {

        console.error(
            "Voice report failed:",
            error
        );

        $("#micStatus").textContent =
            "Something went wrong. Please try again.";

    }

}


/* =========================================================
   TEXT REPORT
========================================================= */

const reportInput =
    $("#reportInput");

if (reportInput) {

    reportInput.addEventListener(
        "input",
        () => {

            const count =
                reportInput.value.length;

            $("#characterCount").textContent =
                `${count} / 3000`;

        }
    );

}


/* =========================================================
   SUBMIT TEXT REPORT
========================================================= */

const submitButton =
    $("#submitReportButton");

if (submitButton) {

    submitButton.addEventListener(
        "click",
        submitTextReport
    );

}


async function submitTextReport() {

    const text =
        reportInput.value.trim();


    if (!text) {

        reportInput.focus();

        return;

    }


    submitButton.disabled = true;

    submitButton.innerHTML =
        "Sending…";


    try {

        const response =
            await fetch(
                `${API_BASE_URL}/report`,
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify({

                        text: text,

                        language:
                            state.selectedLanguage,

                        disclosure_level:
                            state.selectedDisclosure

                    })

                }
            );


        if (!response.ok) {

            throw new Error(
                `Server error: ${response.status}`
            );

        }


        const data =
            await response.json();


        console.log(
            "Report response:",
            data
        );


        showConfirmation();

    }

    catch (error) {

        console.error(
            "Report submission failed:",
            error
        );

        alert(
            "Unable to send the report right now. Please try again."
        );

    }

    finally {

        submitButton.disabled = false;

        submitButton.innerHTML =
            "Send report <span>→</span>";

    }

}


/* =========================================================
   CONFIRMATION
========================================================= */

function showConfirmation() {

    showPage("confirmation");


    if (reportInput) {
        reportInput.value = "";
    }

}


/* =========================================================
   CASES
========================================================= */

async function loadCases() {

    try {

        const response =
            await fetch(
                `${API_BASE_URL}/cases`
            );


        if (!response.ok) {
            throw new Error("Cases request failed");
        }


        const data =
            await response.json();


        /*
            Supports either:

            [
                {...}
            ]

            OR

            {
                cases: [...]
            }
        */

        state.cases =
            Array.isArray(data)
                ? data
                : data.cases || [];


        renderCasesTable();

        renderOverviewCases();

        updateDashboardStats();

    }

    catch (error) {

        console.error(
            "Could not load cases:",
            error
        );

        state.cases = [];

        renderCasesTable();

        renderOverviewCases();

        updateDashboardStats();

    }

}


/* =========================================================
   CASE NORMALIZER
========================================================= */

function normalizeCase(item) {

    return {

        id:
            item.case_id ||
            item.id ||
            "—",

        incident:
            item.incident_type ||
            item.incident ||
            "General report",

        district:
            item.district ||
            item.location ||
            "—",

        risk:
            item.risk_tier ||
            item.risk?.risk_tier ||
            "Low",

        status:
            item.status ||
            (item.escalate
                ? "Escalated"
                : "Pending"),

        time:
            item.created_at ||
            item.timestamp ||
            "Recent"

    };

}


/* =========================================================
   CASE TABLE
========================================================= */

function renderCasesTable() {

    const body =
        $("#casesTableBody");

    if (!body) return;


    const search =
        ($("#caseSearch")?.value || "")
            .toLowerCase();


    const filter =
        $("#riskFilter")?.value ||
        "all";


    const cases =
        state.cases
            .map(normalizeCase)
            .filter(item => {

                const matchesSearch =
                    !search ||

                    item.id
                        .toLowerCase()
                        .includes(search) ||

                    item.incident
                        .toLowerCase()
                        .includes(search) ||

                    item.district
                        .toLowerCase()
                        .includes(search);


                const matchesRisk =
                    filter === "all" ||
                    item.risk === filter;


                return matchesSearch &&
                    matchesRisk;

            });


    if (!cases.length) {

        body.innerHTML = `
            <tr>
                <td colspan="6">
                    <div class="empty-state">
                        No cases available.
                    </div>
                </td>
            </tr>
        `;

        return;

    }


    body.innerHTML =
        cases.map(item => {

            const riskClass =
                item.risk
                    .toLowerCase()
                    .replace(" ", "-");


            return `
                <tr>

                    <td>
                        ${escapeHTML(item.id)}
                    </td>

                    <td>
                        ${escapeHTML(item.incident)}
                    </td>

                    <td>
                        ${escapeHTML(item.district)}
                    </td>

                    <td>
                        <span class="risk-tag ${riskClass}">
                            ${escapeHTML(item.risk)}
                        </span>
                    </td>

                    <td>
                        ${escapeHTML(item.status)}
                    </td>

                    <td>
                        ${formatTime(item.time)}
                    </td>

                </tr>
            `;

        }).join("");

}


/* =========================================================
   OVERVIEW CASES
========================================================= */

function renderOverviewCases() {

    const container =
        $("#overviewCases");

    if (!container) return;


    const cases =
        state.cases
            .map(normalizeCase)
            .slice(0, 5);


    if (!cases.length) {

        container.innerHTML = `
            <div class="empty-state">
                No recent cases.
            </div>
        `;

        return;

    }


    container.innerHTML =
        cases.map(item => {

            const riskClass =
                item.risk
                    .toLowerCase()
                    .replace(" ", "-");


            return `
                <div class="overview-case">

                    <strong>
                        ${escapeHTML(item.id)}
                    </strong>

                    <span>
                        ${escapeHTML(item.incident)}
                    </span>

                    <span>
                        ${escapeHTML(item.district)}
                    </span>

                    <span>
                        <span class="risk-tag ${riskClass}">
                            ${escapeHTML(item.risk)}
                        </span>
                    </span>

                </div>
            `;

        }).join("");

}


/* =========================================================
   DASHBOARD STATS
========================================================= */

function updateDashboardStats() {

    const cases =
        state.cases.map(normalizeCase);


    const total =
        cases.length;


    const critical =
        cases.filter(
            item => item.risk === "Critical"
        ).length;


    const high =
        cases.filter(
            item => item.risk === "High"
        ).length;


    const pending =
        cases.filter(
            item =>
                item.status === "Pending"
        ).length;


    setText(
        "#totalCases",
        total
    );

    setText(
        "#criticalCases",
        critical
    );

    setText(
        "#highCases",
        high
    );

    setText(
        "#pendingCases",
        pending
    );


    setText(
        "#riskTotal",
        total
    );


    const low =
        cases.filter(
            item => item.risk === "Low"
        ).length;


    const moderate =
        cases.filter(
            item => item.risk === "Moderate"
        ).length;


    setText(
        "#lowPercent",
        percentage(low, total)
    );

    setText(
        "#moderatePercent",
        percentage(moderate, total)
    );

    setText(
        "#highPercent",
        percentage(high, total)
    );

    setText(
        "#criticalPercent",
        percentage(critical, total)
    );


    setText(
        "#alertCount",
        critical + high
    );

}

/* =========================================================
   LOAD DASHBOARD STATS
========================================================= */

async function loadStats() {

    try {

        const response =
            await fetch(
                `${API_BASE_URL}/stats`
            );

        if (!response.ok) {

            throw new Error(
                "Stats request failed"
            );

        }

        const stats =
            await response.json();


        const total =
            stats.total_cases || 0;

        const critical =
            stats.by_risk_tier?.Critical || 0;

        const high =
            stats.by_risk_tier?.High || 0;

        const low =
            stats.by_risk_tier?.Low || 0;

        const moderate =
            stats.by_risk_tier?.Medium || 0;


        const pending =
            (stats.by_status?.New || 0) +
            (stats.by_status?.["Under Review"] || 0);


        /* =========================
           TOP STAT CARDS
        ========================= */

        setText(
            "#totalCases",
            total
        );

        setText(
            "#criticalCases",
            critical
        );

        setText(
            "#highCases",
            high
        );

        setText(
            "#pendingCases",
            pending
        );


        /* =========================
           RISK DISTRIBUTION
        ========================= */

        setText(
            "#riskTotal",
            total
        );

        setText(
            "#lowPercent",
            percentage(
                low,
                total
            )
        );

        setText(
            "#moderatePercent",
            percentage(
                moderate,
                total
            )
        );

        setText(
            "#highPercent",
            percentage(
                high,
                total
            )
        );

        setText(
            "#criticalPercent",
            percentage(
                critical,
                total
            )
        );


        /* =========================
           ALERT COUNT
        ========================= */

        setText(
            "#alertCount",
            critical + high
        );


        console.log(
            "Dashboard stats:",
            stats
        );

    }

    catch (error) {

        console.error(
            "Could not load dashboard stats:",
            error
        );

    }

}

/* =========================================================
   LOAD DASHBOARD
========================================================= */

async function loadDashboard() {

    await Promise.all([

        loadCases(),

        loadStats()

    ]);

}

/* =========================================================
   RISK MAP
========================================================= */

async function loadRiskMap() {

    const mapContainer =
        $("#districtMap");

    if (!mapContainer) return;


    try {

        const response =
            await fetch(
                `${API_BASE_URL}/cases/map`
            );


        if (!response.ok) {

            throw new Error(
                `Risk map request failed: ${response.status}`
            );

        }


        const data =
            await response.json();


        console.log(
            "Risk map data:",
            data
        );


        state.mapCases =
            Array.isArray(data)
                ? data
                : data.cases || data.data || [];


        renderRiskMap();

    }

    catch (error) {

        console.error(
            "Could not load risk map:",
            error
        );

        mapContainer.innerHTML = `
            <div class="map-error">
                Unable to load district risk data.
            </div>
        `;

    }

}


/* =========================================================
   RENDER RISK MAP
========================================================= */

function renderRiskMap() {

    const mapContainer =
        $("#districtMap");

    if (!mapContainer) return;


    if (!state.mapCases.length) {

        mapContainer.innerHTML = `
            <div class="map-empty">
                No district risk data available.
            </div>
        `;

        return;

    }


    mapContainer.innerHTML = `

        <div class="large-india">
            INDIA
        </div>

        <div class="map-data-label">
            ${state.mapCases.length} district case records
        </div>

    `;

}


/* =========================================================
   ALERTS
========================================================= */

function renderAlerts() {

    const container =
        $("#alertsContainer");

    if (!container) return;


    const alerts =
        state.cases
            .map(normalizeCase)
            .filter(
                item =>
                    item.risk === "Critical" ||
                    item.risk === "High"
            );


    if (!alerts.length) {

        container.innerHTML = `
            <div class="empty-alert">
                No priority alerts right now.
            </div>
        `;

        return;

    }


    container.innerHTML =
        alerts.map(item => {

            return `
                <div class="alert-card">

                    <div class="alert-icon">
                        !
                    </div>

                    <div>

                        <strong>
                            ${escapeHTML(item.risk)} priority case
                        </strong>

                        <p>
                            ${escapeHTML(item.id)}
                            ·
                            ${escapeHTML(item.district)}
                            ·
                            ${escapeHTML(item.incident)}
                        </p>

                    </div>

                </div>
            `;

        }).join("");

}


/* =========================================================
   SEARCH / FILTER
========================================================= */

$("#caseSearch")?.addEventListener(
    "input",
    renderCasesTable
);


$("#riskFilter")?.addEventListener(
    "change",
    renderCasesTable
);


$("#refreshCasesButton")?.addEventListener(
    "click",
    loadCases
);


/* =========================================================
   UTILITIES
========================================================= */

function setText(
    selector,
    value
) {

    const element =
        $(selector);

    if (element) {
        element.textContent = value;
    }

}


function percentage(
    value,
    total
) {

    if (!total) return "0%";

    return `${Math.round(
        (value / total) * 100
    )}%`;

}


function formatTime(value) {

    if (!value || value === "Recent") {
        return "Recent";
    }


    const date =
        new Date(value);


    if (Number.isNaN(date.getTime())) {
        return value;
    }


    return date.toLocaleString(
        [],
        {
            day: "2-digit",
            month: "short",
            hour: "2-digit",
            minute: "2-digit"
        }
    );

}


function escapeHTML(value) {

    return String(value)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");

}


/* =========================================================
   START
========================================================= */

document.addEventListener(
    "DOMContentLoaded",
    () => {

        showPage("overview");

        loadDashboard();

    }
);