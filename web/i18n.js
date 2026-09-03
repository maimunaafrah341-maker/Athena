/* =========================================================
   ATHENA — UI LOCALIZATION
   ---------------------------------------------------------
   Translates the interface chrome itself (nav labels, buttons,
   hints, confirmations) -- a separate concern from understanding.py's
   NLU, which already handles the *complaint text* in any supported
   language. Judge feedback 2026-08-29: the report form still assumed
   English literacy even though the NLU behind it didn't -- a reporter
   who can't read "Tell us what happened..." never gets far enough to
   type in Hindi/Telugu at all. This closes that gap for the surfaces
   a first-time, non-English-literate reporter actually needs: the
   shared shell (sidebar/topbar), the report form, and the
   confirmation screen.

   Scope note: deeper counsellor-only tooling (the cases table,
   case-brief detail panel, guidance library, alerts list) stays
   English for now. That's a deliberate scope choice under a hard
   deadline, not an oversight -- staff using this dashboard are a
   different audience from the reporter the judges were describing.
   Extending coverage there later just means adding data-i18n
   attributes and TRANSLATIONS keys, same pattern as everything below.

   Adding a new UI language (Urdu, Marathi, ...) means adding one more
   block to TRANSLATIONS and one <option> in the language switcher --
   nothing else here changes.
========================================================= */

