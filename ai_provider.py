# ai_provider.py — Global AI Provider Helper
# ใช้ร่วมกันทุกหน้า เลือก provider จาก st.session_state["ai_provider"]

import streamlit as st
import json, os

# ─── Provider Constants ────────────────────────────────────────────────────────
PROVIDER_CLOUD     = "cloud"      # Typhoon (default) / Vertex AI (Chat only)
PROVIDER_LOCAL     = "local"      # Ollama
PROVIDER_ONPREMISE = "onpremise"  # On-Premise OpenAI-compatible

AI_PROVIDER_OPTIONS = {
    "☁️ Cloud AI (Typhoon / Vertex)": PROVIDER_CLOUD,
    "💻 Local AI (Ollama)":           PROVIDER_LOCAL,
    "🖥️ On-Premise AI":               PROVIDER_ONPREMISE,
}

# ─── Default model per provider ───────────────────────────────────────────────
TYPHOON_BASE_URL = "https://api.opentyphoon.ai/v1"
TYPHOON_MODEL    = "typhoon-v2.5-30b-a3b-instruct"
VERTEX_LOCATION  = "asia-southeast1"
VERTEX_MODEL     = "gemini-2.5-flash"


def init_provider_state():
    """เรียกใน sidebar ทุกหน้าเพื่อ init session state"""
    ss = st.session_state
    ss.setdefault("ai_provider",      PROVIDER_CLOUD)
    ss.setdefault("local_url",        "http://localhost:11434/v1")
    ss.setdefault("local_model",      "typhoon2-8b")
    ss.setdefault("onpremise_url",    "http://your-server:11434/v1")
    ss.setdefault("onpremise_model",  "typhoon2-8b")

    # API keys from secrets
    if "api_key_global" not in ss:
        try:    ss["api_key_global"] = st.secrets["api_key"]
        except: ss["api_key_global"] = ""
    if "vertex_project_id" not in ss:
        try:    ss["vertex_project_id"] = st.secrets["vertex_project_id"]
        except: ss["vertex_project_id"] = ""
    if "vertex_sa_json" not in ss:
        try:    ss["vertex_sa_json"] = st.secrets["vertex_sa_json"]
        except: ss["vertex_sa_json"] = ""


def render_provider_sidebar():
    """แสดง AI Provider selector ใน sidebar — เรียกจาก with st.sidebar"""
    init_provider_state()
    ss = st.session_state

    st.markdown("---")
    st.markdown(
        "<p style='color:rgba(255,255,255,0.6);font-size:11px;font-weight:700;"
        "text-transform:uppercase;letter-spacing:1px;margin-bottom:6px;'>🤖 AI Provider</p>",
        unsafe_allow_html=True
    )

    # Radio selector — label ใช้สี white override
    provider_label = st.radio(
        "AI Provider",
        options=list(AI_PROVIDER_OPTIONS.keys()),
        index=list(AI_PROVIDER_OPTIONS.values()).index(ss["ai_provider"]),
        key="ai_provider_radio",
        label_visibility="collapsed",
    )
    ss["ai_provider"] = AI_PROVIDER_OPTIONS[provider_label]

    current = ss["ai_provider"]

    # ── Cloud AI ──
    if current == PROVIDER_CLOUD:
        typhoon_ok = bool(ss.get("api_key_global"))
        vertex_ok  = bool(ss.get("vertex_project_id") and ss.get("vertex_sa_json"))
        st.markdown(
            f"<small style='color:rgba(255,255,255,0.65);'>"
            f"{'✅' if typhoon_ok else '❌'} Typhoon API<br>"
            f"{'✅' if vertex_ok  else '⚠️'} Vertex AI (Chat)<br>"
            f"<span style='opacity:0.5;font-size:10px;'>ตั้งค่าใน Streamlit Secrets</span>"
            f"</small>",
            unsafe_allow_html=True
        )

    # ── Local AI (Ollama) ──
    elif current == PROVIDER_LOCAL:
        ss["local_url"] = st.text_input(
            "Ollama URL", value=ss["local_url"], key="local_url_inp",
            help="เช่น http://localhost:11434/v1"
        )
        ss["local_model"] = st.text_input(
            "Model name", value=ss["local_model"], key="local_model_inp",
            help="เช่น typhoon2-8b, llama3, gemma3"
        )
        with st.expander("📖 วิธีติดตั้ง Ollama"):
            st.markdown("""
**1. ดาวน์โหลด Ollama**
```
https://ollama.com/download
```
**2. ดึงโมเดล**
```bash
ollama pull typhoon2-8b
ollama pull llama3.2
```
**3. เริ่ม server**
```bash
ollama serve
```
URL เริ่มต้น: `http://localhost:11434`
""")

    # ── On-Premise AI ──
    elif current == PROVIDER_ONPREMISE:
        ss["onpremise_url"] = st.text_input(
            "Server URL", value=ss["onpremise_url"], key="onprem_url_inp",
            help="OpenAI-compatible endpoint เช่น http://192.168.1.100:8000/v1"
        )
        ss["onpremise_model"] = st.text_input(
            "Model name", value=ss["onpremise_model"], key="onprem_model_inp",
        )
        with st.expander("📖 วิธีติดตั้ง On-Premise"):
            st.markdown("""
**ตัวเลือก 1: Ollama บน Server**
```bash
# บน server
curl -fsSL https://ollama.com/install.sh | sh
OLLAMA_HOST=0.0.0.0 ollama serve
ollama pull typhoon2-8b
```
URL: `http://<server-ip>:11434/v1`

**ตัวเลือก 2: vLLM**
```bash
pip install vllm
python -m vllm.entrypoints.openai.api_server \\
  --model scb10x/typhoon2-8b \\
  --host 0.0.0.0 --port 8000
```
URL: `http://<server-ip>:8000/v1`
""")


