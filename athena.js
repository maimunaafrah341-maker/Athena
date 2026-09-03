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

// Pages that show real case data and therefore need the key -- New
// Report and Confirmation are deliberately absent: the README always
// described dashboard.html as "the report form + counsellor
// dashboard (needs ADMIN_API_KEY to unlock case data)," but the gate
// used to block the entire document at script-load regardless of
// page, which meant a citizen with no key couldn't even reach the
// report form. showPage() below is what actually enforces this now;
// the key is checked per-navigation, not once at load.
const ADMIN_PAGES = new Set(["overview", "cases", "risk-map", "guidance", "alerts"]);

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
//
// The submitted value is checked against the server (GET /stats, the
// cheapest admin-gated route) before it's ever written to localStorage
// or the overlay is dismissed. Earlier this just accepted any non-empty
// string -- the overlay would close and the dashboard shell would
// render (empty, since every fetch underneath 401s and quietly falls
// back to []), which reads exactly like "it worked" to anyone who
// doesn't know to expect real numbers. Validating up front means a
// wrong key now visibly fails right here instead of silently degrading
// three screens later.
//
// targetPage is remembered in sessionStorage (survives the reload
// submit() does) so a counsellor who tapped "Cases" from Overview
// lands back on Cases, not dumped back to the default page. A citizen
// who reaches this by mistake (e.g. tapping the wrong nav item) isn't
// trapped here either -- "Back to report form" just re-shows New
// Report without touching the gate at all.
function showAdminKeyGate(targetPage) {

    if (targetPage) {
        sessionStorage.setItem("athena_admin_redirect", targetPage);
    }

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

            <p class="admin-gate-error" id="adminGateError" hidden></p>

            <button type="button" id="adminGateSubmit" class="primary-button">
                Continue
            </button>

            <button type="button" id="adminGateBack" class="text-button" style="margin-top: 10px;">
                ← Back to report form
            </button>

        </div>
    `;

    document.body.appendChild(overlay);

    overlay.querySelector("#adminGateBack").addEventListener("click", () => {
        sessionStorage.removeItem("athena_admin_redirect");
        overlay.remove();
        showPage("new-report");
    });

    const input = overlay.querySelector("#adminGateInput");
    const errorEl = overlay.querySelector("#adminGateError");
    const button = overlay.querySelector("#adminGateSubmit");

    const showError = message => {
        errorEl.textContent = message;
        errorEl.hidden = false;
    };

    const submit = async () => {

        const value = input.value.trim();

        if (!value) return;

        errorEl.hidden = true;
        button.disabled = true;
        button.textContent = "Checking...";

        try {

            const response = await fetch(`${API_BASE_URL}/stats`, {
                headers: { "X-API-Key": value }
            });

            if (response.status === 401 || response.status === 403) {
                showError("Invalid access key -- check with your team lead.");
                return;
            }

            if (!response.ok) {
                showError(
                    `Backend error (${response.status}) -- couldn't verify this key right now.`
                );
                return;
            }

            localStorage.setItem("athena_admin_key", value);

            window.location.reload();

        } catch (error) {

            console.error("Admin key verification failed:", error);

            showError("Couldn't reach the Athena backend -- check your connection and try again.");

        } finally {

            button.disabled = false;
            button.textContent = "Continue";

        }

    };

    button.addEventListener("click", submit);

    input.addEventListener("keydown", event => {
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

    // Set from /cases/map's k-anonymity response -- how many reports
    // were withheld, and the threshold that withheld them.
    mapSuppressed: 0,
    mapMinGroupSize: 0,

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

    if (ADMIN_PAGES.has(pageName) && !ADMIN_API_KEY) {
        showAdminKeyGate(pageName);
        return;
    }

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


        showConfirmation(data);

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


// Shared status line for the submit and SOS flows. role="status" on the
// element means anything set here is announced by a screen reader
// without stealing focus -- which a bare alert() never did, on top of
// blocking the page and losing the message once dismissed.
function setReportStatus(message, isError) {

    const statusEl = $("#reportStatus");

    if (!statusEl) return;

    if (!message) {
        statusEl.hidden = true;
        statusEl.textContent = "";
        statusEl.classList.remove("is-error");
        return;
    }

    statusEl.hidden = false;
    statusEl.textContent = message;
    statusEl.classList.toggle("is-error", Boolean(isError));

    // On failure, offer the retry as an actual control rather than
    // only telling someone to "try again" -- the typed text is still
    // in the textarea untouched, so this genuinely resends it.
    if (isError) {

        const retryButton = document.createElement("button");

        retryButton.type = "button";
        retryButton.className = "status-retry";
        retryButton.textContent = t("status.retry");

        retryButton.addEventListener("click", () => {
            setReportStatus(null);
            submitTextReport();
        });

        statusEl.appendChild(retryButton);

    }

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

    setReportStatus(t("status.sending"), false);


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

        setReportStatus(null);

        showConfirmation(data);

    }

    catch (error) {

        console.error(
            "Report submission failed:",
            error
        );

        // Deliberately does NOT clear the textarea -- whatever was
        // typed stays exactly where it is, so a failed send is a retry
        // rather than asking someone in distress to type it all again.
        setReportStatus(t("status.error"), true);

    }

    finally {

        submitButton.disabled = false;

        if (submitLabel) {
            submitLabel.textContent = t("submit.send");
        }

    }

}


/* =========================================================
   SOS / QUICK EXIT
========================================================= */

// One-tap SOS: unlike the regular submit flow, this is meant to work
// even when there's nothing typed -- pressing it is itself the
// strongest possible signal (see app.py's /sos docstring, which
// forces Critical/Escalated regardless of what the text says).
// Geolocation is attempted but never required: a denied or
// unavailable permission still sends the SOS, just without a
// location attached, since real emergencies don't wait on a location
// prompt.
const sosButton = $("#sosButton");
const sosButtonLabel = $("#sosButtonLabel");

if (sosButton) {

    sosButton.addEventListener("click", () => {

        sosButton.disabled = true;
        if (sosButtonLabel) sosButtonLabel.textContent = t("safety.sosSending");

        const text = reportInput ? reportInput.value.trim() : "";

        const sendSos = (latitude, longitude) => {

            fetch(`${API_BASE_URL}/sos`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    text: text || null,
                    language: state.selectedLanguage,
                    latitude: latitude,
                    longitude: longitude,
                    disclosure_level: state.selectedDisclosure,
                    channel: state.selectedChannel
                })
            })
                .then(response => {
                    if (!response.ok) {
                        throw new Error(`Server error: ${response.status}`);
                    }
                    return response.json();
                })
                .then(data => {
                    showConfirmation(data);
                })
                .catch(error => {
                    console.error("SOS failed:", error);
                    alert(t("safety.sosError"));
                })
                .finally(() => {
                    sosButton.disabled = false;
                    if (sosButtonLabel) sosButtonLabel.textContent = t("safety.sos");
                });

        };

        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(
                position => sendSos(position.coords.latitude, position.coords.longitude),
                () => sendSos(null, null),
                { timeout: 5000 }
            );
        } else {
            sendSos(null, null);
        }

    });

}