const TRANSLATIONS = {

    en: {
        "nav.overview": "Overview",
        "nav.newReport": "New Report",
        "nav.cases": "Cases",
        "nav.riskMap": "Risk Map",
        "nav.guidance": "Guidance",
        "nav.alerts": "Alerts",

        "sidebar.helpline": "National Helpline",
        "sidebar.helplineSub": "Support line · 14566",
        "sidebar.exit": "Exit dashboard",

        "topbar.operator": "Counsellor",
        "topbar.operatorSub": "Support desk",

        "overview.eyebrow": "ATHENA · OVERVIEW",
        "overview.title": "Overview",
        "overview.subtitle": "Real-time helpline monitoring and case support.",
        "overview.newReportBtn": "New report",

        "stats.total": "Total cases",
        "stats.totalSub": "All received cases",
        "stats.criticalSub": "Immediate attention",
        "stats.highSub": "Priority review",
        "stats.pending": "Pending",
        "stats.pendingSub": "Awaiting review",

        "risk.low": "Low",
        "risk.moderate": "Moderate",
        "risk.high": "High",
        "risk.critical": "Critical",
        "risk.sectionEyebrow": "RISK MONITORING",
        "risk.sectionTitle": "Risk distribution",
        "risk.current": "Current",
        "risk.casesWord": "cases",

        "district.eyebrow": "NATIONAL COVERAGE",
        "district.title": "District risk",
        "district.viewMap": "View map →",
        "district.placeholder": "District risk data",

        "recent.eyebrow": "CASE MANAGEMENT",
        "recent.title": "Recent cases",
        "recent.viewAll": "View all →",
        "loading.cases": "Loading cases...",

        "newreport.eyebrow": "NATIONAL HELPLINE · 14566",
        "newreport.title": "Tell us what happened",
        "newreport.subtitle": "You can speak or type. Share only what feels safe.",

        "lang.choose": "Choose your language",

        "channel.question": "Channel this came through",
        "channel.hint": "Tag which of NHAA's channels this report is coming through -- used for case tracking, not shown to the reporter.",
        "channel.call": "14566 Call",
        "channel.portal": "Portal",
        "channel.chatbot": "Chatbot",
        "channel.mobile": "Mobile App",

        "voice.label": "VOICE FIRST",
        "voice.title": "Tell us in your own words",
        "voice.body": "You don't need to explain everything perfectly. Just tell us what happened.",
        "voice.tapToSpeak": "Tap to speak",
        "voice.listening": "Listening… Tap again when finished",
        "voice.micPermission": "Microphone permission is needed",
        "voice.sending": "Sending your report…",
        "voice.error": "Something went wrong. Please try again.",

        "divider.orType": "OR TYPE BELOW",
        "textarea.placeholder": "Tell us what happened...",

        "submit.send": "Send report",
        "submit.sending": "Sending…",
        "evidence.attach": "Add a photo or file (optional)",

        "support.title": "You are being heard.",
        "support.body": "Your information helps trained support staff understand your situation and provide the right assistance.",
        "support.point1": "Your information is handled carefully.",
        "support.point2": "Trained staff can review cases when needed.",
        "support.point3": "Urgent situations can be prioritised.",

        "confirm.eyebrow": "REPORT RECEIVED",
        "confirm.title": "We hear you.",
        "confirm.body": "We've received what you shared.",
        "confirm.helpTitle": "Your report has been recorded.",
        "confirm.small": "This is a prototype. Your report has been scored and queued for a counsellor, but nobody is monitoring it right now. If you need help today, call 14566 — or 112 if you are in danger.",
        "confirm.shareMore": "Share more",
        "confirm.callLink": "Need direct support? Call 14566",
        "confirm.urgentCall": "In immediate danger? Call 112 now.",
        "confirm.urgentSub": "This has also been flagged for our team to review right away.",
        "confirm.legalTitle": "This may fall under:",
        "confirm.contactsTitle": "Immediate contacts",
        "confirm.slaLabel": "Review target",
        "confirm.reference": "Reference",

        "status.sending": "Sending securely… please don't close this page.",
        "status.error": "Couldn't send your report. Nothing was lost — please try again.",
        "status.retry": "Try again",

        "privacy.summary": "Only trained support staff can access your report. We will not contact you unless you choose a safe way for us to do so.",
        "privacy.collected": "What we keep: what you write or say, and the time you sent it.",
        "privacy.access": "Who can see it: trained helpline counsellors reviewing your case. Not the public, and not the person you are reporting.",
        "privacy.location": "Location: only if you tap SOS and allow it, and it is stored rounded to roughly a neighbourhood, never an exact address.",
        "privacy.contact": "Contact: we only reach out the way you choose on the next screen. \"Do not contact me\" is a real option.",
        "privacy.risk": "Please do not include anything that would put you in more danger if someone else saw this device.",

        "followup.title": "How is it safe to contact you?",
        "followup.doNotContact": "Do not contact me",
        "followup.textOnly": "Text message only",
        "followup.callOnly": "Phone call only",
        "followup.either": "Either is safe",
        "followup.timeLabel": "When is it safe to reach you? (optional)",
        "followup.timePlaceholder": "e.g. weekday mornings only",
        "followup.save": "Save my preference",
        "followup.saved": "Saved. We will follow this.",
        "followup.error": "Couldn't save that preference. Please try again.",

        "safety.callNow": "In immediate danger? Call 112 now",
        "safety.sos": "SOS",
        "safety.sosSending": "Sending SOS…",
        "safety.quickExit": "Quick exit",
        "safety.sosError": "Could not send SOS. If you are in danger, call 112 directly.",

        "cases.eyebrow": "CASE MANAGEMENT",
        "cases.title": "Cases",
        "cases.subtitle": "Review incoming reports and prioritise support.",
        "cases.refresh": "Refresh",
        "cases.search": "Search cases...",
        "cases.allRisk": "All risk levels",
        "table.case": "Case",
        "table.incident": "Incident",
        "table.district": "District",
        "table.risk": "Risk",
        "table.status": "Status",
        "table.time": "Time",
        "riskmap.eyebrow": "NATIONAL COVERAGE",
        "riskmap.title": "Risk map",
        "riskmap.subtitle": "Monitor case concentration across districts.",
        "riskmap.cardTitle": "India · District risk",
        "riskmap.cardSub": "Risk levels across reported cases.",
        "guidance.eyebrow": "STAFF SUPPORT",
        "guidance.title": "Guidance",
        "guidance.subtitle": "Plain-language support guidance for counsellors.",
        "guidance.c1t": "Listen first",
        "guidance.c1b": "Allow the person to explain their situation in their own words without interrupting unnecessarily.",
        "guidance.c2t": "Check immediate safety",
        "guidance.c2b": "If the case indicates immediate danger, prioritise connecting the person with appropriate human support.",
        "guidance.c3t": "Protect information",
        "guidance.c3b": "Handle personal information carefully and only access information needed for the support process.",
        "guidance.c4t": "Escalate when necessary",
        "guidance.c4b": "High-priority situations should be reviewed promptly by trained personnel.",
        "alerts.eyebrow": "PRIORITY MONITORING",
        "alerts.title": "Alerts",
        "alerts.subtitle": "Cases requiring closer attention.",
        "alerts.show": "Show",
        "alerts.needsReview": "Needs review",
        "alerts.reviewedOpt": "Reviewed",
        "alerts.allOpt": "All",
        "alerts.priority": "Priority",
        "alerts.criticalHigh": "Critical and High",
        "alerts.allPriorities": "All priorities",
        "alerts.category": "Category",
        "alerts.allCategories": "All categories",
        "alerts.reset": "Reset",
        "alerts.viewCase": "View case",
        "alerts.markReviewed": "Mark reviewed",
        "alerts.reviewedBadge": "Reviewed",

        "report.submitError": "Unable to send the report right now. Please try again.",
    },

    hi: {
        "nav.overview": "अवलोकन",
        "nav.newReport": "नई रिपोर्ट",
        "nav.cases": "मामले",
        "nav.riskMap": "जोखिम मानचित्र",
        "nav.guidance": "मार्गदर्शन",
        "nav.alerts": "अलर्ट",

        "sidebar.helpline": "राष्ट्रीय हेल्पलाइन",
        "sidebar.helplineSub": "सहायता लाइन · 14566",
        "sidebar.exit": "डैशबोर्ड से बाहर निकलें",

        "topbar.operator": "काउंसलर",
        "topbar.operatorSub": "सहायता डेस्क",

        "overview.eyebrow": "एथेना · अवलोकन",
        "overview.title": "अवलोकन",
        "overview.subtitle": "रीयल-टाइम हेल्पलाइन निगरानी और केस सहायता।",
        "overview.newReportBtn": "नई रिपोर्ट",

        "stats.total": "कुल मामले",
        "stats.totalSub": "सभी प्राप्त मामले",
        "stats.criticalSub": "तत्काल ध्यान",
        "stats.highSub": "प्राथमिकता समीक्षा",
        "stats.pending": "लंबित",
        "stats.pendingSub": "समीक्षा की प्रतीक्षा में",

        "risk.low": "कम",
        "risk.moderate": "मध्यम",
        "risk.high": "उच्च",
        "risk.critical": "गंभीर",
        "risk.sectionEyebrow": "जोखिम निगरानी",
        "risk.sectionTitle": "जोखिम वितरण",
        "risk.current": "वर्तमान",
        "risk.casesWord": "मामले",

        "district.eyebrow": "राष्ट्रीय कवरेज",
        "district.title": "जिला जोखिम",
        "district.viewMap": "मानचित्र देखें →",
        "district.placeholder": "जिला जोखिम डेटा",

        "recent.eyebrow": "केस प्रबंधन",
        "recent.title": "हाल के मामले",
        "recent.viewAll": "सभी देखें →",
        "loading.cases": "मामले लोड हो रहे हैं...",

        "newreport.eyebrow": "राष्ट्रीय हेल्पलाइन · 14566",
        "newreport.title": "हमें बताएं कि क्या हुआ",
        "newreport.subtitle": "आप बोल सकते हैं या टाइप कर सकते हैं। सिर्फ वही साझा करें जो आपको सुरक्षित लगे।",

        "lang.choose": "अपनी भाषा चुनें",

        "channel.question": "यह रिपोर्ट किस माध्यम से आई",
        "channel.hint": "यह रिपोर्ट NHAA के किस चैनल से आ रही है, वह चुनें -- केवल केस ट्रैकिंग के लिए, रिपोर्ट करने वाले को नहीं दिखाया जाता।",
        "channel.call": "14566 कॉल",
        "channel.portal": "पोर्टल",
        "channel.chatbot": "चैटबॉट",
        "channel.mobile": "मोबाइल ऐप",

        "voice.label": "पहले आवाज़",
        "voice.title": "अपने शब्दों में हमें बताएं",
        "voice.body": "आपको सब कुछ पूरी तरह से समझाने की ज़रूरत नहीं है। बस हमें बताएं कि क्या हुआ।",
        "voice.tapToSpeak": "बोलने के लिए टैप करें",
        "voice.listening": "सुन रहे हैं… समाप्त होने पर फिर से टैप करें",
        "voice.micPermission": "माइक्रोफ़ोन की अनुमति आवश्यक है",
        "voice.sending": "आपकी रिपोर्ट भेजी जा रही है…",
        "voice.error": "कुछ गलत हो गया। कृपया फिर से प्रयास करें।",

        "divider.orType": "या नीचे टाइप करें",
        "textarea.placeholder": "हमें बताएं क्या हुआ...",

        "submit.send": "रिपोर्ट भेजें",
        "submit.sending": "भेजा जा रहा है…",
        "evidence.attach": "फ़ोटो या फ़ाइल जोड़ें (वैकल्पिक)",

        "support.title": "आपकी बात सुनी जा रही है।",
        "support.body": "आपकी जानकारी प्रशिक्षित सहायता कर्मचारियों को आपकी स्थिति समझने और सही सहायता प्रदान करने में मदद करती है।",
        "support.point1": "आपकी जानकारी को सावधानी से संभाला जाता है।",
        "support.point2": "प्रशिक्षित कर्मचारी ज़रूरत पड़ने पर मामलों की समीक्षा कर सकते हैं।",
        "support.point3": "तत्काल स्थितियों को प्राथमिकता दी जा सकती है।",

        "confirm.eyebrow": "रिपोर्ट प्राप्त हुई",
        "confirm.title": "हम आपकी बात सुन रहे हैं।",
        "confirm.body": "आपने जो साझा किया है वह हमें मिल गया है।",
        "confirm.helpTitle": "आपकी रिपोर्ट दर्ज कर ली गई है।",
        "confirm.small": "यह एक प्रोटोटाइप है। आपकी रिपोर्ट का आकलन करके काउंसलर की सूची में डाल दिया गया है, लेकिन अभी कोई इसे नहीं देख रहा है। यदि आपको आज मदद चाहिए तो 14566 पर कॉल करें — और यदि आप खतरे में हैं तो 112 पर।",
        "confirm.shareMore": "और साझा करें",
        "confirm.callLink": "सीधी सहायता चाहिए? 14566 पर कॉल करें",
        "confirm.urgentCall": "तुरंत खतरे में हैं? अभी 112 पर कॉल करें।",
        "confirm.urgentSub": "हमारी टीम को भी इसकी तुरंत समीक्षा के लिए सूचित कर दिया गया है।",
        "confirm.legalTitle": "यह इसके अंतर्गत आ सकता है:",
        "confirm.contactsTitle": "तत्काल संपर्क",
        "confirm.slaLabel": "समीक्षा लक्ष्य",
        "confirm.reference": "संदर्भ संख्या",

        "status.sending": "सुरक्षित रूप से भेजा जा रहा है… कृपया यह पेज बंद न करें।",
        "status.error": "आपकी रिपोर्ट भेजी नहीं जा सकी। कुछ भी खोया नहीं है — कृपया फिर से कोशिश करें।",
        "status.retry": "फिर से कोशिश करें",

        "privacy.summary": "आपकी रिपोर्ट केवल प्रशिक्षित सहायता कर्मचारी ही देख सकते हैं। जब तक आप कोई सुरक्षित तरीका नहीं चुनते, हम आपसे संपर्क नहीं करेंगे।",
        "privacy.collected": "हम क्या रखते हैं: आपने जो लिखा या कहा, और भेजने का समय।",
        "privacy.access": "कौन देख सकता है: आपका मामला देख रहे प्रशिक्षित काउंसलर। न आम लोग, न वह व्यक्ति जिसकी आप शिकायत कर रहे हैं।",
        "privacy.location": "स्थान: केवल तब जब आप एसओएस दबाएँ और अनुमति दें, और वह लगभग मोहल्ले तक ही सीमित रखा जाता है, सटीक पता कभी नहीं।",
        "privacy.contact": "संपर्क: हम केवल उसी तरीके से संपर्क करेंगे जो आप अगली स्क्रीन पर चुनेंगे। \"मुझसे संपर्क न करें\" एक वास्तविक विकल्प है।",
        "privacy.risk": "कृपया ऐसा कुछ न लिखें जिससे कोई और यह उपकरण देखे तो आपको अधिक खतरा हो।",

        "followup.title": "आपसे संपर्क करना कैसे सुरक्षित है?",
        "followup.doNotContact": "मुझसे संपर्क न करें",
        "followup.textOnly": "केवल संदेश (टेक्स्ट)",
        "followup.callOnly": "केवल फ़ोन कॉल",
        "followup.either": "दोनों सुरक्षित हैं",
        "followup.timeLabel": "आपसे कब संपर्क करना सुरक्षित है? (वैकल्पिक)",
        "followup.timePlaceholder": "जैसे केवल कार्यदिवस की सुबह",
        "followup.save": "मेरी पसंद सहेजें",
        "followup.saved": "सहेज लिया गया। हम इसका पालन करेंगे।",
        "followup.error": "यह पसंद सहेजी नहीं जा सकी। कृपया फिर से कोशिश करें।",

        "safety.callNow": "तुरंत खतरे में हैं? अभी 112 पर कॉल करें",
        "safety.sos": "एसओएस",
        "safety.sosSending": "एसओएस भेजा जा रहा है…",
        "safety.quickExit": "तुरंत बाहर निकलें",
        "safety.sosError": "एसओएस भेजा नहीं जा सका। यदि आप खतरे में हैं, तो सीधे 112 पर कॉल करें।",

        "cases.eyebrow": "केस प्रबंधन",
        "cases.title": "मामले",
        "cases.subtitle": "आने वाली रिपोर्ट देखें और सहायता को प्राथमिकता दें।",
        "cases.refresh": "ताज़ा करें",
        "cases.search": "मामले खोजें...",
        "cases.allRisk": "सभी जोखिम स्तर",
        "table.case": "मामला",
        "table.incident": "घटना",
        "table.district": "ज़िला",
        "table.risk": "जोखिम",
        "table.status": "स्थिति",
        "table.time": "समय",
        "riskmap.eyebrow": "राष्ट्रीय कवरेज",
        "riskmap.title": "जोखिम मानचित्र",
        "riskmap.subtitle": "ज़िलों में मामलों की सघनता देखें।",
        "riskmap.cardTitle": "भारत · ज़िला जोखिम",
        "riskmap.cardSub": "दर्ज मामलों के अनुसार जोखिम स्तर।",
        "guidance.eyebrow": "स्टाफ़ सहायता",
        "guidance.title": "मार्गदर्शन",
        "guidance.subtitle": "काउंसलर के लिए सरल भाषा में सहायता मार्गदर्शन।",
        "guidance.c1t": "पहले सुनें",
        "guidance.c1b": "व्यक्ति को अपनी बात अपने शब्दों में कहने दें, बिना ज़रूरत के बीच में न टोकें।",
        "guidance.c2t": "तत्काल सुरक्षा जाँचें",
        "guidance.c2b": "यदि मामला तत्काल खतरे का संकेत देता है, तो व्यक्ति को उपयुक्त मानवीय सहायता से जोड़ना प्राथमिकता है।",
        "guidance.c3t": "जानकारी सुरक्षित रखें",
        "guidance.c3b": "निजी जानकारी सावधानी से संभालें और केवल वही देखें जो सहायता प्रक्रिया के लिए आवश्यक है।",
        "guidance.c4t": "ज़रूरत होने पर आगे बढ़ाएँ",
        "guidance.c4b": "उच्च प्राथमिकता वाली स्थितियों की समीक्षा प्रशिक्षित कर्मियों द्वारा शीघ्र की जानी चाहिए।",
        "alerts.eyebrow": "प्राथमिकता निगरानी",
        "alerts.title": "अलर्ट",
        "alerts.subtitle": "ऐसे मामले जिन पर अधिक ध्यान चाहिए।",
        "alerts.show": "दिखाएँ",
        "alerts.needsReview": "समीक्षा बाकी",
        "alerts.reviewedOpt": "समीक्षित",
        "alerts.allOpt": "सभी",
        "alerts.priority": "प्राथमिकता",
        "alerts.criticalHigh": "गंभीर और उच्च",
        "alerts.allPriorities": "सभी प्राथमिकताएँ",
        "alerts.category": "श्रेणी",
        "alerts.allCategories": "सभी श्रेणियाँ",
        "alerts.reset": "रीसेट",
        "alerts.viewCase": "मामला देखें",
        "alerts.markReviewed": "समीक्षित करें",
        "alerts.reviewedBadge": "समीक्षित",

        "report.submitError": "अभी रिपोर्ट भेजने में असमर्थ। कृपया फिर से प्रयास करें।",
    },

    te: {
        "nav.overview": "అవలోకనం",
        "nav.newReport": "కొత్త ఫిర్యాదు",
        "nav.cases": "కేసులు",
        "nav.riskMap": "ప్రమాద పటం",
        "nav.guidance": "మార్గదర్శకత్వం",
        "nav.alerts": "అలర్ట్‌లు",

        "sidebar.helpline": "జాతీయ హెల్ప్‌లైన్",
        "sidebar.helplineSub": "సహాయ లైన్ · 14566",
        "sidebar.exit": "డాష్‌బోర్డ్ నుండి నిష్క్రమించండి",

        "topbar.operator": "కౌన్సెలర్",
        "topbar.operatorSub": "సహాయ డెస్క్",

        "overview.eyebrow": "ఎథీనా · అవలోకనం",
        "overview.title": "అవలోకనం",
        "overview.subtitle": "రియల్-టైమ్ హెల్ప్‌లైన్ పర్యవేక్షణ మరియు కేసు మద్దతు.",
        "overview.newReportBtn": "కొత్త ఫిర్యాదు",

        "stats.total": "మొత్తం కేసులు",
        "stats.totalSub": "అందిన మొత్తం కేసులు",
        "stats.criticalSub": "తక్షణ శ్రద్ధ",
        "stats.highSub": "ప్రాధాన్యత సమీక్ష",
        "stats.pending": "పెండింగ్‌లో",
        "stats.pendingSub": "సమీక్ష కోసం వేచి ఉంది",

        "risk.low": "తక్కువ",
        "risk.moderate": "మధ్యస్థం",
        "risk.high": "అధికం",
        "risk.critical": "అత్యవసరం",
        "risk.sectionEyebrow": "ప్రమాద పర్యవేక్షణ",
        "risk.sectionTitle": "ప్రమాద పంపిణీ",
        "risk.current": "ప్రస్తుతం",
        "risk.casesWord": "కేసులు",

        "district.eyebrow": "జాతీయ కవరేజ్",
        "district.title": "జిల్లా ప్రమాదం",
        "district.viewMap": "పటం చూడండి →",
        "district.placeholder": "జిల్లా ప్రమాద డేటా",

        "recent.eyebrow": "కేసు నిర్వహణ",
        "recent.title": "ఇటీవలి కేసులు",
        "recent.viewAll": "అన్నీ చూడండి →",
        "loading.cases": "కేసులు లోడ్ అవుతున్నాయి...",

        "newreport.eyebrow": "జాతీయ హెల్ప్‌లైన్ · 14566",
        "newreport.title": "ఏం జరిగిందో మాకు చెప్పండి",
        "newreport.subtitle": "మీరు మాట్లాడవచ్చు లేదా టైప్ చేయవచ్చు. మీకు సురక్షితం అనిపించినది మాత్రమే పంచుకోండి.",

        "lang.choose": "మీ భాషను ఎంచుకోండి",

        "channel.question": "ఈ నివేదిక ఏ మార్గం ద్వారా వచ్చింది",
        "channel.hint": "ఈ నివేదిక NHAA యొక్క ఏ ఛానెల్ ద్వారా వస్తుందో ఎంచుకోండి -- ఇది కేసు ట్రాకింగ్ కోసం మాత్రమే, రిపోర్టర్‌కు చూపించబడదు.",
        "channel.call": "14566 కాల్",
        "channel.portal": "పోర్టల్",
        "channel.chatbot": "చాట్‌బాట్",
        "channel.mobile": "మొబైల్ యాప్",

        "voice.label": "మొదట వాయిస్",
        "voice.title": "మీ మాటల్లో మాకు చెప్పండి",
        "voice.body": "మీరు ప్రతిదీ పరిపూర్ణంగా వివరించాల్సిన అవసరం లేదు. ఏం జరిగిందో మాకు చెప్పండి.",
        "voice.tapToSpeak": "మాట్లాడటానికి నొక్కండి",
        "voice.listening": "వింటున్నాము… పూర్తయిన తర్వాత మళ్లీ నొక్కండి",
        "voice.micPermission": "మైక్రోఫోన్ అనుమతి అవసరం",
        "voice.sending": "మీ ఫిర్యాదు పంపబడుతోంది…",
        "voice.error": "ఏదో తప్పు జరిగింది. దయచేసి మళ్లీ ప్రయత్నించండి.",

        "divider.orType": "లేదా క్రింద టైప్ చేయండి",
        "textarea.placeholder": "ఏం జరిగిందో మాకు చెప్పండి...",

        "submit.send": "ఫిర్యాదు పంపండి",
        "submit.sending": "పంపుతోంది…",
        "evidence.attach": "ఫోటో లేదా ఫైల్ జోడించండి (ఐచ్ఛికం)",

        "support.title": "మీ మాట వినబడుతోంది.",
        "support.body": "మీ సమాచారం శిక్షణ పొందిన సహాయ సిబ్బందికి మీ పరిస్థితిని అర్థం చేసుకోవడానికి మరియు సరైన సహాయం అందించడానికి సహాయపడుతుంది.",
        "support.point1": "మీ సమాచారం జాగ్రత్తగా నిర్వహించబడుతుంది.",
        "support.point2": "అవసరమైనప్పుడు శిక్షణ పొందిన సిబ్బంది కేసులను సమీక్షించగలరు.",
        "support.point3": "తక్షణ పరిస్థితులకు ప్రాధాన్యత ఇవ్వవచ్చు.",

        "confirm.eyebrow": "ఫిర్యాదు అందింది",
        "confirm.title": "మేము మీ మాట వింటున్నాము.",
        "confirm.body": "మీరు పంచుకున్నది మాకు అందింది.",
        "confirm.helpTitle": "మీ ఫిర్యాదు నమోదు చేయబడింది.",
        "confirm.small": "ఇది ఒక ప్రోటోటైప్. మీ ఫిర్యాదు అంచనా వేయబడి కౌన్సెలర్ జాబితాలో చేర్చబడింది, కానీ ప్రస్తుతం ఎవరూ దీన్ని పర్యవేక్షించడం లేదు. ఈరోజు సహాయం కావాలంటే 14566కి కాల్ చేయండి — ప్రమాదంలో ఉంటే 112కి.",
        "confirm.shareMore": "మరింత పంచుకోండి",
        "confirm.callLink": "నేరుగా సహాయం కావాలా? 14566కి కాల్ చేయండి",
        "confirm.urgentCall": "తక్షణ ప్రమాదంలో ఉన్నారా? వెంటనే 112కి కాల్ చేయండి.",
        "confirm.urgentSub": "దీన్ని వెంటనే సమీక్షించమని మా బృందానికి కూడా తెలియజేయబడింది.",
        "confirm.legalTitle": "ఇది దీని పరిధిలోకి రావచ్చు:",
        "confirm.contactsTitle": "తక్షణ సంప్రదింపులు",
        "confirm.slaLabel": "సమీక్షా లక్ష్యం",
        "confirm.reference": "సూచన సంఖ్య",

        "status.sending": "సురక్షితంగా పంపుతోంది… దయచేసి ఈ పేజీని మూసివేయవద్దు.",
        "status.error": "మీ ఫిర్యాదు పంపడం సాధ్యం కాలేదు. ఏమీ పోలేదు — దయచేసి మళ్లీ ప్రయత్నించండి.",
        "status.retry": "మళ్లీ ప్రయత్నించండి",

        "privacy.summary": "మీ ఫిర్యాదును శిక్షణ పొందిన సహాయ సిబ్బంది మాత్రమే చూడగలరు. మీరు సురక్షితమైన మార్గం ఎంచుకుంటే తప్ప మేము మిమ్మల్ని సంప్రదించము.",
        "privacy.collected": "మేము ఏమి ఉంచుతాము: మీరు రాసినది లేదా చెప్పినది, మరియు పంపిన సమయం.",
        "privacy.access": "ఎవరు చూడగలరు: మీ కేసును సమీక్షిస్తున్న శిక్షణ పొందిన కౌన్సెలర్లు. ప్రజలు కాదు, మీరు ఫిర్యాదు చేస్తున్న వ్యక్తి అంతకంటే కాదు.",
        "privacy.location": "స్థానం: మీరు ఎస్ఓఎస్ నొక్కి అనుమతిస్తేనే, అది సుమారు ప్రాంతం వరకే నిల్వ చేయబడుతుంది, ఖచ్చితమైన చిరునామా ఎప్పుడూ కాదు.",
        "privacy.contact": "సంప్రదింపు: తదుపరి స్క్రీన్‌లో మీరు ఎంచుకున్న విధంగానే మేము సంప్రదిస్తాము. \"నన్ను సంప్రదించవద్దు\" నిజమైన ఎంపిక.",
        "privacy.risk": "ఈ పరికరాన్ని వేరొకరు చూస్తే మీకు మరింత ప్రమాదం కలిగించే విషయాలను దయచేసి రాయవద్దు.",

        "followup.title": "మిమ్మల్ని సంప్రదించడం ఎలా సురక్షితం?",
        "followup.doNotContact": "నన్ను సంప్రదించవద్దు",
        "followup.textOnly": "సందేశం (టెక్స్ట్) మాత్రమే",
        "followup.callOnly": "ఫోన్ కాల్ మాత్రమే",
        "followup.either": "రెండూ సురక్షితమే",
        "followup.timeLabel": "మిమ్మల్ని ఎప్పుడు సంప్రదించడం సురక్షితం? (ఐచ్ఛికం)",
        "followup.timePlaceholder": "ఉదా. పని దినాల ఉదయం మాత్రమే",
        "followup.save": "నా ఎంపికను సేవ్ చేయండి",
        "followup.saved": "సేవ్ చేయబడింది. మేము దీన్ని పాటిస్తాము.",
        "followup.error": "ఆ ఎంపికను సేవ్ చేయడం సాధ్యం కాలేదు. దయచేసి మళ్లీ ప్రయత్నించండి.",

        "safety.callNow": "తక్షణ ప్రమాదంలో ఉన్నారా? వెంటనే 112కి కాల్ చేయండి",
        "safety.sos": "ఎస్ఓఎస్",
        "safety.sosSending": "ఎస్ఓఎస్ పంపుతోంది…",
        "safety.quickExit": "త్వరిత నిష్క్రమణ",
        "safety.sosError": "ఎస్ఓఎస్ పంపడం సాధ్యం కాలేదు. మీరు ప్రమాదంలో ఉంటే, నేరుగా 112కి కాల్ చేయండి.",

        "cases.eyebrow": "కేసు నిర్వహణ",
        "cases.title": "కేసులు",
        "cases.subtitle": "వచ్చిన ఫిర్యాదులను సమీక్షించి సహాయానికి ప్రాధాన్యం ఇవ్వండి.",
        "cases.refresh": "రిఫ్రెష్",
        "cases.search": "కేసులను వెతకండి...",
        "cases.allRisk": "అన్ని ప్రమాద స్థాయిలు",
        "table.case": "కేసు",
        "table.incident": "ఘటన",
        "table.district": "జిల్లా",
        "table.risk": "ప్రమాదం",
        "table.status": "స్థితి",
        "table.time": "సమయం",
        "riskmap.eyebrow": "జాతీయ పరిధి",
        "riskmap.title": "ప్రమాద పటం",
        "riskmap.subtitle": "జిల్లాల వారీగా కేసుల కేంద్రీకరణను గమనించండి.",
        "riskmap.cardTitle": "భారతదేశం · జిల్లా ప్రమాదం",
        "riskmap.cardSub": "నమోదైన కేసుల ఆధారంగా ప్రమాద స్థాయిలు.",
        "guidance.eyebrow": "సిబ్బంది సహాయం",
        "guidance.title": "మార్గదర్శకత్వం",
        "guidance.subtitle": "కౌన్సెలర్ల కోసం సరళ భాషలో సహాయ మార్గదర్శకత్వం.",
        "guidance.c1t": "ముందు వినండి",
        "guidance.c1b": "వ్యక్తి తన పరిస్థితిని తన సొంత మాటల్లో చెప్పనివ్వండి, అనవసరంగా మధ్యలో ఆపవద్దు.",
        "guidance.c2t": "తక్షణ భద్రతను చూడండి",
        "guidance.c2b": "కేసు తక్షణ ప్రమాదాన్ని సూచిస్తే, వ్యక్తిని తగిన మానవ సహాయంతో కలపడానికి ప్రాధాన్యం ఇవ్వండి.",
        "guidance.c3t": "సమాచారాన్ని కాపాడండి",
        "guidance.c3b": "వ్యక్తిగత సమాచారాన్ని జాగ్రత్తగా నిర్వహించండి, సహాయ ప్రక్రియకు అవసరమైనది మాత్రమే చూడండి.",
        "guidance.c4t": "అవసరమైనప్పుడు పైకి పంపండి",
        "guidance.c4b": "అధిక ప్రాధాన్యత గల పరిస్థితులను శిక్షణ పొందిన సిబ్బంది వెంటనే సమీక్షించాలి.",
        "alerts.eyebrow": "ప్రాధాన్యత పర్యవేక్షణ",
        "alerts.title": "అలర్ట్‌లు",
        "alerts.subtitle": "మరింత శ్రద్ధ అవసరమైన కేసులు.",
        "alerts.show": "చూపించు",
        "alerts.needsReview": "సమీక్ష అవసరం",
        "alerts.reviewedOpt": "సమీక్షించినవి",
        "alerts.allOpt": "అన్నీ",
        "alerts.priority": "ప్రాధాన్యత",
        "alerts.criticalHigh": "క్రిటికల్ మరియు హై",
        "alerts.allPriorities": "అన్ని ప్రాధాన్యతలు",
        "alerts.category": "వర్గం",
        "alerts.allCategories": "అన్ని వర్గాలు",
        "alerts.reset": "రీసెట్",
        "alerts.viewCase": "కేసు చూడండి",
        "alerts.markReviewed": "సమీక్షించినట్లు గుర్తించు",
        "alerts.reviewedBadge": "సమీక్షించబడింది",

        "report.submitError": "ప్రస్తుతం ఫిర్యాదు పంపడం సాధ్యం కాలేదు. దయచేసి మళ్లీ ప్రయత్నించండి.",
    },

    // Translation-review caveat: Hindi/Telugu above were battle-tested
    // through this whole project's development. Urdu/Bengali were
    // added 2026-08-29 alongside understanding.py's NLU support for
    // them -- translated with real care but without a native-speaker
    // review pass. Recommended before relying on these in front of
    // judges, same disclosure as eval_pipeline.py carries for the
    // underlying NLU coverage.
    ur: {
        "nav.overview": "جائزہ",
        "nav.newReport": "نئی رپورٹ",
        "nav.cases": "مقدمات",
        "nav.riskMap": "خطرے کا نقشہ",
        "nav.guidance": "رہنمائی",
        "nav.alerts": "انتباہات",

        "sidebar.helpline": "قومی ہیلپ لائن",
        "sidebar.helplineSub": "سپورٹ لائن · 14566",
        "sidebar.exit": "ڈیش بورڈ سے باہر نکلیں",

        "topbar.operator": "کاؤنسلر",
        "topbar.operatorSub": "سپورٹ ڈیسک",

        "overview.eyebrow": "ایتھینا · جائزہ",
        "overview.title": "جائزہ",
        "overview.subtitle": "ریئل ٹائم ہیلپ لائن نگرانی اور کیس سپورٹ۔",
        "overview.newReportBtn": "نئی رپورٹ",

        "stats.total": "کل مقدمات",
        "stats.totalSub": "تمام موصولہ مقدمات",
        "stats.criticalSub": "فوری توجہ",
        "stats.highSub": "ترجیحی جائزہ",
        "stats.pending": "زیر التوا",
        "stats.pendingSub": "جائزے کا انتظار",

        "risk.low": "کم",
        "risk.moderate": "درمیانہ",
        "risk.high": "زیادہ",
        "risk.critical": "شدید",
        "risk.sectionEyebrow": "خطرے کی نگرانی",
        "risk.sectionTitle": "خطرے کی تقسیم",
        "risk.current": "موجودہ",
        "risk.casesWord": "مقدمات",

        "district.eyebrow": "قومی احاطہ",
        "district.title": "ضلعی خطرہ",
        "district.viewMap": "نقشہ دیکھیں →",
        "district.placeholder": "ضلعی خطرے کا ڈیٹا",

        "recent.eyebrow": "کیس مینجمنٹ",
        "recent.title": "حالیہ مقدمات",
        "recent.viewAll": "سب دیکھیں →",
        "loading.cases": "مقدمات لوڈ ہو رہے ہیں...",

        "newreport.eyebrow": "قومی ہیلپ لائن · 14566",
        "newreport.title": "ہمیں بتائیں کہ کیا ہوا",
        "newreport.subtitle": "آپ بول سکتے ہیں یا ٹائپ کر سکتے ہیں۔ صرف وہی بتائیں جو آپ کو محفوظ لگے۔",

        "lang.choose": "اپنی زبان منتخب کریں",

        "channel.question": "یہ رپورٹ کس ذریعے سے آئی",
        "channel.hint": "منتخب کریں کہ یہ رپورٹ NHAA کے کس چینل سے آ رہی ہے -- صرف کیس ٹریکنگ کے لیے، رپورٹ کرنے والے کو نہیں دکھایا جاتا۔",
        "channel.call": "14566 کال",
        "channel.portal": "پورٹل",
        "channel.chatbot": "چیٹ بوٹ",
        "channel.mobile": "موبائل ایپ",

        "voice.label": "پہلے آواز",
        "voice.title": "اپنے الفاظ میں ہمیں بتائیں",
        "voice.body": "آپ کو ہر چیز کامل طریقے سے بیان کرنے کی ضرورت نہیں۔ بس ہمیں بتائیں کہ کیا ہوا۔",
        "voice.tapToSpeak": "بولنے کے لیے ٹیپ کریں",
        "voice.listening": "سن رہے ہیں… ختم ہونے پر دوبارہ ٹیپ کریں",
        "voice.micPermission": "مائیکروفون کی اجازت درکار ہے",
        "voice.sending": "آپ کی رپورٹ بھیجی جا رہی ہے…",
        "voice.error": "کچھ غلط ہو گیا۔ براہ کرم دوبارہ کوشش کریں۔",

        "divider.orType": "یا نیچے ٹائپ کریں",
        "textarea.placeholder": "ہمیں بتائیں کیا ہوا...",

        "submit.send": "رپورٹ بھیجیں",
        "submit.sending": "بھیجا جا رہا ہے…",
        "evidence.attach": "تصویر یا فائل شامل کریں (اختیاری)",

        "support.title": "آپ کی بات سنی جا رہی ہے۔",
        "support.body": "آپ کی معلومات تربیت یافتہ سپورٹ اسٹاف کو آپ کی صورتحال سمجھنے اور صحیح مدد فراہم کرنے میں مدد دیتی ہیں۔",
        "support.point1": "آپ کی معلومات کو احتیاط سے سنبھالا جاتا ہے۔",
        "support.point2": "ضرورت پڑنے پر تربیت یافتہ اسٹاف مقدمات کا جائزہ لے سکتا ہے۔",
        "support.point3": "فوری صورتحال کو ترجیح دی جا سکتی ہے۔",

        "confirm.eyebrow": "رپورٹ موصول ہو گئی",
        "confirm.title": "ہم آپ کی بات سن رہے ہیں۔",
        "confirm.body": "آپ نے جو کچھ بتایا وہ ہمیں مل گیا ہے۔",
        "confirm.helpTitle": "آپ کی رپورٹ درج کر لی گئی ہے۔",
        "confirm.small": "یہ ایک پروٹوٹائپ ہے۔ آپ کی رپورٹ کا جائزہ لے کر کونسلر کی فہرست میں شامل کر دی گئی ہے، لیکن ابھی کوئی اسے نہیں دیکھ رہا۔ اگر آپ کو آج مدد چاہیے تو 14566 پر کال کریں — اور اگر آپ خطرے میں ہیں تو 112 پر۔",
        "confirm.shareMore": "مزید بتائیں",
        "confirm.callLink": "براہ راست مدد چاہیے؟ 14566 پر کال کریں",
        "confirm.urgentCall": "فوری خطرے میں ہیں؟ ابھی 112 پر کال کریں۔",
        "confirm.urgentSub": "ہماری ٹیم کو بھی فوری جائزے کے لیے مطلع کر دیا گیا ہے۔",
        "confirm.legalTitle": "یہ اس کے تحت آ سکتا ہے:",
        "confirm.contactsTitle": "فوری رابطے",
        "confirm.slaLabel": "جائزے کا ہدف",
        "confirm.reference": "حوالہ نمبر",

        "status.sending": "محفوظ طریقے سے بھیجا جا رہا ہے… براہ کرم یہ صفحہ بند نہ کریں۔",
        "status.error": "آپ کی رپورٹ بھیجی نہیں جا سکی۔ کچھ ضائع نہیں ہوا — براہ کرم دوبارہ کوشش کریں۔",
        "status.retry": "دوبارہ کوشش کریں",

        "privacy.summary": "آپ کی رپورٹ صرف تربیت یافتہ معاون عملہ دیکھ سکتا ہے۔ جب تک آپ کوئی محفوظ طریقہ منتخب نہ کریں، ہم آپ سے رابطہ نہیں کریں گے۔",
        "privacy.collected": "ہم کیا رکھتے ہیں: آپ نے جو لکھا یا کہا، اور بھیجنے کا وقت۔",
        "privacy.access": "کون دیکھ سکتا ہے: آپ کا کیس دیکھنے والے تربیت یافتہ کونسلر۔ نہ عام لوگ، نہ وہ شخص جس کی آپ شکایت کر رہے ہیں۔",
        "privacy.location": "مقام: صرف اس صورت میں جب آپ ایس او ایس دبائیں اور اجازت دیں، اور یہ تقریباً محلے کی سطح تک محفوظ ہوتا ہے، کبھی درست پتہ نہیں۔",
        "privacy.contact": "رابطہ: ہم صرف اسی طریقے سے رابطہ کریں گے جو آپ اگلی اسکرین پر منتخب کریں گے۔ \"مجھ سے رابطہ نہ کریں\" ایک حقیقی آپشن ہے۔",
        "privacy.risk": "براہ کرم ایسی کوئی بات نہ لکھیں جس سے کوئی اور یہ ڈیوائس دیکھے تو آپ کو زیادہ خطرہ ہو۔",

        "followup.title": "آپ سے رابطہ کرنا کس طرح محفوظ ہے؟",
        "followup.doNotContact": "مجھ سے رابطہ نہ کریں",
        "followup.textOnly": "صرف پیغام (ٹیکسٹ)",
        "followup.callOnly": "صرف فون کال",
        "followup.either": "دونوں محفوظ ہیں",
        "followup.timeLabel": "آپ سے کب رابطہ کرنا محفوظ ہے؟ (اختیاری)",
        "followup.timePlaceholder": "مثلاً صرف کام کے دنوں کی صبح",
        "followup.save": "میری ترجیح محفوظ کریں",
        "followup.saved": "محفوظ ہو گیا۔ ہم اس پر عمل کریں گے۔",
        "followup.error": "یہ ترجیح محفوظ نہیں ہو سکی۔ براہ کرم دوبارہ کوشش کریں۔",

        "safety.callNow": "فوری خطرے میں ہیں؟ ابھی 112 پر کال کریں",
        "safety.sos": "ایس او ایس",
        "safety.sosSending": "ایس او ایس بھیجا جا رہا ہے…",
        "safety.quickExit": "فوری اخراج",
        "safety.sosError": "ایس او ایس بھیجا نہیں جا سکا۔ اگر آپ خطرے میں ہیں تو براہ راست 112 پر کال کریں۔",

        "cases.eyebrow": "کیس مینجمنٹ",
        "cases.title": "مقدمات",
        "cases.subtitle": "آنے والی رپورٹس دیکھیں اور مدد کو ترجیح دیں۔",
        "cases.refresh": "تازہ کریں",
        "cases.search": "مقدمات تلاش کریں...",
        "cases.allRisk": "تمام خطرے کی سطحیں",
        "table.case": "مقدمہ",
        "table.incident": "واقعہ",
        "table.district": "ضلع",
        "table.risk": "خطرہ",
        "table.status": "حیثیت",
        "table.time": "وقت",
        "riskmap.eyebrow": "قومی کوریج",
        "riskmap.title": "خطرے کا نقشہ",
        "riskmap.subtitle": "اضلاع میں مقدمات کا ارتکاز دیکھیں۔",
        "riskmap.cardTitle": "بھارت · ضلعی خطرہ",
        "riskmap.cardSub": "رپورٹ شدہ مقدمات کے مطابق خطرے کی سطحیں۔",
        "guidance.eyebrow": "عملے کی معاونت",
        "guidance.title": "رہنمائی",
        "guidance.subtitle": "کونسلرز کے لیے سادہ زبان میں رہنمائی۔",
        "guidance.c1t": "پہلے سنیں",
        "guidance.c1b": "شخص کو اپنی بات اپنے الفاظ میں کہنے دیں، بلا ضرورت مداخلت نہ کریں۔",
        "guidance.c2t": "فوری حفاظت جانچیں",
        "guidance.c2b": "اگر مقدمہ فوری خطرے کی نشاندہی کرے تو شخص کو مناسب انسانی مدد سے جوڑنے کو ترجیح دیں۔",
        "guidance.c3t": "معلومات کی حفاظت کریں",
        "guidance.c3b": "ذاتی معلومات احتیاط سے سنبھالیں اور صرف وہی دیکھیں جو مدد کے عمل کے لیے ضروری ہو۔",
        "guidance.c4t": "ضرورت پر آگے بھیجیں",
        "guidance.c4b": "اعلیٰ ترجیحی صورتحال کا جائزہ تربیت یافتہ عملے کو فوری لینا چاہیے۔",
        "alerts.eyebrow": "ترجیحی نگرانی",
        "alerts.title": "الرٹس",
        "alerts.subtitle": "وہ مقدمات جن پر زیادہ توجہ درکار ہے۔",
        "alerts.show": "دکھائیں",
        "alerts.needsReview": "جائزہ باقی",
        "alerts.reviewedOpt": "جائزہ شدہ",
        "alerts.allOpt": "تمام",
        "alerts.priority": "ترجیح",
        "alerts.criticalHigh": "شدید اور اعلیٰ",
        "alerts.allPriorities": "تمام ترجیحات",
        "alerts.category": "زمرہ",
        "alerts.allCategories": "تمام زمرے",
        "alerts.reset": "ری سیٹ",
        "alerts.viewCase": "مقدمہ دیکھیں",
        "alerts.markReviewed": "جائزہ شدہ نشان زد کریں",
        "alerts.reviewedBadge": "جائزہ شدہ",

        "report.submitError": "ابھی رپورٹ بھیجنا ممکن نہیں۔ براہ کرم دوبارہ کوشش کریں۔",
    },

    bn: {
        "nav.overview": "সংক্ষিপ্ত বিবরণ",
        "nav.newReport": "নতুন প্রতিবেদন",
        "nav.cases": "কেস",
        "nav.riskMap": "ঝুঁকি মানচিত্র",
        "nav.guidance": "নির্দেশনা",
        "nav.alerts": "সতর্কতা",

        "sidebar.helpline": "জাতীয় হেল্পলাইন",
        "sidebar.helplineSub": "সহায়তা লাইন · 14566",
        "sidebar.exit": "ড্যাশবোর্ড থেকে বেরিয়ে যান",

        "topbar.operator": "কাউন্সেলর",
        "topbar.operatorSub": "সহায়তা ডেস্ক",

        "overview.eyebrow": "এথীনা · সংক্ষিপ্ত বিবরণ",
        "overview.title": "সংক্ষিপ্ত বিবরণ",
        "overview.subtitle": "রিয়েল-টাইম হেল্পলাইন পর্যবেক্ষণ এবং কেস সহায়তা।",
        "overview.newReportBtn": "নতুন প্রতিবেদন",

        "stats.total": "মোট কেস",
        "stats.totalSub": "প্রাপ্ত সমস্ত কেস",
        "stats.criticalSub": "তাৎক্ষণিক মনোযোগ",
        "stats.highSub": "অগ্রাধিকার পর্যালোচনা",
        "stats.pending": "অমীমাংসিত",
        "stats.pendingSub": "পর্যালোচনার অপেক্ষায়",

        "risk.low": "কম",
        "risk.moderate": "মাঝারি",
        "risk.high": "বেশি",
        "risk.critical": "সংকটাপন্ন",
        "risk.sectionEyebrow": "ঝুঁকি পর্যবেক্ষণ",
        "risk.sectionTitle": "ঝুঁকি বণ্টন",
        "risk.current": "বর্তমান",
        "risk.casesWord": "কেস",

        "district.eyebrow": "জাতীয় কভারেজ",
        "district.title": "জেলা ঝুঁকি",
        "district.viewMap": "মানচিত্র দেখুন →",
        "district.placeholder": "জেলা ঝুঁকির তথ্য",

        "recent.eyebrow": "কেস ব্যবস্থাপনা",
        "recent.title": "সাম্প্রতিক কেস",
        "recent.viewAll": "সব দেখুন →",
        "loading.cases": "কেস লোড হচ্ছে...",

        "newreport.eyebrow": "জাতীয় হেল্পলাইন · 14566",
        "newreport.title": "আমাদের জানান কী ঘটেছে",
        "newreport.subtitle": "আপনি বলতে বা লিখতে পারেন। যা নিরাপদ মনে হয় শুধু তাই জানান।",

        "lang.choose": "আপনার ভাষা নির্বাচন করুন",

        "channel.question": "এই রিপোর্ট কোন মাধ্যমে এসেছে",
        "channel.hint": "এই রিপোর্ট NHAA-র কোন চ্যানেলের মাধ্যমে আসছে তা ট্যাগ করুন -- শুধু কেস ট্র্যাকিংয়ের জন্য, রিপোর্টকারীকে দেখানো হয় না।",
        "channel.call": "14566 কল",
        "channel.portal": "পোর্টাল",
        "channel.chatbot": "চ্যাটবট",
        "channel.mobile": "মোবাইল অ্যাপ",

        "voice.label": "প্রথমে কণ্ঠস্বর",
        "voice.title": "নিজের ভাষায় আমাদের বলুন",
        "voice.body": "আপনাকে সবকিছু নিখুঁতভাবে ব্যাখ্যা করতে হবে না। শুধু আমাদের বলুন কী ঘটেছে।",
        "voice.tapToSpeak": "কথা বলতে ট্যাপ করুন",
        "voice.listening": "শুনছি… শেষ হলে আবার ট্যাপ করুন",
        "voice.micPermission": "মাইক্রোফোনের অনুমতি প্রয়োজন",
        "voice.sending": "আপনার প্রতিবেদন পাঠানো হচ্ছে…",
        "voice.error": "কিছু ভুল হয়েছে। আবার চেষ্টা করুন।",

        "divider.orType": "অথবা নিচে টাইপ করুন",
        "textarea.placeholder": "আমাদের বলুন কী ঘটেছে...",

        "submit.send": "প্রতিবেদন পাঠান",
        "submit.sending": "পাঠানো হচ্ছে…",
        "evidence.attach": "ছবি বা ফাইল যুক্ত করুন (ঐচ্ছিক)",

        "support.title": "আপনার কথা শোনা হচ্ছে।",
        "support.body": "আপনার তথ্য প্রশিক্ষিত সহায়তা কর্মীদের আপনার পরিস্থিতি বুঝতে এবং সঠিক সহায়তা প্রদান করতে সাহায্য করে।",
        "support.point1": "আপনার তথ্য যত্ন সহকারে পরিচালনা করা হয়।",
        "support.point2": "প্রয়োজনে প্রশিক্ষিত কর্মীরা কেস পর্যালোচনা করতে পারেন।",
        "support.point3": "জরুরি পরিস্থিতিকে অগ্রাধিকার দেওয়া যেতে পারে।",

        "confirm.eyebrow": "প্রতিবেদন গৃহীত হয়েছে",
        "confirm.title": "আমরা আপনার কথা শুনছি।",
        "confirm.body": "আপনি যা জানিয়েছেন তা আমরা পেয়েছি।",
        "confirm.helpTitle": "আপনার প্রতিবেদন নথিভুক্ত হয়েছে।",
        "confirm.small": "এটি একটি প্রোটোটাইপ। আপনার প্রতিবেদন মূল্যায়ন করে কাউন্সেলরের তালিকায় রাখা হয়েছে, তবে এখন কেউ এটি পর্যবেক্ষণ করছেন না। আজ সাহায্য দরকার হলে 14566 নম্বরে কল করুন — বিপদে থাকলে 112 নম্বরে।",
        "confirm.shareMore": "আরও জানান",
        "confirm.callLink": "সরাসরি সহায়তা দরকার? 14566 নম্বরে কল করুন",
        "confirm.urgentCall": "তাৎক্ষণিক বিপদে আছেন? এখনই ১১২ নম্বরে কল করুন।",
        "confirm.urgentSub": "এটি অবিলম্বে পর্যালোচনার জন্য আমাদের দলকেও জানানো হয়েছে।",
        "confirm.legalTitle": "এটি এর আওতায় পড়তে পারে:",
        "confirm.contactsTitle": "তাৎক্ষণিক যোগাযোগ",
        "confirm.slaLabel": "পর্যালোচনার লক্ষ্য",
        "confirm.reference": "রেফারেন্স নম্বর",

        "status.sending": "নিরাপদে পাঠানো হচ্ছে… অনুগ্রহ করে এই পেজটি বন্ধ করবেন না।",
        "status.error": "আপনার প্রতিবেদন পাঠানো যায়নি। কিছুই হারায়নি — অনুগ্রহ করে আবার চেষ্টা করুন।",
        "status.retry": "আবার চেষ্টা করুন",

        "privacy.summary": "আপনার প্রতিবেদন কেবল প্রশিক্ষিত সহায়তা কর্মীরাই দেখতে পারেন। আপনি নিরাপদ কোনো উপায় বেছে না নিলে আমরা আপনার সঙ্গে যোগাযোগ করব না।",
        "privacy.collected": "আমরা যা রাখি: আপনি যা লিখেছেন বা বলেছেন, এবং পাঠানোর সময়।",
        "privacy.access": "কারা দেখতে পারেন: আপনার কেস দেখছেন এমন প্রশিক্ষিত কাউন্সেলররা। সাধারণ মানুষ নন, এবং যাঁর বিরুদ্ধে অভিযোগ করছেন তিনিও নন।",
        "privacy.location": "অবস্থান: কেবল আপনি এসওএস চাপলে ও অনুমতি দিলে, এবং তা প্রায় এলাকা পর্যন্তই সংরক্ষিত হয়, কখনও নির্দিষ্ট ঠিকানা নয়।",
        "privacy.contact": "যোগাযোগ: পরের স্ক্রিনে আপনি যেভাবে বেছে নেবেন কেবল সেভাবেই যোগাযোগ করা হবে। \"আমার সঙ্গে যোগাযোগ করবেন না\" একটি প্রকৃত বিকল্প।",
        "privacy.risk": "অন্য কেউ এই ডিভাইস দেখলে আপনার বিপদ বাড়তে পারে, এমন কিছু অনুগ্রহ করে লিখবেন না।",

        "followup.title": "আপনার সঙ্গে কীভাবে যোগাযোগ করা নিরাপদ?",
        "followup.doNotContact": "আমার সঙ্গে যোগাযোগ করবেন না",
        "followup.textOnly": "শুধু বার্তা (টেক্সট)",
        "followup.callOnly": "শুধু ফোন কল",
        "followup.either": "দুটোই নিরাপদ",
        "followup.timeLabel": "কখন যোগাযোগ করা নিরাপদ? (ঐচ্ছিক)",
        "followup.timePlaceholder": "যেমন কেবল কর্মদিবসের সকাল",
        "followup.save": "আমার পছন্দ সংরক্ষণ করুন",
        "followup.saved": "সংরক্ষিত হয়েছে। আমরা এটি মেনে চলব।",
        "followup.error": "পছন্দটি সংরক্ষণ করা যায়নি। অনুগ্রহ করে আবার চেষ্টা করুন।",

        "safety.callNow": "তাৎক্ষণিক বিপদে আছেন? এখনই ১১২ নম্বরে কল করুন",
        "safety.sos": "এসওএস",
        "safety.sosSending": "এসওএস পাঠানো হচ্ছে…",
        "safety.quickExit": "দ্রুত প্রস্থান",
        "safety.sosError": "এসওএস পাঠানো যায়নি। আপনি বিপদে থাকলে সরাসরি ১১২ নম্বরে কল করুন।",

        "cases.eyebrow": "কেস ব্যবস্থাপনা",
        "cases.title": "মামলা",
        "cases.subtitle": "আসা প্রতিবেদন পর্যালোচনা করুন ও সহায়তাকে অগ্রাধিকার দিন।",
        "cases.refresh": "রিফ্রেশ",
        "cases.search": "মামলা খুঁজুন...",
        "cases.allRisk": "সব ঝুঁকির স্তর",
        "table.case": "মামলা",
        "table.incident": "ঘটনা",
        "table.district": "জেলা",
        "table.risk": "ঝুঁকি",
        "table.status": "অবস্থা",
        "table.time": "সময়",
        "riskmap.eyebrow": "জাতীয় পরিধি",
        "riskmap.title": "ঝুঁকি মানচিত্র",
        "riskmap.subtitle": "জেলাভিত্তিক মামলার ঘনত্ব পর্যবেক্ষণ করুন।",
        "riskmap.cardTitle": "ভারত · জেলা ঝুঁকি",
        "riskmap.cardSub": "রিপোর্ট করা মামলার ভিত্তিতে ঝুঁকির স্তর।",
        "guidance.eyebrow": "কর্মী সহায়তা",
        "guidance.title": "নির্দেশনা",
        "guidance.subtitle": "কাউন্সেলরদের জন্য সহজ ভাষায় সহায়তা নির্দেশনা।",
        "guidance.c1t": "আগে শুনুন",
        "guidance.c1b": "ব্যক্তিকে নিজের ভাষায় পরিস্থিতি বলতে দিন, অপ্রয়োজনে বাধা দেবেন না।",
        "guidance.c2t": "তাৎক্ষণিক নিরাপত্তা দেখুন",
        "guidance.c2b": "মামলাটি তাৎক্ষণিক বিপদ নির্দেশ করলে ব্যক্তিকে উপযুক্ত মানবিক সহায়তার সঙ্গে যুক্ত করাকে অগ্রাধিকার দিন।",
        "guidance.c3t": "তথ্য সুরক্ষিত রাখুন",
        "guidance.c3b": "ব্যক্তিগত তথ্য সাবধানে সামলান এবং সহায়তা প্রক্রিয়ার জন্য প্রয়োজনীয় তথ্যই দেখুন।",
        "guidance.c4t": "প্রয়োজনে উপরে পাঠান",
        "guidance.c4b": "উচ্চ অগ্রাধিকারের পরিস্থিতি প্রশিক্ষিত কর্মীদের দ্রুত পর্যালোচনা করা উচিত।",
        "alerts.eyebrow": "অগ্রাধিকার পর্যবেক্ষণ",
        "alerts.title": "সতর্কতা",
        "alerts.subtitle": "যেসব মামলায় বেশি মনোযোগ দরকার।",
        "alerts.show": "দেখান",
        "alerts.needsReview": "পর্যালোচনা বাকি",
        "alerts.reviewedOpt": "পর্যালোচিত",
        "alerts.allOpt": "সব",
        "alerts.priority": "অগ্রাধিকার",
        "alerts.criticalHigh": "গুরুতর ও উচ্চ",
        "alerts.allPriorities": "সব অগ্রাধিকার",
        "alerts.category": "বিভাগ",
        "alerts.allCategories": "সব বিভাগ",
        "alerts.reset": "রিসেট",
        "alerts.viewCase": "মামলা দেখুন",
        "alerts.markReviewed": "পর্যালোচিত চিহ্নিত করুন",
        "alerts.reviewedBadge": "পর্যালোচিত",

        "report.submitError": "এই মুহূর্তে প্রতিবেদন পাঠানো সম্ভব হচ্ছে না। আবার চেষ্টা করুন।",
    },

};