def get_openai_client_and_model(page: str = "default"):
    """
    คืนค่า (client, model_name) ตาม provider ที่เลือก
    page="chat" → ใช้ Vertex AI เมื่อเป็น Cloud
    page อื่น   → ใช้ Typhoon
    """
    from openai import OpenAI
    init_provider_state()
    ss = st.session_state
    provider = ss.get("ai_provider", PROVIDER_CLOUD)

    if provider == PROVIDER_CLOUD:
        if page == "chat":
            # ── Vertex AI via OpenAI-compatible endpoint ──────────────────────
            # Vertex AI มี OpenAI-compatible endpoint ที่ต้องใช้ Bearer token
            # จาก Service Account → generate access token
            try:
                import google.auth
                import google.auth.transport.requests
                from google.oauth2 import service_account

                sa_json   = ss.get("vertex_sa_json", "")
                project   = ss.get("vertex_project_id", "")
                location  = VERTEX_LOCATION

                if not sa_json or not project:
                    raise ValueError("ไม่พบ vertex_project_id หรือ vertex_sa_json ใน Secrets")

                sa_info = json.loads(sa_json)
                creds   = service_account.Credentials.from_service_account_info(
                    sa_info,
                    scopes=["https://www.googleapis.com/auth/cloud-platform"]
                )
                auth_req = google.auth.transport.requests.Request()
                creds.refresh(auth_req)
                token = creds.token

                base_url = (
                    f"https://{location}-aiplatform.googleapis.com/v1beta1/"
                    f"projects/{project}/locations/{location}/endpoints/openapi"
                )
                client = OpenAI(api_key=token, base_url=base_url)
                model  = f"google/{VERTEX_MODEL}"
                return client, model

            except Exception as e:
                # หน้า chat ใช้ Vertex เท่านั้น — ไม่ fallback ไป Typhoon
                raise ValueError(
                    f"Vertex AI ใช้งานไม่ได้: {e}\n\n"
                    "กรุณาตรวจสอบ Secrets:\n"
                    "• vertex_project_id = \"pa-gen-ai\"\n"
                    "• vertex_sa_json = '{...}' (JSON แบบ single line)"
                )

        else:
            # ── Typhoon (default cloud) ───────────────────────────────────────
            api_key = ss.get("api_key_global", "")
            if not api_key:
                raise ValueError("ไม่พบ api_key ใน Streamlit Secrets")
            return OpenAI(api_key=api_key, base_url=TYPHOON_BASE_URL), TYPHOON_MODEL

    elif provider == PROVIDER_LOCAL:
        url   = ss.get("local_url", "http://localhost:11434/v1")
        model = ss.get("local_model", "typhoon2-8b")
        return OpenAI(api_key="ollama", base_url=url), model

    elif provider == PROVIDER_ONPREMISE:
        url   = ss.get("onpremise_url", "")
        model = ss.get("onpremise_model", "")
        if not url:
            raise ValueError("กรุณาระบุ Server URL ใน sidebar")
        return OpenAI(api_key="onpremise", base_url=url), model

    raise ValueError(f"Unknown provider: {provider}")


def get_provider_display_name() -> str:
    """แสดงชื่อ provider ปัจจุบันสั้นๆ"""
    ss = st.session_state
    p = ss.get("ai_provider", PROVIDER_CLOUD)
    if p == PROVIDER_CLOUD:    return "☁️ Cloud AI"
    if p == PROVIDER_LOCAL:    return f"💻 Local ({ss.get('local_model','ollama')})"
    if p == PROVIDER_ONPREMISE: return f"🖥️ On-Premise ({ss.get('onpremise_model','')})"
    return "Unknown"