// Quick exit: clear anything visibly typed first (synchronous, so it
// happens even if the navigation below is slow), then leave the site
// immediately via replace() rather than href/assign, so the browser's
// back button lands wherever the reporter was before Athena, not on
// this page.
const quickExitButton = $("#quickExitButton");

if (quickExitButton) {

    quickExitButton.addEventListener("click", () => {

        if (reportInput) reportInput.value = "";
        state.evidenceFile = null;

        window.location.replace("https://www.google.com");

    });

}


/* =========================================================
   CONFIRMATION
========================================================= */

function setFollowUpStatus(message, isError) {

    const statusEl = $("#followUpStatus");

    if (!statusEl) return;

    statusEl.hidden = !message;
    statusEl.textContent = message || "";
    statusEl.classList.toggle("is-error", Boolean(isError));

}


$("#confirmFollowUp")?.addEventListener("submit", async event => {

    event.preventDefault();

    const form = event.currentTarget;
    const caseId = form.dataset.caseId;
    const selected = form.querySelector("input[name='followUp']:checked");

    if (!caseId || !selected) return;

    const submitButton = $("#followUpSubmit");
    const noteInput = $("#followUpNote");

    if (submitButton) submitButton.disabled = true;

    try {

        const response = await fetch(
            `${API_BASE_URL}/cases/${caseId}/follow-up`,
            {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    preference: selected.value,
                    note: (noteInput && noteInput.value.trim()) || null,
                    token: form.dataset.followUpToken || null
                })
            }
        );

        if (!response.ok) {
            throw new Error(`Server error: ${response.status}`);
        }

        setFollowUpStatus(t("followup.saved"), false);

        // The endpoint only accepts one answer per case (see app.py) --
        // so once it's saved, close the form rather than leaving
        // controls that would now fail with a 409.
        form.querySelectorAll("input, button").forEach(el => {
            el.disabled = true;
        });

    } catch (error) {

        console.error("Could not save follow-up preference:", error);

        setFollowUpStatus(t("followup.error"), true);

        if (submitButton) submitButton.disabled = false;

    }

});