// Languages offered in the UI language switcher, in display order.
// Kept separate from understanding.py's SUPPORTED_LANGUAGES (backend
// NLU coverage) and from TRANSLATIONS (which language keys actually
// exist above) -- this is just what shows up as a switchable option.
const UI_LANGUAGES = [
    { code: "en", label: "English" },
    { code: "hi", label: "हिंदी" },
    { code: "te", label: "తెలుగు" },
    { code: "ur", label: "اردو" },
    { code: "bn", label: "বাংলা" },
];

const UI_LANG_STORAGE_KEY = "athena_ui_lang";

function getUiLanguage() {
    try {
        const stored = localStorage.getItem(UI_LANG_STORAGE_KEY);
        return (stored && TRANSLATIONS[stored]) ? stored : "en";
    } catch (error) {
        return "en";
    }
}

// Falls back to the English string, then to the raw key itself, so a
// missing translation is visibly wrong (shows the key) rather than
// silently blank -- easier to spot while extending language coverage.
function t(key) {
    const lang = getUiLanguage();
    const table = TRANSLATIONS[lang] || TRANSLATIONS.en;
    return table[key] || TRANSLATIONS.en[key] || key;
}

function applyTranslations() {

    document.querySelectorAll("[data-i18n]").forEach(el => {
        el.textContent = t(el.dataset.i18n);
    });

    document.querySelectorAll("[data-i18n-placeholder]").forEach(el => {
        el.setAttribute("placeholder", t(el.dataset.i18nPlaceholder));
    });

    document.querySelectorAll("[data-i18n-title]").forEach(el => {
        el.setAttribute("title", t(el.dataset.i18nTitle));
    });

    // Icon-only controls -- the visible glyph is aria-hidden, so this
    // label is the only thing a screen reader has to go on, and it has
    // to switch language with everything else.
    document.querySelectorAll("[data-i18n-aria-label]").forEach(el => {
        el.setAttribute("aria-label", t(el.dataset.i18nAriaLabel));
    });

    const select = document.getElementById("uiLanguageSelect");
    if (select) {
        select.value = getUiLanguage();
    }

}

