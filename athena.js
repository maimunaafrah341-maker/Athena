/* ==========================================
   ATHENA FRONTEND
   Demo UI — backend integration later
========================================== */


/* ================= PAGE NAVIGATION ================= */

const pageTitles = {
    overview: "Campus overview",
    report: "Report an incident",
    map: "Campus safety map",
    routes: "Safe routes",
    alerts: "Safety alerts",
    reports: "My reports"
};

function showPage(pageId, clickedButton = null) {

    document.querySelectorAll(".page").forEach(page => {
        page.classList.remove("active-page");
    });

    const page = document.getElementById(pageId);

    if (page) {
        page.classList.add("active-page");
    }

    document.getElementById("pageTitle").textContent =
        pageTitles[pageId] || "Athena";

    document.querySelectorAll(".nav-item").forEach(item => {
        item.classList.remove("active");
    });

    if (clickedButton) {
        clickedButton.classList.add("active");
    } else {

        document.querySelectorAll(".nav-item").forEach(item => {

            const text = item.textContent.toLowerCase();

            if (
                (pageId === "overview" && text.includes("overview")) ||
                (pageId === "report" && text.includes("report an")) ||
                (pageId === "map" && text.includes("safety map")) ||
                (pageId === "routes" && text.includes("safe routes")) ||
                (pageId === "alerts" && text.includes("alerts")) ||
                (pageId === "reports" && text.includes("my reports"))
            ) {
                item.classList.add("active");
            }

        });
    }

    window.scrollTo({
        top: 0,
        behavior: "smooth"
    });
}


/* ================= REPORTING ================= */

async function submitReport() {

    const input = document.getElementById("reportInput");

    const message = input.value.trim();

    if (!message) {
        input.focus();
        return;
    }


    addUserMessage(message);

    input.value = "";

    showTyping();


        let data;

    try {

        const response = await fetch("http://localhost:8000/report", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                text: message,
                language: null
            })
        });

        data = await response.json();

    } catch (error) {

        console.error("Backend connection error:", error);

        removeTyping();

        const bubble = document.createElement("div");

        bubble.style.cssText = `
            display:flex;
            gap:10px;
            margin-top:25px;
        `;

        bubble.innerHTML = `
            <div class="chat-avatar">✦</div>

            <div>
                <span class="message-name">Athena</span>

                <div class="chat-bubble">
                    I couldn't connect to the safety intelligence system.
                    Please try again.
                </div>
            </div>
        `;

        document.getElementById("chatMessages").appendChild(bubble);

        scrollChat();

        return;
    }

    removeTyping();

    displayAnalysis(data);
}


/* ================= USER MESSAGE ================= */

function addUserMessage(message) {

    const container =
        document.getElementById("chatMessages");

    const messageElement =
        document.createElement("div");

    messageElement.style.cssText = `
        display:flex;
        justify-content:flex-end;
        margin-top:20px;
    `;

    messageElement.innerHTML = `
        <div style="
            max-width:75%;
            padding:14px 17px;
            background:#1E293B;
            color:white;
            border-radius:17px 17px 5px 17px;
            font-size:12px;
            line-height:1.6;
        ">
            ${escapeHTML(message)}
        </div>
    `;

    container.appendChild(messageElement);

    scrollChat();
}


/* ================= TYPING ================= */

function showTyping() {

    const container =
        document.getElementById("chatMessages");

    const typing =
        document.createElement("div");

    typing.id = "typingIndicator";

    typing.style.cssText = `
        display:flex;
        gap:10px;
        margin-top:22px;
        align-items:center;
    `;

    typing.innerHTML = `
        <div class="chat-avatar">✦</div>

        <div style="
            background:#F5F3FF;
            padding:13px 17px;
            border-radius:6px 16px 16px 16px;
            color:#777;
            font-size:10px;
        ">
            Athena is analysing your report...
        </div>
    `;

    container.appendChild(typing);

    scrollChat();
}


function removeTyping() {

    const typing =
        document.getElementById("typingIndicator");

    if (typing) {
        typing.remove();
    }
}


/* ================= ANALYSIS RESULT ================= */

