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

    parts = []

    response_text = (result.get("response") or "").strip()

    if response_text:
        parts.append(response_text)
    elif result.get("reason"):
        parts.append(
            "Thank you for telling us. A trained counsellor will review this."
        )

    risk = result.get("risk") or {}
    risk_tier = risk.get("risk_tier")

    if risk_tier in ("Critical", "High"):
        parts.append(
            "⚠️ If you are in immediate danger, call 112 now. "
            "This report has been flagged for urgent human review."
        )

    contacts = result.get("emergency_contacts") or []

    if contacts:
        lines = "\n".join(
            f"• {contact['label']}: {contact['phone']}"
            for contact in contacts[:4]
        )
        parts.append(f"Numbers you can call:\n{lines}")

    docket = result.get("nhaa_docket") or {}
    reference = docket.get("docket_id") or result.get("case_id")

    if reference:
        parts.append(f"Your reference: {reference}")

    return "\n\n".join(parts)
