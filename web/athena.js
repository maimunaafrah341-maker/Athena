/* =========================================================
   ATHENA — SIH26093
   FRONTEND APPLICATION
========================================================= */


/* =========================================================
   CONFIG
========================================================= */

// Relative path -> same origin the page was served from, whether
// that's a local backend or the deployed one. Do not hardcode a host
// here.
const API_BASE_URL = "";

// Never hardcode the real admin key in a shipped file -- this is a
// public repo, so anything written here is permanently visible in git
// history to anyone, and it gates every case endpoint (real reporter
// text, legal guidance, SVI). Kept only in localStorage, not in
// source, and persists per browser (not per tab -- opening a new tab
// or reloading doesn't ask again).
//
// Two ways in, so a link handed to someone else (e.g. a judge, from a
// PDF) doesn't dead-end on a raw browser prompt():
//   1. ?key=... in the URL -- consumed into localStorage below, then
//      stripped from the address bar so it doesn't linger visibly.
//      Whoever controls that link controls admin access, same trust
//      level as the key itself -- don't publish a link carrying a key
//      you're not fine with the recipient having indefinitely.
//   2. showAdminKeyGate() below, a proper in-page screen instead of
//      prompt() -- shown once if neither of the above already set one.
const _urlParams = new URLSearchParams(window.location.search);
const _keyFromUrl = _urlParams.get("key");

if (_keyFromUrl) {

    localStorage.setItem("athena_admin_key", _keyFromUrl);

    _urlParams.delete("key");

    const _cleanQuery = _urlParams.toString();

    window.history.replaceState(
        {},
        "",
        window.location.pathname +
            (_cleanQuery ? `?${_cleanQuery}` : "") +
            window.location.hash
    );

}

const ADMIN_API_KEY = localStorage.getItem("athena_admin_key");

if (!ADMIN_API_KEY) {
    showAdminKeyGate();
}

/* =========================================================
   ADMIN KEY GATE
========================================================= */

// A full-page screen in place of prompt() -- every fetch call below
// still fires with a null/blank key and 401s (already handled by each
// call's existing catch block, so nothing crashes), but this overlay
// visually blocks the rest of the UI until a key is entered. Submitting
// reloads the page rather than trying to hot-swap ADMIN_API_KEY (a
// const, and already captured in every closure that reads it) --
// simplest correct fix, and this only happens once per browser.
function showAdminKeyGate() {

    const overlay = document.createElement("div");

    overlay.className = "admin-gate-overlay";

    overlay.innerHTML = `
        <div class="admin-gate-card">

            <div class="brand-symbol" style="margin: 0 auto 14px;">A</div>

            <h2>Counsellor / Admin Access</h2>

            <p>
                This dashboard handles real reporter data, so it's
                gated behind an access key. Enter the one you were
                given to continue.
            </p>

            <input
                type="password"
                id="adminGateInput"
                placeholder="Access key"
                autofocus
            />

            <button type="button" id="adminGateSubmit" class="primary-button">
                Continue
            </button>

        </div>
    `;

    document.body.appendChild(overlay);

    const submit = () => {

        const value = overlay.querySelector("#adminGateInput").value.trim();

        if (!value) return;

        localStorage.setItem("athena_admin_key", value);

        window.location.reload();

    };

    overlay.querySelector("#adminGateSubmit").addEventListener("click", submit);

    overlay.querySelector("#adminGateInput").addEventListener("keydown", event => {
        if (event.key === "Enter") submit();
    });

}

/* =========================================================
   STATE
========================================================= */