function displayAnalysis(data) {

    const container =
        document.getElementById("chatMessages");


    const response =
        document.createElement("div");

    response.style.cssText = `
        display:flex;
        gap:10px;
        margin-top:25px;
    `;


    let citations = "";

    if (data.citations && data.citations.length) {

        citations = data.citations.map(citation => `
            <div style="
                padding:8px 10px;
                background:#F5F3FF;
                border-radius:8px;
                color:#6D45D8;
                font-size:8px;
                display:inline-block;
                margin:4px 4px 0 0;
            ">
                📄 ${escapeHTML(citation.source)}
				· page ${citation.page}
            </div>
        `).join("");
    }


    let escalation = "";

    if (data.escalate === true) {

        escalation = `
            <div style="
                margin-top:12px;
                padding:17px;
                background:#FFF1F3;
                border:1px solid #FECDD3;
                border-radius:15px;
            ">

                <div style="
                    display:flex;
                    gap:10px;
                    align-items:center;
                ">

                    <div style="
                        width:38px;
                        height:38px;
                        display:grid;
                        place-items:center;
                        border-radius:11px;
                        background:#FFE4E6;
                        color:#E11D48;
                    ">
                        !
                    </div>

                    <div>
                        <strong style="
                            display:block;
                            color:#9F1239;
                            font-size:12px;
                        ">
                            Human assistance recommended
                        </strong>

                        <span style="
                            display:block;
                            margin-top:3px;
                            color:#7F1D3D;
                            font-size:9px;
                        ">
                            This situation may need additional support.
                        </span>
                    </div>

                </div>

                <button
                    onclick="connectHuman()"
                    style="
                        width:100%;
                        margin-top:13px;
                        padding:11px;
                        border-radius:9px;
                        background:#E11D48;
                        color:white;
                        font-size:9px;
                        font-weight:700;
                    "
                >
                    CONNECT TO A HUMAN
                </button>

            </div>
        `;
    }


    response.innerHTML = `

        <div class="chat-avatar">✦</div>

        <div style="max-width:620px; width:100%;">

            <span style="
                font-size:8px;
                color:#8B5CF6;
                font-weight:800;
                letter-spacing:1px;
            ">
                ATHENA
            </span>


            <div style="
                margin-top:5px;
                padding:16px 18px;
                background:white;
                border:1px solid #E6E3EE;
                border-radius:6px 16px 16px 16px;
                box-shadow:0 8px 25px rgba(30,23,60,.05);
                font-size:11px;
                line-height:1.7;
            ">
               ${escapeHTML(
					data.response ??
					"This situation needs human review — no automated response was generated."
				)}
            </div>


            <!-- UNDERSTANDING -->

            <div style="
                margin-top:10px;
                background:white;
                border:1px solid #E6E3EE;
                border-radius:15px;
                overflow:hidden;
            ">

                <div style="
                    padding:12px 15px;
                    background:#F5F3FF;
                    display:flex;
                    justify-content:space-between;
                ">

                    <strong style="
                        color:#7565A5;
                        font-size:8px;
                        letter-spacing:1px;
                    ">
                        WHAT ATHENA UNDERSTOOD
                    </strong>

                    <span style="
                        color:#737B8C;
                        font-size:8px;
                    ">
                        ${data.incident.confidence}% confidence
                    </span>

                </div>


                <div style="
                    padding:14px;
                    display:grid;
                    grid-template-columns:1fr 1fr;
                    gap:8px;
                ">

                    <div class="result-info">
                        <small>INCIDENT</small>
                        <strong>
                            ${escapeHTML(data.incident.incident_type)}
                        </strong>
                    </div>

                    <div class="result-info">
                        <small>LOCATION</small>
                        <strong>
                            ${data.incident.location
								? escapeHTML(data.incident.location)
								: "Not identified"}
                        </strong>
                    </div>

                    <div class="result-info">
                        <small>IMMEDIATE DANGER</small>
                        <strong>
                            ${data.incident.immediate_danger
								? "Yes — attention needed"
								: "No immediate danger detected"}
                        </strong>
                    </div>

                    <div class="result-info">
                        <small>CONFIDENCE</small>
                        <strong>
                            ${data.incident.confidence}%
                        </strong>
                    </div>

                </div>

            </div>


            <!-- RISK -->

            <div style="
                margin-top:10px;
                padding:16px;
                background:${getRiskBackground(data.risk.risk_tier)};
                border:1px solid ${getRiskBorder(data.risk.risk_tier)};
                border-radius:15px;
            ">

                <div style="
                    display:flex;
                    justify-content:space-between;
                ">

                    <strong style="
                        color:${getRiskColor(data.risk.risk_tier)};
                        font-size:10px;
                        letter-spacing:1px;
                    ">
                        ${data.risk.risk_tier.toUpperCase()} RISK
                    </strong>

                    <span style="
                        font-size:8px;
                        color:#737B8C;
                    ">
                        AI assessment
                    </span>

                </div>

                <p style="
                    margin-top:7px;
                    color:#626978;
                    font-size:9px;
                    line-height:1.6;
                ">
                    ${escapeHTML(data.reason)}
                </p>

            </div>


            <!-- EVIDENCE -->

            <div style="margin-top:10px;">

                <div style="
                    font-size:8px;
                    font-weight:800;
                    color:#8B5CF6;
                    letter-spacing:1px;
                ">
                    VERIFIED EVIDENCE
                </div>

                <div style="margin-top:3px;">
                    ${citations}
                </div>

            </div>


            ${escalation}

        </div>
    `;


    container.appendChild(response);

    scrollChat();
}


