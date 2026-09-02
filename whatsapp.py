# ============================================================
# ATHENA — WHATSAPP CHANNEL (Twilio)
# ============================================================

"""
Real WhatsApp, running the same pipeline as everything else.

Why Twilio's sandbox rather than Meta's Cloud API directly: the Cloud
API needs a Meta Business account cleared through Meta's verification
flow, and a phone number that is NOT already a normal WhatsApp account
-- registering one moves that number off consumer WhatsApp for good.
The sandbox needs neither. It lends you a shared WhatsApp number,
people opt in by messaging it a join code, and no number of ours is
ever consumed. For proving the channel works end to end, that is the
whole job.

What this is NOT: a production WhatsApp deployment. The sandbox number
is shared with every other Twilio developer, recipients must opt in
before they can be messaged, and a joined session lapses after a few
days. Those are the honest limits of the sandbox, not of Athena --
moving to a dedicated Cloud API number later changes the credentials
and the sender, not a line of pipeline code.

Signature verification is implemented against Twilio's documented
scheme rather than pulled in via their SDK -- it is ~15 lines of
stdlib hmac, and this project already avoids adding a dependency for
something that small. Without it the webhook is a public URL that
will run the pipeline for anyone who POSTs to it.
"""

import base64
import hashlib
import hmac
import os
from urllib.parse import urlparse, urlunparse

import requests

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")

# Twilio caps a single WhatsApp body at 1600 characters. Athena's
# grounded replies are normally far shorter, but a legal-guidance
# heavy answer can run long, and a silently truncated reply to
# someone in crisis is worse than a visibly shortened one.
WHATSAPP_MAX_BODY = 1500


def _signature_for(url, form_params):
    """
    Twilio's scheme: the full webhook URL, then every POST parameter
    appended in alphabetical order (name then value, no separators),
    HMAC-SHA1 with the auth token, base64.
    """

    payload = url
    for key in sorted(form_params):
        payload += key + str(form_params[key])

    return base64.b64encode(
        hmac.new(
            TWILIO_AUTH_TOKEN.encode("utf-8"),
            payload.encode("utf-8"),
            hashlib.sha1,
        ).digest()
    ).decode("utf-8")


def signature_is_valid(urls, form_params, signature_header):
    """
    Verifies X-Twilio-Signature against any of the candidate URLs this
    request could have been signed as (see candidate_urls).

    Accepts a single URL string too, so the documented single-URL case
    and the tests read naturally.

    Returns True when no auth token is configured -- a local run
    without credentials should still be testable -- so deployments
    MUST set TWILIO_AUTH_TOKEN. app.py logs loudly when it isn't.
    """

    if not TWILIO_AUTH_TOKEN:
        return True

    if not signature_header:
        return False

    if isinstance(urls, str):
        urls = [urls]

    for url in urls:
        if hmac.compare_digest(
            _signature_for(url, form_params), signature_header
        ):
            return True

    # Logged because a signature failure is otherwise invisible: Twilio
    # just sees a 403 and the reporter sees silence. Never logs the
    # signature or any message content.
    print(
        "[whatsapp] signature did not match any candidate URL: "
        f"{urls} -- if this is a real Twilio request, set "
        "TWILIO_WEBHOOK_URL to the exact URL configured in the console."
    )

    return False