function showConfirmation(data) {

    showPage("confirmation");


    if (reportInput) {
        reportInput.value = "";
    }

    renderConfirmationDetail(data || null);

}


// Fills in what the pipeline actually decided for THIS report --
// previously this card was 100% static regardless of risk tier, so a
// Critical report and a Low one showed the identical "Help is on the
// way" text and everything the backend computed (the AI's grounded
// response, applicable law, response SLA, real emergency contacts)
// was fetched, logged to the console, and thrown away. Athena never
// actually dispatches police itself -- risk.py's RESPONSE_PROTOCOL is
// documented as staff-facing routing metadata, not a live ERSS-112
// integration -- so Critical/High tiers get told plainly to call 112
// themselves rather than a false "help is on the way" promise.
function renderConfirmationDetail(data) {

    const urgentBox = $("#confirmUrgent");
    const helpBox = $("#confirmHelpBox");
    const responseText = $("#confirmResponseText");
    const legalBox = $("#confirmLegal");
    const contactsBox = $("#confirmContacts");
    const referenceEl = $("#confirmReference");
    const followUpForm = $("#confirmFollowUp");

    if (!urgentBox || !helpBox || !responseText || !legalBox || !contactsBox) {
        return;
    }

    if (referenceEl) {
        referenceEl.hidden = true;
        referenceEl.textContent = "";
    }

    if (followUpForm) {
        followUpForm.hidden = true;
        followUpForm.reset();
        setFollowUpStatus(null);
    }

    urgentBox.hidden = true;
    urgentBox.innerHTML = "";
    helpBox.hidden = false;
    responseText.hidden = true;
    responseText.textContent = "";
    legalBox.hidden = true;
    legalBox.innerHTML = "";
    contactsBox.hidden = true;
    contactsBox.innerHTML = "";

    if (!data) {
        return;
    }

    const riskTier = data.risk ? data.risk.risk_tier : null;
    const protocol = data.risk ? data.risk.response_protocol : null;
    const isUrgent = riskTier === "Critical" || riskTier === "High";

    // Something to quote when calling back. Prefers the NHAA docket id
    // (the reference an actual helpline case is tracked under) and
    // falls back to the internal case number when no docket was cut.
    const referenceId =
        (data.nhaa_docket && data.nhaa_docket.docket_id) ||
        (data.case_id != null ? `#${data.case_id}` : null);

    if (referenceEl && referenceId) {
        referenceEl.hidden = false;
        referenceEl.textContent = `${t("confirm.reference")}: ${referenceId}`;
    }

    // Only offered when there's a case to attach it to -- a failed or
    // unsaved report has nothing for the preference to belong to.
    //
    // The token comes back with the report and is the only proof this
    // browser is the one that filed it (see app.py's _follow_up_token),
    // so it's carried on the form rather than re-derived or looked up.
    if (followUpForm && data.case_id != null) {
        followUpForm.hidden = false;
        followUpForm.dataset.caseId = data.case_id;
        followUpForm.dataset.followUpToken = data.follow_up_token || "";
    }

    if (isUrgent) {

        helpBox.hidden = true;
        urgentBox.hidden = false;

        urgentBox.innerHTML = `
            <a href="tel:112" class="urgent-call">
                📞 ${escapeHTML(t("confirm.urgentCall"))}
            </a>
            <p>${escapeHTML(t("confirm.urgentSub"))}</p>
            ${
                protocol
                    ? `<p class="urgent-sla">${escapeHTML(t("confirm.slaLabel"))}: ${escapeHTML(protocol.sla)}</p>`
                    : ""
            }
        `;

    }

    // The AI's own grounded response, already in whatever language the
    // report came in and already crisis-safe-filtered when suicidal
    // ideation was detected (see response_engine.py's
    // crisis_instructions / _filter_evidence_for_crisis) -- not run
    // through t(), since it's the pipeline's own generated text, not a
    // UI label.
    if (data.response) {
        responseText.hidden = false;
        responseText.textContent = data.response;
    }

    // Real applicable law from kg.py's knowledge graph, shown as "may
    // fall under" -- advisory routing information for a human, never a
    // legal determination (see kg.get_legal_guidance's docstring).
    const legal = data.legal_guidance;

    if (legal && legal.applicable_provisions && legal.applicable_provisions.length) {

        legalBox.hidden = false;

        legalBox.innerHTML = `
            <strong>${escapeHTML(t("confirm.legalTitle"))}</strong>
            <ul>
                ${
                    legal.applicable_provisions.map(provision => `
                        <li>
                            <strong>${escapeHTML(provision.act)} — ${escapeHTML(provision.section)}</strong>
                            <br>
                            ${escapeHTML(provision.description)}
                        </li>
                    `).join("")
                }
            </ul>
        `;

    }

    // Real contacts, not AI-generated: data.emergency_contacts is
    // computed deterministically by emergency_contacts.py from risk/
    // stress tier alone (pipeline.py's _finalize), so it's present
    // even when no location was shared -- includes KIRAN automatically
    // whenever stress tier is Critical/High, regardless of whether the
    // report text used the word "suicide." data.nearby_help (only
    // present when the reporter shared a location) adds real, named
    // nearby police stations/hospitals on top.
    const contacts = [
        ...(data.emergency_contacts || []),
        ...(data.nearby_help || []).slice(0, 3).map(place => ({
            label: `${place.name} (${place.distance_km} km)`,
            phone: place.phone
        }))
    ];

    if (contacts.length) {

        contactsBox.hidden = false;

        contactsBox.innerHTML = `
            <strong>${escapeHTML(t("confirm.contactsTitle"))}</strong>
            <ul>
                ${
                    contacts.map(contact => `
                        <li>
                            ${escapeHTML(contact.label)}
                            ${
                                contact.phone
                                    ? ` — <a href="tel:${escapeHTML(contact.phone)}">${escapeHTML(contact.phone)}</a>`
                                    : ""
                            }
                        </li>
                    `).join("")
                }
            </ul>
        `;

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
            "Recent",

        acknowledged:
            Boolean(item.acknowledged),

        // Why the pipeline flagged this -- already computed and stored
        // per case, just never surfaced in the alert list, which meant
        // every row said "Critical priority case" and nothing about
        // what made it critical.
        reason:
            item.reason || null

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


    // Urgency cue: how long has this case sat since its last real
    // action? For an Escalated case that's measured from the escalation
    // event itself (not just "last timeline entry"), since a status
    // change or note after escalating still leaves the underlying
    // "has anyone actually responded to the escalation" question open.
    const lastEvent =
        timeline.length
            ? timeline[timeline.length - 1]
            : null;

    const lastEscalatedEvent =
        [...timeline].reverse().find(
            event => event.event_type === "escalated"
        ) ||
        null;

    const isEscalated =
        (brief.status || "").toLowerCase() === "escalated";

    const urgencyReference =
        isEscalated && lastEscalatedEvent
            ? lastEscalatedEvent.created_at
            : (lastEvent ? lastEvent.created_at : brief.first_reported);

    const urgencyElapsedLabel =
        formatElapsed(urgencyReference);

    const urgencyMinutes =
        urgencyReference
            ? (Date.now() - new Date(urgencyReference).getTime()) / 60000
            : null;

    let urgencyTier = "normal";

    if (isEscalated && urgencyMinutes != null) {
        urgencyTier =
            urgencyMinutes >= 60
                ? "critical"
                : urgencyMinutes >= 15
                    ? "watch"
                    : "ok";
    }

    const noUpdateSinceEscalation =
        isEscalated &&
        lastEscalatedEvent &&
        lastEvent &&
        lastEscalatedEvent.id === lastEvent.id;

    const urgencyText =
        isEscalated
            ? `Escalated ${urgencyElapsedLabel}` +
              (noUpdateSinceEscalation ? " — no update since" : "")
            : urgencyElapsedLabel
                ? `Last activity: ${urgencyElapsedLabel}`
                : null;


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
                urgencyText
                    ? `
                        <div class="case-brief-urgency urgency-${urgencyTier}">
                            ${escapeHTML(urgencyText)}
                        </div>
                      `
                    : ""
            }


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
                    ${
                        brief.language
                            ? `<span class="lang-tag">${escapeHTML(brief.language)}</span>`
                            : ""
                    }
                </span>

                <p class="case-summary">
                    ${escapeHTML(
                        brief.summary ||
                        "No summary available."
                    )}
                </p>

                ${
                    brief.summary_translated
                        ? `
                            <div class="case-translation">

                                <span class="eyebrow">
                                    ENGLISH TRANSLATION
                                    <span class="ai-badge">Machine translation — original above is authoritative</span>
                                </span>

                                <p class="case-summary">
                                    ${escapeHTML(brief.summary_translated)}
                                </p>

                            </div>
                          `
                        : ""
                }

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
                <span class="ai-badge">
                    Suggested — not final
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
                // Only offered when the case is actually in another
                // language -- on an English case this would be a box
                // that translates English into English.
                brief.language &&
                !["en", "eng", "english"].includes(String(brief.language).toLowerCase())
                    ? `
                        <div class="case-brief-section">

                            <span class="eyebrow">
                                DRAFT A REPLY
                                <span class="ai-badge">Machine translation — read before you use it</span>
                            </span>

                            <p class="reply-help">
                                Write in English. This gives you the same words in
                                ${escapeHTML(String(brief.language).toUpperCase())} to
                                use on a call or message — Athena does not send it.
                            </p>

                            <div class="case-action-row">
                                <textarea
                                    id="replyDraftInput"
                                    placeholder="e.g. A counsellor will call you tomorrow morning. You are not alone."
                                ></textarea>
                                <button
                                    type="button"
                                    id="translateReplyButton"
                                    class="secondary-button"
                                >
                                    Translate
                                </button>
                            </div>

                            <div id="replyDraftOutput" class="reply-output" hidden></div>

                        </div>
                      `
                    : ""
            }


            ${
                signals.length
                    ? `
                        <div class="case-brief-section">

                            <span class="eyebrow">
                                STRESS / TRAUMA SIGNALS
                            </span>
                            <span class="ai-badge">
                                Suggested — not final
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
                            <span class="ai-badge">
                                Suggested — verify before citing
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
                            <span class="ai-badge">
                                Suggested — counsellor discretion applies
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


    /* Reply drafting -- translate only, never send. Deliberately does
       not reload the brief afterwards: the draft is not case data and
       there is nothing new on the server to fetch. */

    overlay
        .querySelector("#translateReplyButton")
        ?.addEventListener("click", async () => {

            const button = overlay.querySelector("#translateReplyButton");
            const input = overlay.querySelector("#replyDraftInput");
            const output = overlay.querySelector("#replyDraftOutput");

            const text = input?.value.trim();

            if (!text || !output) return;

            button.disabled = true;
            button.textContent = "Translating...";

            output.hidden = false;
            output.textContent = "Translating…";
            output.classList.remove("is-error");

            try {

                const response = await fetch(
                    `${API_BASE_URL}/cases/${brief.case_id}/translate-reply`,
                    {
                        method: "POST",
                        headers: {
                            "Content-Type": "application/json",
                            "X-API-Key": ADMIN_API_KEY
                        },
                        body: JSON.stringify({ note: text })
                    }
                );

                if (!response.ok) {
                    throw new Error(`Server error: ${response.status}`);
                }

                const data = await response.json();

                if (!data.translated) {

                    output.classList.add("is-error");
                    output.textContent =
                        data.reason === "already_english"
                            ? "This case was reported in English — no translation needed."
                            : "Couldn't translate that right now. Please try again.";

                    return;

                }

                // Rendered as text, not innerHTML -- this string came
                // back from a model and is about to sit in a
                // counsellor's browser alongside real case data.
                output.textContent = data.translated;

            } catch (error) {

                console.error("Could not translate reply:", error);

                output.classList.add("is-error");
                output.textContent =
                    "Couldn't translate that right now. Please try again.";

            } finally {

                button.disabled = false;
                button.textContent = "Translate";

            }

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
                : data.pins || data.cases || data.data || [];

        // How many reports the backend withheld because too few share
        // an area to be anonymous (see cases._suppress_sparse_locations).
        // Surfaced rather than swallowed: a map quietly missing pins
        // reads as "nothing happened here", which is the opposite of
        // what a sparse, high-risk district means.
        state.mapSuppressed = data && !Array.isArray(data)
            ? (data.suppressed || 0)
            : 0;

        state.mapMinGroupSize = data && !Array.isArray(data)
            ? (data.min_group_size || 0)
            : 0;

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

    // "Nothing to draw" and "everything there was got withheld to
    // protect identity" are different situations and must not look
    // identical -- the second one means there ARE reports here.
    const suppressedNotice =
        state.mapSuppressed
            ? `
                <div class="map-suppressed-note">
                    ${escapeHTML(String(state.mapSuppressed))}
                    ${state.mapSuppressed === 1 ? "report is" : "reports are"}
                    hidden from this map — fewer than
                    ${escapeHTML(String(state.mapMinGroupSize))}
                    reports in their area, so a pin could identify who filed it.
                    They are still counted in case totals and alerts.
                </div>
              `
            : "";

    if (!state.mapCases.length) {

        mapContainer.innerHTML = `
            <div class="map-empty">
                ${
                    state.mapSuppressed
                        ? "No pins can be shown without risking identifying a reporter."
                        : "No district risk data available."
                }
            </div>
            ${suppressedNotice}
        `;

        return;

    }


    /* Create Leaflet container */

    mapContainer.innerHTML = `
        <div
            id="liveRiskMap"
            style="width:100%; height:100%; min-height:520px;"
        ></div>
        ${suppressedNotice}
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

// Review state outranks severity here, which is the opposite of what
// this sort did first. A reviewed Critical case has already been
// picked up by somebody; an unreviewed High case has not been seen at
// all. Sorting purely by tier pushed handled work above unhandled
// work, which is precisely how the case nobody has looked at gets
// missed -- the thing this queue exists to prevent.
//
// So: everything needing review first, ordered by severity, then
// everything already reviewed, also ordered by severity.
const ALERT_RISK_ORDER = { "Critical": 0, "High": 1, "Medium": 2, "Low": 3 };

function alertRank(item) {
    return ALERT_RISK_ORDER[item.risk] ?? 99;
}

// Categories come from the cases actually present rather than a fixed
// list, so a new incident_type from understanding.py shows up here
// without anyone remembering to add it.
function populateAlertCategories(normalizedCases) {

    const select = $("#alertCategoryFilter");

    if (!select) return;

    const categories =
        [...new Set(normalizedCases.map(item => item.incident).filter(Boolean))]
            .sort();

    const current = select.value;

    const wanted =
        ["all", ...categories].join("|");

    // Only rebuild when the option set actually changed -- otherwise
    // every refresh would reset the counsellor's current selection
    // mid-triage.
    if (select.dataset.builtFor === wanted) return;

    select.innerHTML =
        `<option value="all">All categories</option>` +
        categories.map(
            category =>
                `<option value="${escapeHTML(category)}">${escapeHTML(category)}</option>`
        ).join("");

    select.dataset.builtFor = wanted;

    if (current && [...select.options].some(o => o.value === current)) {
        select.value = current;
    }

}


function renderAlerts() {

    const container =
        $("#alertsContainer");

    if (!container) return;


    const reviewFilter = $("#alertReviewFilter")?.value || "unreviewed";
    const priorityFilter = $("#alertPriorityFilter")?.value || "escalating";
    const categoryFilter = $("#alertCategoryFilter")?.value || "all";

    const normalized = state.cases.map(normalizeCase);

    populateAlertCategories(normalized);

    const alerts =
        normalized
            .filter(item => {

                if (priorityFilter === "escalating") {
                    if (item.risk !== "Critical" && item.risk !== "High") return false;
                } else if (priorityFilter !== "all") {
                    if (item.risk !== priorityFilter) return false;
                }

                if (reviewFilter === "unreviewed" && item.acknowledged) return false;
                if (reviewFilter === "reviewed" && !item.acknowledged) return false;

                if (categoryFilter !== "all" && item.incident !== categoryFilter) return false;

                return true;

            })
            .sort((a, b) => {

                // Unreviewed before reviewed, severity within each.
                const reviewDiff =
                    Number(a.acknowledged) - Number(b.acknowledged);

                if (reviewDiff !== 0) return reviewDiff;

                return alertRank(a) - alertRank(b);

            });


    const countEl = $("#alertResultCount");

    if (countEl) {
        countEl.textContent =
            alerts.length === 1
                ? "1 case"
                : `${alerts.length} cases`;
    }


    if (!alerts.length) {

        container.innerHTML = `
            <div class="empty-alert">
                ${
                    reviewFilter === "unreviewed"
                        ? "Nothing waiting for review with these filters."
                        : "No cases match these filters."
                }
            </div>
        `;

        return;

    }


    container.innerHTML =
        alerts.map(item => {

            const elapsed = formatElapsed(item.time);

            return `
                <div class="alert-card tier-${escapeHTML(String(item.risk).toLowerCase())} ${item.acknowledged ? "is-acknowledged" : ""}">

                    <div class="alert-icon" aria-hidden="true">
                        !
                    </div>

                    <div class="alert-body">

                        <strong>
                            <span class="alert-priority priority-${escapeHTML(item.risk.toLowerCase())}">
                                ${escapeHTML(item.risk)} priority
                            </span>
                            <span class="alert-case-id">${escapeHTML(item.id)}</span>
                        </strong>

                        <p class="alert-meta">
                            ${escapeHTML(item.district)}
                            ·
                            ${escapeHTML(item.incident)}
                            ·
                            <span class="alert-status">${escapeHTML(item.status)}</span>
                            ${elapsed ? `· ${escapeHTML(elapsed)}` : ""}
                        </p>

                        ${
                            item.reason
                                ? `<p class="alert-reason">${escapeHTML(item.reason)}</p>`
                                : ""
                        }

                    </div>

                    <div class="alert-actions">

                        <button type="button" class="alert-view-button" data-view-case="${escapeHTML(item.id)}">
                            ${escapeHTML(t("alerts.viewCase"))}
                        </button>

                        ${
                            item.acknowledged
                                ? `<span class="alert-ack-badge">✓ ${escapeHTML(t("alerts.reviewedBadge"))}</span>`
                                : `<button type="button" class="alert-ack-button" data-ack-case="${escapeHTML(item.id)}">${escapeHTML(t("alerts.markReviewed"))}</button>`
                        }

                    </div>

                </div>
            `;

        }).join("");

}


["#alertReviewFilter", "#alertPriorityFilter", "#alertCategoryFilter"].forEach(
    selector => {
        $(selector)?.addEventListener("change", renderAlerts);
    }
);

$("#alertResetFilters")?.addEventListener("click", () => {

    const review = $("#alertReviewFilter");
    const priority = $("#alertPriorityFilter");
    const category = $("#alertCategoryFilter");

    if (review) review.value = "unreviewed";
    if (priority) priority.value = "escalating";
    if (category) category.value = "all";

    renderAlerts();

});


$("#alertsContainer")?.addEventListener("click", async event => {

    // Reuses the same case-brief panel the Cases table opens -- an
    // alert that can't be acted on without hunting for the case in
    // another tab isn't much of a priority queue.
    const viewButton = event.target.closest("[data-view-case]");

    if (viewButton) {
        openCaseBrief(viewButton.dataset.viewCase);
        return;
    }

    const button = event.target.closest("[data-ack-case]");

    if (!button) return;

    const caseId = button.dataset.ackCase;

    button.disabled = true;
    button.textContent = "Marking...";

    try {

        const response = await fetch(
            `${API_BASE_URL}/cases/${caseId}/acknowledge`,
            {
                method: "POST",
                headers: { "X-API-Key": ADMIN_API_KEY }
            }
        );

        if (!response.ok) {
            throw new Error(`Server error: ${response.status}`);
        }

        const updatedCase = await response.json();

        // Patch the one case in place rather than a full loadCases()
        // round trip -- keeps the rest of the list stable for whoever
        // is mid-review instead of jumping/reloading under them.
        const index = state.cases.findIndex(
            item => item.id === updatedCase.id
        );

        if (index !== -1) {
            state.cases[index] = updatedCase;
        }

        renderAlerts();
        renderCasesTable();

    } catch (error) {

        console.error("Could not acknowledge case:", error);

        button.disabled = false;
        button.textContent = "Mark reviewed";

    }

});


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


function formatElapsed(value) {

    if (!value) {
        return null;
    }


    const date =
        new Date(value);


    if (Number.isNaN(date.getTime())) {
        return null;
    }


    const minutes =
        Math.floor((Date.now() - date.getTime()) / 60000);


    if (minutes < 1) {
        return "just now";
    }

    if (minutes < 60) {
        return `${minutes}m ago`;
    }

    const hours =
        Math.floor(minutes / 60);

    if (hours < 24) {
        return `${hours}h ${minutes % 60}m ago`;
    }

    const days =
        Math.floor(hours / 24);

    return `${days}d ago`;

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

        // A returning counsellor (key already in localStorage) picks
        // up where a gate redirect left off, or lands on Overview as
        // before. A citizen with no key yet -- the common case for
        // dashboard.html's report-form half -- lands on New Report
        // instead of hitting a login wall on the very first paint.
        const redirectPage = sessionStorage.getItem("athena_admin_redirect");
        sessionStorage.removeItem("athena_admin_redirect");

        const initialPage =
            redirectPage && ADMIN_API_KEY
                ? redirectPage
                : ADMIN_API_KEY
                    ? "overview"
                    : "new-report";

        showPage(initialPage);

        // The NHAA channel tag is counsellor bookkeeping, not a
        // question a self-reporting citizen can meaningfully answer --
        // only shown once a key is present (see dashboard.html's
        // comment on #channelSelectorGroup). A key entered later
        // reloads the page anyway (see showAdminKeyGate), so this
        // check only ever needs to run once, here.
        const channelSelectorGroup = document.getElementById("channelSelectorGroup");
        if (channelSelectorGroup) {
            channelSelectorGroup.hidden = !ADMIN_API_KEY;
        }

        document.getElementById("sidebarExit")?.addEventListener(
            "click",
            () => { window.location.href = "/"; }
        );

    }
);