// Single entry point for changing the UI language, called both from
// the topbar switcher and from the New Report page's language buttons
// (see athena.js) -- one choice drives both the interface chrome and
// which language the complaint text gets tagged as, since keeping
// them in sync is what an actual first-time reporter expects: picking
// Telugu should mean everything they see is in Telugu, not just the
// eventual NLU response.
function setUiLanguage(lang) {

    if (!TRANSLATIONS[lang]) {
        lang = "en";
    }

    try {
        localStorage.setItem(UI_LANG_STORAGE_KEY, lang);
    } catch (error) {
        // localStorage unavailable (private browsing, etc.) -- the
        // language still applies for this page load, it just won't
        // persist across reloads.
    }

    // Urdu is right-to-left. Setting dir/lang on <html> is the minimum
    // that makes text, punctuation and input caret behave correctly --
    // a full RTL layout mirror (sidebar, tables, icon order) is a
    // bigger change than this pass takes on, so this deliberately
    // fixes reading direction without pretending the whole dashboard
    // has been mirrored.
    document.documentElement.setAttribute("lang", lang);
    document.documentElement.setAttribute(
        "dir",
        lang === "ur" ? "rtl" : "ltr"
    );

    applyTranslations();

    if (typeof window.onUiLanguageChange === "function") {
        window.onUiLanguageChange(lang);
    }

}

document.addEventListener("DOMContentLoaded", () => {

    // Re-apply the stored language's direction on load, not just when
    // the switcher changes -- otherwise someone who chose Urdu last
    // visit comes back to Urdu text laid out left-to-right.
    const storedLang = getUiLanguage();
    document.documentElement.setAttribute("lang", storedLang);
    document.documentElement.setAttribute(
        "dir",
        storedLang === "ur" ? "rtl" : "ltr"
    );

    applyTranslations();

    const select = document.getElementById("uiLanguageSelect");

    if (select) {

        select.innerHTML = UI_LANGUAGES.map(
            l => `<option value="${l.code}">${l.label}</option>`
        ).join("");

        select.value = getUiLanguage();

        select.addEventListener("change", () => {
            setUiLanguage(select.value);
        });

    }

});