def candidate_urls(request):
    """
    Every URL this request could plausibly have been signed as.

    Twilio signs the URL it was *configured* with. Behind a TLS-
    terminating proxy (Railway, Render, Fly, anything with a load
    balancer) the app sees something different: usually http:// where
    the caller used https://, sometimes an internal hostname entirely.
    Signing over the wrong one fails every legitimate request, which
    looks identical to an attack and is miserable to debug -- the
    webhook simply goes quiet.

    Rather than guessing which rewrite a given host performs, this
    returns the plausible candidates and the caller accepts a match on
    any. That is not a weakening: an attacker still cannot produce a
    valid HMAC for any of them without the auth token.

    TWILIO_WEBHOOK_URL short-circuits the guessing entirely. Set it to
    the exact URL configured in the Twilio console and the ambiguity
    disappears.
    """

    configured = os.getenv("TWILIO_WEBHOOK_URL")

    if configured:
        return [configured.strip()]

    raw = str(request.url)
    urls = [raw]

    parts = urlparse(raw)

    # Whatever the proxy says the original scheme was.
    forwarded_proto = request.headers.get("x-forwarded-proto")
    if forwarded_proto:
        urls.append(urlunparse(parts._replace(scheme=forwarded_proto)))

    # Twilio webhooks are configured over https in practice; include it
    # explicitly in case no proxy header is set at all.
    if parts.scheme != "https":
        urls.append(urlunparse(parts._replace(scheme="https")))

    # The proxy may also rewrite the host -- rebuild from the original
    # Host/X-Forwarded-Host as well.
    forwarded_host = (
        request.headers.get("x-forwarded-host")
        or request.headers.get("host")
    )
    if forwarded_host and forwarded_host != parts.netloc:
        urls.append(
            urlunparse(
                parts._replace(scheme="https", netloc=forwarded_host)
            )
        )

    # De-duplicate, preserving order.
    seen = set()
    unique = []
    for url in urls:
        if url not in seen:
            seen.add(url)
            unique.append(url)

    return unique


def download_media(media_url):
    """
    Fetches a media attachment (voice note, photo) from Twilio.

    Media URLs are NOT public -- they need the account's own basic
    auth. Returns (bytes, content_type), or (None, None) on any
    failure: a media fetch that fails must degrade to "we couldn't
    read that attachment", never take down the reply to someone who
    just reported an assault.
    """

    if not (TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN):
        return None, None

    try:
        response = requests.get(
            media_url,
            auth=(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN),
            timeout=20,
        )
        response.raise_for_status()

    except Exception as e:
        print(f"[whatsapp] media download failed: {type(e).__name__}: {e}")
        return None, None

    return response.content, response.headers.get("Content-Type", "")


TWILIO_MESSAGES_URL = (
    "https://api.twilio.com/2010-04-01/Accounts/{sid}/Messages.json"
)


def send_message(to, body, from_number):
    """
    Sends a WhatsApp message through Twilio's REST API, outside the
    webhook response.

    Needed because some work cannot finish inside Twilio's ~15s webhook
    timeout. Measured on a 14-second voice note: transcription is fast
    (~0.5s), but librosa's acoustic feature extraction -- the pitch and
    pause analysis the SVI's voice half is built on -- takes ~20s, so
    the reply was never going to be sent in time. Rather than drop the
    voice features (which would gut the multimodal assessment that is
    the point of this project) the webhook acknowledges immediately and
    the real answer follows through here.

    Returns True on success. Never raises: a failed send is logged and
    swallowed, because this runs in a background task where an
    exception would vanish silently anyway.
    """

    if not (TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN):
        print("[whatsapp] cannot send: Twilio credentials not configured")
        return False

    try:
        response = requests.post(
            TWILIO_MESSAGES_URL.format(sid=TWILIO_ACCOUNT_SID),
            auth=(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN),
            data={
                "From": from_number,
                "To": to,
                "Body": (body or "")[:WHATSAPP_MAX_BODY],
            },
            timeout=20,
        )
        response.raise_for_status()

    except Exception as e:
        print(f"[whatsapp] send failed: {type(e).__name__}: {e}")
        return False

    return True