/* ================= RISK HELPERS ================= */

function getRiskColor(risk) {

    switch (risk) {

        case "Critical":
        case "High":
            return "#E11D48";

        case "Medium":
            return "#B45309";

        case "Low":
            return "#047857";

        default:
            return "#8B5CF6";
    }
}


function getRiskBackground(risk) {

    switch (risk) {

        case "Critical":
        case "High":
            return "#FFF1F3";

        case "Medium":
            return "#FFFBEB";

        case "Low":
            return "#ECFDF5";

        default:
            return "#F5F3FF";
    }
}


function getRiskBorder(risk) {

    switch (risk) {

        case "Critical":
        case "High":
            return "#FECDD3";

        case "Medium":
            return "#FDE68A";

        case "Low":
            return "#A7F3D0";

        default:
            return "#DDD6FE";
    }
}


/* ================= ROUTES ================= */

function calculateRoute() {

    const results =
        document.getElementById("routeResults");

    results.innerHTML = `
        <div style="
            padding:20px;
            background:white;
            border:1px solid #E6E3EE;
            border-radius:16px;
            text-align:center;
            color:#737B8C;
            font-size:11px;
        ">
            ✦ Athena is analysing reported safety patterns...
        </div>
    `;

    setTimeout(() => {

        results.innerHTML = `
            <div class="route-card">

                <div class="route-icon safe-route">✓</div>

                <div class="route-main">

                    <div class="route-title">
                        <strong>Safer route</strong>
                        <span class="recommended">RECOMMENDED</span>
                    </div>

                    <p>
                        Avoids the current high-risk zone.
                    </p>

                    <div class="route-meta">
                        <span>⌁ 12 min</span>
                        <span>↓ Lower reported risk</span>
                    </div>

                </div>

                <button>
                    Start route →
                </button>

            </div>
        `;

    }, 1000);
}


/* ================= HUMAN HELP ================= */

function connectHuman() {

    alert(
        "Human assistance would open here. " +
        "Your backend/team can later connect this to the escalation system."
    );
}


function emergencyHelp() {

    alert(
        "Emergency assistance workflow will be connected here."
    );
}


/* ================= VOICE / LOCATION ================= */

function voiceComingSoon() {

    alert(
        "Voice reporting will be connected through the multilingual/voice module."
    );
}


function locationComingSoon() {

    alert(
        "Location sharing will be connected to the campus safety map."
    );
}


/* ================= UTILITIES ================= */

function delay(ms) {

    return new Promise(resolve => {
        setTimeout(resolve, ms);
    });
}


function scrollChat() {

    const chat =
        document.getElementById("chatMessages");

    chat.scrollTo({
        top: chat.scrollHeight,
        behavior: "smooth"
    });
}


function escapeHTML(text) {

    const div =
        document.createElement("div");

    div.textContent = text ?? "";

    return div.innerHTML;
}