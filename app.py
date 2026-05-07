import streamlit as st
from transformers import pipeline
import re
from difflib import SequenceMatcher
import ipaddress

# --------------------
# Page Config
st.set_page_config(page_title="Email, IP & URL Analyzer", page_icon="📧", layout="centered")

st.title("📧 Email, IP & URL Analyzer")
st.write("Check if an email is **Spam/Ham**, detect **URLs inside it**, and verify if the sender's **IP or URL is safe**.")

# --------------------
# Input fields
email_text = st.text_area("✉️ Enter Email Text", height=150)
ip_address = st.text_input("🌍 Enter Sender IP Address", "8.8.8.8")
manual_url = st.text_input("🔗 Enter a URL to Check (optional)")

# --------------------
# Spam detection model
@st.cache_resource
def load_model():
    return pipeline("text-classification", model="IreNkweke/HamOrSpamModel")

spam_classifier = load_model()
label_map = {"LABEL_0": "Not Spam", "LABEL_1": "Spam"}

def detect_spam(email_text):
    result = spam_classifier(email_text)
    label = label_map.get(result[0]['label'], result[0]['label'])
    score = result[0]['score']
    return label, score

# --------------------
# URL Extraction from email
def extract_urls(text):
    url_pattern = r"(https?://[^\s,)\]]+|www\.[^\s,)\]]+|\b[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b)"
    urls = re.findall(url_pattern, text)
    urls = list(set(urls))  # remove duplicates
    return urls

# --------------------
# Manual URL Detector
BLACKLISTED_URLS = [
    "http://malicious.com",
    "http://phishing.testurl.org",
    "http://example-bad-domain.biz",
    "http://fake-login.net",
    "http://steal-your-info.com",
    "http://update-account.com",
    "http://secure-login.net",
    "http://verify-info.org",
    "http://banking-alerts.com",
    "http://reset-password.info"
]

SUSPICIOUS_KEYWORDS = [
    "login", "secure", "update", "verify", "account", "banking",
    "confirm", "password", "reset", "auth", "webmail", "credential",
    "signin", "security-alert", "payment", "billing", "access", "support"
]

def is_similar(a, b, threshold=0.8):
    return SequenceMatcher(None, a, b).ratio() >= threshold

def manual_url_check(url):
    url_lower = url.lower()
    url_no_protocol = re.sub(r'^https?://', '', url_lower)

    for blacklisted in BLACKLISTED_URLS:
        blacklisted_no_protocol = re.sub(r'^https?://', '', blacklisted.lower())
        if url_no_protocol == blacklisted_no_protocol or is_similar(url_no_protocol, blacklisted_no_protocol):
            return False  # Unsafe

    for keyword in SUSPICIOUS_KEYWORDS:
        if keyword in url_no_protocol:
            return False  # Unsafe

    return True  # Safe

# --------------------
# Manual IP Detector
BLACKLISTED_IPS = [
    "1.2.3.4", "123.45.67.89", "198.51.100.42", "203.0.113.77",
    "5.6.7.8", "185.220.101.1", "66.249.66.1", "209.85.231.104",
    "192.0.2.123", "203.0.113.200"
]

VPN_PROXY_TOR_IPS = {
    "185.220.101.1": {"vpn": False, "proxy": False, "tor": True},
    "5.6.7.8": {"vpn": True, "proxy": False, "tor": False},
    "198.51.100.42": {"vpn": False, "proxy": True, "tor": False},
    "66.249.66.1": {"vpn": False, "proxy": False, "tor": True},
    "209.85.231.104": {"vpn": True, "proxy": False, "tor": False},
    "192.0.2.123": {"vpn": False, "proxy": True, "tor": False},
}

SUSPICIOUS_RANGES = [
    ("198.51.100.0", "198.51.100.255"),
    ("203.0.113.0", "203.0.113.255")
]

def ip_in_range(ip, start, end):
    ip_val = int(ipaddress.IPv4Address(ip))
    return int(ipaddress.IPv4Address(start)) <= ip_val <= int(ipaddress.IPv4Address(end))

def manual_ip_check(ip_address):
    ip = ip_address.strip()
    
    is_safe = True
    vpn_used = False
    proxy_used = False
    tor_used = False

    if ip in BLACKLISTED_IPS:
        is_safe = False

    if ip in VPN_PROXY_TOR_IPS:
        vpn_used = VPN_PROXY_TOR_IPS[ip].get("vpn", False)
        proxy_used = VPN_PROXY_TOR_IPS[ip].get("proxy", False)
        tor_used = VPN_PROXY_TOR_IPS[ip].get("tor", False)
        is_safe = False

    for start, end in SUSPICIOUS_RANGES:
        if ip_in_range(ip, start, end):
            is_safe = False
            break

    return is_safe, vpn_used, proxy_used, tor_used

# --------------------
# Analyze Button
if st.button("🔍 Analyze"):
    if email_text.strip() == "" and manual_url.strip() == "" and ip_address.strip() == "":
        st.warning("⚠️ Please enter at least one input (Email, IP, or URL).")
    else:
        st.subheader("📊 Analysis Results")

        # Spam detection
        if email_text.strip():
            spam_label, spam_score = detect_spam(email_text)
            if spam_label == "Spam":
                st.error(f"🚨 Spam Detected (Confidence: {spam_score:.2f})")
            else:
                st.success(f"✅ Not Spam (Confidence: {spam_score:.2f})")

            # Extract URLs
            urls = extract_urls(email_text)
            st.subheader("🔗 URLs Found in Email")
            if urls:
                for u in urls:
                    safe = manual_url_check(u)
                    if safe:
                        st.success(f"✅ {u} (Safe)")
                    else:
                        st.error(f"🚨 {u} (Unsafe)")
            else:
                st.info("No URLs found in the email text.")

        # IP check
        if ip_address.strip():
            st.subheader("🌍 IP Check")
            ip_safe, vpn, proxy, tor = manual_ip_check(ip_address)
            status_text = "Safe ✅" if ip_safe else "Unsafe ⚠️"
            st.write(f"{ip_address}: {status_text}")
            col1, col2, col3 = st.columns(3)
            col1.metric("VPN Used", "Yes" if vpn else "No")
            col2.metric("Proxy Used", "Yes" if proxy else "No")
            col3.metric("Tor Used", "Yes" if tor else "No")

        # Manual URL Check
        if manual_url.strip():
            st.subheader("🔗 Manual URL Check")
            safe = manual_url_check(manual_url)
            if safe:
                st.success(f"✅ {manual_url} (Safe)")
            else:
                st.error(f"🚨 {manual_url} (Unsafe)")