const state = {

    currentPage: "overview",

    selectedLanguage: "en",

    selectedDisclosure: "full",

    selectedChannel: "portal",

    recording: false,

    cases: [],

    mapCases: [],

    mediaRecorder: null,

    audioChunks: [],

    evidenceFile: null

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

// data-lang on these buttons drives both the NLU language tag AND the
// UI chrome's language (setUiLanguage, from i18n.js) -- a reporter
// picking Telugu here expects everything they see to switch to
// Telugu, not just the eventual response. onUiLanguageChange (below)
// keeps this in sync the other way, if the language is instead
// changed via the topbar switcher.
$$(".report-language-btn[data-lang]").forEach(button => {

    button.addEventListener("click", () => {

        $$(".report-language-btn[data-lang]").forEach(btn => {
            btn.classList.remove("active");
        });

        button.classList.add("active");

        state.selectedLanguage = button.dataset.lang || "en";

        if (typeof setUiLanguage === "function") {
            setUiLanguage(state.selectedLanguage);
        }

    });

});

// Keeps the New Report page's language buttons in sync when the
// language is changed from the topbar switcher instead (e.g. a
// counsellor switching UI language before a reporter has touched New
// Report at all).
window.onUiLanguageChange = function (lang) {

    state.selectedLanguage = lang;

    $$(".report-language-btn[data-lang]").forEach(btn => {
        btn.classList.toggle("active", btn.dataset.lang === lang);
    });

};


/* =========================================================
   NHAA CHANNEL
========================================================= */

$$(".channel-options .report-language-btn").forEach(button => {

    button.addEventListener("click", () => {

        $$(".channel-options .report-language-btn").forEach(btn => {
            btn.classList.remove("active");
        });

        button.classList.add("active");

        state.selectedChannel = button.dataset.channel || "portal";

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
            t("voice.listening");

    }

    catch (error) {

        console.error(error);

        $("#micStatus").textContent =
            t("voice.micPermission");

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
        t("voice.sending");

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

        // Field name/shape must match /report/voice's actual signature
        // (file: UploadFile, language: Form(str)) -- this was
        // previously posting to /report (which expects a JSON body
        // with a required "text" field, not multipart audio) under a
        // field name ("audio") that endpoint never even declared, so
        // the mic button always failed with a 422 before this fix.
        // disclosure_level/channel aren't accepted by /report/voice
        // yet -- dropped here rather than sent and silently ignored;
        // voice reports default to full disclosure / the 14566_voice
        // channel until that endpoint is extended to take them.
        formData.append(
            "file",
            audioBlob,
            "report.webm"
        );

        formData.append(
            "language",
            state.selectedLanguage
        );


        const response =
            await fetch(
                `${API_BASE_URL}/report/voice`,
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
            t("voice.error");

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


/* =========================================================
   EVIDENCE ATTACHMENT
========================================================= */

// Alternative input mode, same relationship as voice-vs-text: /report
// (typed text) and /report/image (OCR'd photo) are separate backend
// endpoints that don't combine into one call, so attaching a photo
// submits via /report/image instead of /report, same as recording
// voice submits via /report/voice instead. See app.py's /report/image
// docstring -- this endpoint already existed and worked, it just had
// no UI anywhere to reach it from until now.
const evidenceAttachButton = $("#evidenceAttachButton");
const evidenceFileInput = $("#evidenceFileInput");
const evidenceFileName = $("#evidenceFileName");

if (evidenceAttachButton && evidenceFileInput) {

    evidenceAttachButton.addEventListener("click", () => {
        evidenceFileInput.click();
    });

    evidenceFileInput.addEventListener("change", () => {

        const file = evidenceFileInput.files[0] || null;

        state.evidenceFile = file;

        if (evidenceFileName) {
            evidenceFileName.textContent = file ? file.name : "";
        }

    });

}


async function submitTextReport() {

    const text =
        reportInput.value.trim();

    const evidenceFile = state.evidenceFile;


    if (!text && !evidenceFile) {

        reportInput.focus();

        return;

    }


    submitButton.disabled = true;

    const submitLabel = $("#submitReportLabel");
    if (submitLabel) {
        submitLabel.textContent = t("submit.sending");
    }


    try {

        // A photo is an alternative input mode, not combined with
        // typed text (see the EVIDENCE ATTACHMENT section above) --
        // if one's attached, it takes priority and goes through OCR
        // instead of the typed text being sent as-is.
        const response = evidenceFile
            ? await fetch(
                `${API_BASE_URL}/report/image`,
                {
                    method: "POST",
                    body: (() => {
                        const formData = new FormData();
                        formData.append("file", evidenceFile);
                        formData.append("language", state.selectedLanguage || "en");
                        return formData;
                    })()
                }
            )
            : await fetch(
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
                            state.selectedDisclosure,

                        channel:
                            state.selectedChannel

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


        state.evidenceFile = null;
        if (evidenceFileInput) evidenceFileInput.value = "";
        if (evidenceFileName) evidenceFileName.textContent = "";

        showConfirmation();

    }

    catch (error) {

        console.error(
            "Report submission failed:",
            error
        );

        alert(
            t("report.submitError")
        );

    }

    finally {

        submitButton.disabled = false;

        if (submitLabel) {
            submitLabel.textContent = t("submit.send");
        }

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
        `${API_BASE_URL}/cases`,
        {
            headers: {
                "X-API-Key": ADMIN_API_KEY
            }
        }
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
                : "New"),

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

                    String(item.id)
                        .toLowerCase()
                        .includes(search) ||

                    String(item.incident)
                        .toLowerCase()
                        .includes(search) ||

                    String(item.district)
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
                <tr
                    class="case-row"
                    data-case-id="${escapeHTML(item.id)}"
                    title="View case brief"
                >

                    <td>
                        <strong>
                            ${escapeHTML(item.id)}
                        </strong>
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


    /* Add click handlers */

    body
        .querySelectorAll(".case-row")
        .forEach(row => {

            row.addEventListener(
                "click",
                () => {

                    const caseId =
                        row.dataset.caseId;

                    if (caseId) {

                        openCaseBrief(caseId);

                    }

                }
            );

        });

}

/* =========================================================
   CASE BRIEF
========================================================= */

async function openCaseBrief(caseId) {

    try {

        const response =
            await fetch(
                `${API_BASE_URL}/cases/${caseId}/brief`,
                {
                    headers: {
                        "X-API-Key": ADMIN_API_KEY
                    }
                }
            );


        if (!response.ok) {

            throw new Error(
                `Case brief request failed: ${response.status}`
            );

        }


        const brief =
            await response.json();


        console.log(
            "Case brief:",
            brief
        );


        showCaseBrief(brief);

    }

    catch (error) {

        console.error(
            "Could not load case brief:",
            error
        );

        alert(
            "Unable to load the case details."
        );

    }

}

/* =========================================================
   CASE ACTIONS (escalate / status / notes)
========================================================= */

async function postCaseAction(url, body, method = "POST") {

    try {

        const response =
            await fetch(url, {
                method,
                headers: {
                    "X-API-Key": ADMIN_API_KEY,
                    "Content-Type": "application/json",
                },
                body: JSON.stringify(body),
            });

        if (!response.ok) {
            throw new Error(`Case action failed: ${response.status}`);
        }

        return await response.json();

    }

    catch (error) {

        console.error("Case action failed:", error);

        alert("That action couldn't be saved. Please try again.");

        return null;

    }

}

/* =========================================================
   SHOW CASE BRIEF
========================================================= */

function showCaseBrief(brief) {

    /* Remove existing panel */

    document
        .querySelector(".case-brief-overlay")
        ?.remove();


    const risk =
        brief.risk_tier ||
        "Low";


    const riskClass =
        risk
            .toLowerCase()
            .replace(" ", "-");


    const sviScore =
        brief.svi_score ??
        "—";


    const confidence =
        brief.confidence != null
            ? `${Number(brief.confidence).toFixed(0)}%`
            : "—";


    const signals =
        brief.svi_explainability?.text_signals ||
        [];


    const legalSteps =
        brief.legal_guidance?.procedural_next_steps ||
        [];


    const provisions =
        brief.legal_guidance?.applicable_provisions ||
        [];


    const docket =
        brief.nhaa_docket ||
        null;


    const timeline =
        brief.timeline ||
        [];


    const CHANNEL_LABELS = {
        "14566_voice": "14566 Voice Call",
        "ivrs": "IVRS",
        "portal": "Integrated Portal",
        "chatbot": "Chatbot",
        "mobile_app": "Mobile App",
    };


    // Kept in sync with cases.py's VALID_STATUSES by hand -- that
    // tuple isn't exposed over the API anywhere, so this is a
    // deliberate, small duplication rather than an extra round trip
    // just to populate a dropdown.
    const CASE_STATUSES = [
        "New", "Under Review", "Escalated",
        "In Progress", "Resolved", "Closed",
    ];


    const TIMELINE_LABELS = {
        reported: "Report received",
        status_changed: "Status changed",
        escalated: "Escalated",
        note_added: "Note added",
    };


    const overlay =
        document.createElement("div");


    overlay.className =
        "case-brief-overlay";


    overlay.innerHTML = `

        <div class="case-brief-panel">

            <div class="case-brief-header">

                <div>

                    <span class="eyebrow">
                        CASE BRIEF
                    </span>

                    <h2>
                        Case #${escapeHTML(
                            brief.case_id
                        )}
                    </h2>

                    <p>
                        ${escapeHTML(
                            brief.incident_type ||
                            "General report"
                        )}
                    </p>

                </div>


                <button
                    class="case-brief-close"
                    type="button"
                    aria-label="Close"
                >
                    ×
                </button>

            </div>


            ${
                docket
                    ? `
                        <div class="case-brief-section">

                            <span class="eyebrow">
                                NHAA DOCKET
                            </span>

                            <p class="case-summary">
                                <strong>${escapeHTML(docket.docket_id || "—")}</strong>
                                &nbsp;·&nbsp;
                                ${escapeHTML(CHANNEL_LABELS[docket.channel] || docket.channel || "—")}
                                &nbsp;·&nbsp;
                                ${escapeHTML(
                                    docket.status === "escalated"
                                        ? "Auto-escalated"
                                        : "Logged"
                                )}
                            </p>

                        </div>
                      `
                    : ""
            }


            <div class="case-brief-risk">

                <div>

                    <span class="brief-label">
                        RISK LEVEL
                    </span>

                    <span class="
                        risk-tag
                        ${riskClass}
                    ">
                        ${escapeHTML(risk)}
                    </span>

                </div>


                <div>

                    <span class="brief-label">
                        RISK SCORE
                    </span>

                    <strong>
                        ${brief.risk_score ?? "—"}
                    </strong>

                </div>


                <div>

                    <span class="brief-label">
                        SVI SCORE
                    </span>

                    <strong>
                        ${sviScore}
                    </strong>

                </div>


                <div>

                    <span class="brief-label">
                        CONFIDENCE
                    </span>

                    <strong>
                        ${confidence}
                    </strong>

                </div>

            </div>


            <div class="case-brief-section">

                <span class="eyebrow">
                    REPORT
                </span>

                <p class="case-summary">
                    ${escapeHTML(
                        brief.summary ||
                        "No summary available."
                    )}
                </p>

            </div>


            <div class="case-brief-grid">

                <div class="brief-info">

                    <span>District</span>

                    <strong>
                        ${escapeHTML(
                            brief.district ||
                            "—"
                        )}
                    </strong>

                </div>


                <div class="brief-info">

                    <span>Language</span>

                    <strong>
                        ${escapeHTML(
                            brief.language ||
                            "—"
                        )}
                    </strong>

                </div>


                <div class="brief-info">

                    <span>Status</span>

                    <strong>
                        ${escapeHTML(
                            brief.status ||
                            "—"
                        )}
                    </strong>

                </div>


                <div class="brief-info">

                    <span>SOS</span>

                    <strong>
                        ${
                            brief.is_sos
                                ? "Yes"
                                : "No"
                        }
                    </strong>

                </div>

            </div>


            <div class="case-brief-section">

                <span class="eyebrow">
                    AI ASSESSMENT
                </span>

                <p class="brief-reason">
                    ${escapeHTML(
                        brief.reason ||
                        "No assessment explanation available."
                    )}
                </p>

            </div>


            <div class="case-brief-section">

                <span class="eyebrow">
                    ACTIONS
                </span>

                <div class="case-action-row">
                    <input
                        type="text"
                        id="escalateNoteInput"
                        placeholder="Optional note (e.g. who's being notified)"
                    />
                    <button
                        type="button"
                        id="escalateNowButton"
                        class="primary-button escalate-button"
                    >
                        Escalate now
                    </button>
                </div>

                <div class="case-action-row">
                    <select id="statusSelect">
                        ${
                            CASE_STATUSES.map(status => `
                                <option value="${status}" ${status === brief.status ? "selected" : ""}>
                                    ${status}
                                </option>
                            `).join("")
                        }
                    </select>
                    <button
                        type="button"
                        id="updateStatusButton"
                        class="secondary-button"
                    >
                        Update status
                    </button>
                </div>

                <div class="case-action-row">
                    <textarea
                        id="caseNoteInput"
                        placeholder="Add a note (e.g. context from a follow-up call)"
                    ></textarea>
                    <button
                        type="button"
                        id="addNoteButton"
                        class="secondary-button"
                    >
                        Add note
                    </button>
                </div>

            </div>


            ${
                signals.length
                    ? `
                        <div class="case-brief-section">

                            <span class="eyebrow">
                                STRESS / TRAUMA SIGNALS
                            </span>

                            <div class="brief-list">

                                ${
                                    signals.map(signal => `
                                        <div class="brief-list-item">

                                            <strong>
                                                ${escapeHTML(
                                                    signal.label ||
                                                    signal.signal ||
                                                    "Signal"
                                                )}
                                            </strong>

                                            <span>
                                                ${signal.points ?? 0} points
                                            </span>

                                        </div>
                                    `).join("")
                                }

                            </div>

                        </div>
                      `
                    : ""
            }


            ${
                provisions.length
                    ? `
                        <div class="case-brief-section">

                            <span class="eyebrow">
                                LEGAL GUIDANCE
                            </span>

                            <div class="brief-list">

                                ${
                                    provisions.map(item => `
                                        <div class="brief-list-item">

                                            <div>

                                                <strong>
                                                    ${escapeHTML(
                                                        item.act ||
                                                        "Applicable provision"
                                                    )}
                                                </strong>

                                                <p>
                                                    ${escapeHTML(
                                                        item.section ||
                                                        ""
                                                    )}
                                                </p>

                                            </div>

                                        </div>
                                    `).join("")
                                }

                            </div>

                        </div>
                      `
                    : ""
            }


            ${
                legalSteps.length
                    ? `
                        <div class="case-brief-section">

                            <span class="eyebrow">
                                PROCEDURAL NEXT STEPS
                            </span>

                            <div class="brief-steps">

                                ${
                                    legalSteps.map(step => `
                                        <div class="brief-step">

                                            <span>
                                                ${step.step ?? ""}
                                            </span>

                                            <p>
                                                ${escapeHTML(
                                                    step.action ||
                                                    ""
                                                )}
                                            </p>

                                        </div>
                                    `).join("")
                                }

                            </div>

                        </div>
                      `
                    : ""
            }


            ${
                timeline.length
                    ? `
                        <div class="case-brief-section">

                            <span class="eyebrow">
                                TIMELINE
                            </span>

                            <div class="case-timeline">

                                ${
                                    timeline.map(event => `
                                        <div class="case-timeline-item event-${escapeHTML(event.event_type)}">

                                            <span class="timeline-dot"></span>

                                            <div class="timeline-body">

                                                <strong>
                                                    ${escapeHTML(TIMELINE_LABELS[event.event_type] || event.event_type)}
                                                </strong>

                                                ${
                                                    event.note
                                                        ? `<p>${escapeHTML(event.note)}</p>`
                                                        : ""
                                                }

                                                <time>${formatTime(event.created_at)}</time>

                                            </div>

                                        </div>
                                    `).join("")
                                }

                            </div>

                        </div>
                      `
                    : ""
            }


            <div class="case-brief-footer">

                <span>
                    First reported:
                    ${formatTime(
                        brief.first_reported
                    )}
                </span>

                <button
                    class="primary-button case-brief-close-button"
                    type="button"
                >
                    Close
                </button>

            </div>

        </div>

    `;


    document.body.appendChild(overlay);


    /* Actions: escalate / status change / add note -- each posts to
       the backend, then reloads the case list (so the table/stats
       reflect the change) and re-opens this same case's brief to show
       the updated status/timeline. */

    overlay
        .querySelector("#escalateNowButton")
        ?.addEventListener("click", async () => {

            const note = overlay.querySelector("#escalateNoteInput")?.value.trim();

            const result = await postCaseAction(
                `${API_BASE_URL}/cases/${brief.case_id}/escalate`,
                { note: note || null }
            );

            const contact = result?.escalation_contact;

            if (contact) {
                alert(
                    `Escalated. Notify the ${contact.district} Sakhi/OSC` +
                    (contact.contact_person ? ` (${contact.contact_person})` : "") +
                    `: ${contact.contact_person_phone || contact.phone || "no phone on file"}`
                );
            } else if (result) {
                alert("Escalated. No district contact on file for this case -- check the district contacts list manually.");
            }

            await loadCases();
            openCaseBrief(brief.case_id);

        });

    overlay
        .querySelector("#updateStatusButton")
        ?.addEventListener("click", async () => {

            const status = overlay.querySelector("#statusSelect")?.value;

            await postCaseAction(
                `${API_BASE_URL}/cases/${brief.case_id}/status`,
                { status },
                "PATCH"
            );

            await loadCases();
            openCaseBrief(brief.case_id);

        });

    overlay
        .querySelector("#addNoteButton")
        ?.addEventListener("click", async () => {

            const note = overlay.querySelector("#caseNoteInput")?.value.trim();

            if (!note) return;

            await postCaseAction(
                `${API_BASE_URL}/cases/${brief.case_id}/notes`,
                { note }
            );

            await loadCases();
            openCaseBrief(brief.case_id);

        });


    /* Close buttons */

    overlay
        .querySelectorAll(
            ".case-brief-close, .case-brief-close-button"
        )
        .forEach(button => {

            button.addEventListener(
                "click",
                () => overlay.remove()
            );

        });


    /* Close by clicking outside */

    overlay.addEventListener(
        "click",
        event => {

            if (
                event.target === overlay
            ) {

                overlay.remove();

            }

        }
    );

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
            // "New" is the real status a just-created, non-escalated
            // case starts at (see cases.py's create_case()) -- this
            // used to check for "Pending", a status that's never
            // actually assigned, so this card silently always read 0.
            item =>
                item.status === "New"
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
            // risk_tier's real value is "Medium", not "Moderate" --
            // that's svi_tier's naming, a different field entirely
            // (see svi.py). This was silently undercounting every
            // medium-risk case out of every tier bucket.
            item => item.risk === "Medium"
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
        `${API_BASE_URL}/stats`,
        {
            headers: {
                "X-API-Key": ADMIN_API_KEY
            }
        }
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

let riskMap = null;
let riskMarkers = [];


async function loadRiskMap() {

    const mapContainer = $("#districtMap");

    if (!mapContainer) return;

    try {

        const response = await fetch(
            `${API_BASE_URL}/cases/map`
        );

        if (!response.ok) {
            throw new Error(
                `Risk map request failed: ${response.status}`
            );
        }

        const data = await response.json();

        console.log("Risk map data:", data);

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
   RENDER REAL LEAFLET MAP
========================================================= */

function renderRiskMap() {

    const mapContainer = $("#districtMap");

    if (!mapContainer) return;


    /* Remove previous map */

    if (riskMap) {

        riskMap.remove();

        riskMap = null;
        riskMarkers = [];

    }


    /* Empty state */

    if (!state.mapCases.length) {

        mapContainer.innerHTML = `
            <div class="map-empty">
                No district risk data available.
            </div>
        `;

        return;

    }


    /* Create Leaflet container */

    mapContainer.innerHTML = `
        <div
            id="liveRiskMap"
            style="width:100%; height:100%; min-height:520px;"
        ></div>
    `;


    /* Check Leaflet */

    if (typeof L === "undefined") {

        console.error("Leaflet is not loaded.");

        mapContainer.innerHTML = `
            <div class="map-error">
                Map library could not be loaded.
            </div>
        `;

        return;

    }


    /* Create map */

    riskMap = L.map("liveRiskMap", {
        zoomControl: true
    }).setView(
        [20.5937, 78.9629],
        5
    );


    /* OpenStreetMap */

    L.tileLayer(
        "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
        {
            maxZoom: 18,
            attribution:
                '&copy; OpenStreetMap contributors'
        }
    ).addTo(riskMap);


    /* =====================================================
       RISK MARKERS
    ===================================================== */

    state.mapCases.forEach(caseItem => {

        const latitude =
            Number(caseItem.latitude);

        const longitude =
            Number(caseItem.longitude);


        /* Ignore cases without coordinates */

        if (
            !Number.isFinite(latitude) ||
            !Number.isFinite(longitude)
        ) {
            return;
        }


        const risk =
            String(
                caseItem.risk_tier || "Low"
            ).toLowerCase();


        /* Risk colour */

        let markerColor;

        if (risk === "critical") {

            markerColor = "#8f4141";

        }

        else if (risk === "high") {

            markerColor = "#a95c4d";

        }

        else if (risk === "medium") {

            // risk_tier's real value from /cases/map is "Medium" --
            // this was checking "moderate" (that's svi_tier's scale,
            // a different axis), so every medium-risk pin was
            // silently falling through to the green low-risk color.
            markerColor = "#a8763c";

        }

        else {

            markerColor = "#4c8060";

        }


        /* Custom circular marker */

        const markerIcon =
            L.divIcon({

                className: "risk-marker-wrapper",

                html: `
                    <div
                        class="risk-marker"
                        style="
                            --marker-color:${markerColor};
                        "
                    >
                        <span></span>
                    </div>
                `,

                iconSize: [22, 22],

                iconAnchor: [11, 11],

                popupAnchor: [0, -12]

            });


        /* Create marker */

        const marker =
            L.marker(
                [latitude, longitude],
                {
                    icon: markerIcon
                }
            ).addTo(riskMap);


        /* Popup */

        marker.bindPopup(`

            <div class="risk-popup">

                <div class="risk-popup-top">

                    <span
                        class="risk-popup-tag"
                        style="
                            color:${markerColor};
                        "
                    >
                        ${escapeHTML(
                            caseItem.risk_tier || "Low"
                        )}
                    </span>

                    ${
                        caseItem.is_sos
                            ? `
                                <span class="risk-popup-sos">
                                    SOS
                                </span>
                              `
                            : ""
                    }

                </div>


                <strong class="risk-popup-title">
                    Case #${escapeHTML(caseItem.id)}
                </strong>


                <div class="risk-popup-row">

                    <span>Incident</span>

                    <strong>
                        ${escapeHTML(
                            caseItem.incident_type ||
                            "General"
                        )}
                    </strong>

                </div>


                <div class="risk-popup-row">

                    <span>Coordinates</span>

                    <strong>
                        ${latitude.toFixed(3)},
                        ${longitude.toFixed(3)}
                        ${
                            caseItem.location_source === "district_approx"
                                ? " (approx.)"
                                : ""
                        }
                    </strong>

                </div>

                ${
                    caseItem.location_source === "district_approx"
                        ? `
                            <div class="risk-popup-row">
                                <span></span>
                                <em style="font-size:11px;opacity:0.75;">
                                    District-level location, not exact GPS
                                </em>
                            </div>
                          `
                        : ""
                }


                <div class="risk-popup-status">

                    ${
                        caseItem.is_sos
                            ? "Immediate attention required"
                            : "Reported case"
                    }

                </div>

            </div>

        `);


        riskMarkers.push(marker);

    });


    /* =====================================================
       FIT MAP TO CASES
    ===================================================== */

    if (riskMarkers.length === 1) {

        riskMap.setView(
            riskMarkers[0].getLatLng(),
            12
        );

    }

    else if (riskMarkers.length > 1) {

        const bounds =
            L.featureGroup(
                riskMarkers
            ).getBounds();


        riskMap.fitBounds(
            bounds,
            {
                padding: [50, 50],
                maxZoom: 12
            }
        );

    }


    /* =====================================================
       FIX LEAFLET SIZE
    ===================================================== */

    setTimeout(() => {

        if (riskMap) {

            riskMap.invalidateSize();

        }

    }, 250);

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

        document.getElementById("sidebarExit")?.addEventListener(
            "click",
            () => { window.location.href = "/"; }
        );

    }
);