def _escape_xml(text):
    return (
        str(text)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def build_reply(body_text):
    """
    TwiML for a single WhatsApp reply.

    Truncation is explicit and visible -- a reply cut off mid-sentence
    reads as a broken system exactly when someone needs to trust it,
    so an over-long body ends with a clear marker and a pointer to the
    helpline that can say the rest.
    """

    text = (body_text or "").strip()

    if not text:
        text = (
            "Sorry — I couldn't produce a reply just then. "
            "If you are in danger right now, call 112. "
            "For support, call the helpline on 14566."
        )

    if len(text) > WHATSAPP_MAX_BODY:
        text = (
            text[:WHATSAPP_MAX_BODY].rstrip()
            + "…\n\n(Message shortened. Call 14566 to speak to a counsellor.)"
        )

    return (
        '<?xml version="1.0" encoding="UTF-8"?>'
        f"<Response><Message>{_escape_xml(text)}</Message></Response>"
    )


# The wrapper around the AI's answer -- urgency warning, contact list
# header, reference label -- was English regardless of what language
# the person wrote in. On a report filed in Hindi that meant a reply
# that was part Hindi, part English, which is precisely the barrier
# this project exists to remove: someone who writes in Hindi because
# that is the language they are comfortable in should not have to read
# English to find out they should call 112.
#
# Only these fixed strings are translated here -- the AI's own answer
# already comes back in the reporter's language from response_engine,
# and helpline NAMES stay as they are, because they are what a person
# will hear and see when they actually call.
REPLY_STRINGS = {
    "en": {
        "urgent": "⚠️ If you are in immediate danger, call 112 now. "
                  "This report has been flagged for urgent human review.",
        "contacts": "Numbers you can call:",
        "reference": "Your reference",
        "received": "Thank you for telling us. A trained counsellor will review this.",
    },
    "hi": {
        "urgent": "⚠️ अगर आप अभी खतरे में हैं, तो तुरंत 112 पर कॉल करें। "
                  "यह रिपोर्ट तत्काल मानवीय समीक्षा के लिए भेज दी गई है।",
        "contacts": "आप इन नंबरों पर कॉल कर सकते हैं:",
        "reference": "आपका संदर्भ नंबर",
        "received": "हमें बताने के लिए धन्यवाद। एक प्रशिक्षित काउंसलर इसे देखेंगे।",
    },
    "te": {
        "urgent": "⚠️ మీరు ఇప్పుడు ప్రమాదంలో ఉంటే, వెంటనే 112కి కాల్ చేయండి. "
                  "ఈ ఫిర్యాదు తక్షణ మానవ సమీక్ష కోసం పంపబడింది.",
        "contacts": "మీరు ఈ నంబర్లకు కాల్ చేయవచ్చు:",
        "reference": "మీ సూచన నంబర్",
        "received": "మాకు తెలియజేసినందుకు ధన్యవాదాలు. శిక్షణ పొందిన కౌన్సెలర్ దీన్ని సమీక్షిస్తారు.",
    },
    "ur": {
        "urgent": "⚠️ اگر آپ اس وقت خطرے میں ہیں تو فوراً 112 پر کال کریں۔ "
                  "یہ رپورٹ فوری انسانی جائزے کے لیے بھیج دی گئی ہے۔",
        "contacts": "آپ ان نمبروں پر کال کر سکتے ہیں:",
        "reference": "آپ کا حوالہ نمبر",
        "received": "بتانے کے لیے شکریہ۔ ایک تربیت یافتہ کونسلر اسے دیکھے گا۔",
    },
    "bn": {
        "urgent": "⚠️ আপনি যদি এখন বিপদে থাকেন, অবিলম্বে ১১২ নম্বরে কল করুন। "
                  "এই প্রতিবেদনটি জরুরি মানবিক পর্যালোচনার জন্য পাঠানো হয়েছে।",
        "contacts": "আপনি এই নম্বরগুলিতে কল করতে পারেন:",
        "reference": "আপনার রেফারেন্স নম্বর",
        "received": "জানানোর জন্য ধন্যবাদ। একজন প্রশিক্ষিত কাউন্সেলর এটি দেখবেন।",
    },
}


# Romanized variants, used when the reporter typed in Latin letters.
# Someone writing "mujhe dar lag raha hai" rather than Devanagari
# often does so because they don't read the native script comfortably
# -- response_engine already replies in whatever script the person
# wrote in for exactly this reason, and answering them in Devanagari
# here would undo that in the part of the message that matters most.
ROMANIZED_REPLY_STRINGS = {
    "hi": {
        "urgent": "⚠️ Agar aap abhi khatre mein hain, to turant 112 par call karein. "
                  "Yeh report turant maanviya sameeksha ke liye bhej di gayi hai.",
        "contacts": "Aap in numbers par call kar sakte hain:",
        "reference": "Aapka reference number",
        "received": "Hamein batane ke liye dhanyavaad. Ek prashikshit counsellor ise dekhenge.",
    },
    "te": {
        "urgent": "⚠️ Meeru ippudu pramadam lo unte, ventane 112 ki call cheyandi. "
                  "Ee phiryadu takshana manava sameeksha kosam pampabadindi.",
        "contacts": "Meeru ee numbers ki call cheyavachu:",
        "reference": "Mee reference number",
        "received": "Maaku teliyajesinanduku dhanyavaadalu. Shikshana pondina counsellor deenni sameekshistaru.",
    },
    "ur": {
        "urgent": "⚠️ Agar aap is waqt khatre mein hain to foran 112 par call karein. "
                  "Yeh report fori insani jaaize ke liye bhej di gayi hai.",
        "contacts": "Aap in numbers par call kar sakte hain:",
        "reference": "Aap ka reference number",
        "received": "Batane ke liye shukriya. Ek tarbiyat yafta counsellor ise dekhega.",
    },
    "bn": {
        "urgent": "⚠️ Apni jodi ekhon bipode thaken, obilombe 112 nombore call korun. "
                  "Ei protibedonti joruri manobik porjalochonar jonno pathano hoyeche.",
        "contacts": "Apni ei nombor gulite call korte paren:",
        "reference": "Apnar reference number",
        "received": "Janano jonno dhonnobad. Ekjon proshikkhito counsellor eti dekhben.",
    },
}


def _strings_for(result):
    """
    Reply strings in the language AND script the report was actually
    written in, falling back to English for anything unrecognised.
    """

    incident = result.get("incident") or {}
    language = (incident.get("language") or "en").strip().lower()
    script = (incident.get("script") or "").strip().lower()

    if script == "romanized" and language in ROMANIZED_REPLY_STRINGS:
        return ROMANIZED_REPLY_STRINGS[language]

    return REPLY_STRINGS.get(language, REPLY_STRINGS["en"])


def format_pipeline_reply(result):
    """
    Turns a pipeline result into what actually gets sent back on
    WhatsApp.

    Mirrors what the web confirmation screen shows, with the same
    honesty rule: a Critical/High case is told to call 112 itself
    rather than reassured that help is coming, because Athena flags a
    case for a human -- it does not dispatch anyone (see risk.py's
    RESPONSE_PROTOCOL note).
    """

    strings = _strings_for(result)

    parts = []

    response_text = (result.get("response") or "").strip()

    if response_text:
        parts.append(response_text)
    elif result.get("reason"):
        parts.append(strings["received"])

    risk = result.get("risk") or {}
    risk_tier = risk.get("risk_tier")

    if risk_tier in ("Critical", "High"):
        parts.append(strings["urgent"])

    contacts = result.get("emergency_contacts") or []

    if contacts:
        lines = "\n".join(
            f"• {contact['label']}: {contact['phone']}"
            for contact in contacts[:4]
        )
        parts.append(f"{strings['contacts']}\n{lines}")

    docket = result.get("nhaa_docket") or {}
    reference = docket.get("docket_id") or result.get("case_id")

    if reference:
        parts.append(f"{strings['reference']}: {reference}")

    return "\n\n".join(parts)
