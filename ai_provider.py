# ai_provider.py — Global AI Provider Helper
# ใช้ร่วมกันทุกหน้า เลือก provider จาก st.session_state["ai_provider"]

import streamlit as st
import os

# ─── Provider Constants ────────────────────────────────────────────────────────
PROVIDER_CLOUD     = "cloud"      # Claude (Anthropic) — ทุกหน้า
PROVIDER_LOCAL     = "local"      # Ollama
PROVIDER_ONPREMISE = "onpremise"  # On-Premise OpenAI-compatible

AI_PROVIDER_OPTIONS = {
    "☁️ Cloud AI ": PROVIDER_CLOUD,
    "💻 Local AI ": PROVIDER_LOCAL,
    "🖥️ On-Premise AI": PROVIDER_ONPREMISE,
}

# ─── Default model per provider ───────────────────────────────────────────────
# Cloud = Claude (Anthropic). เปลี่ยนมาจาก Typhoon (Model-1) และ Vertex/Gemini (Model-2)
ANTHROPIC_MODEL = "claude-sonnet-5"


def init_provider_state():
    """เรียกใน sidebar ทุกหน้าเพื่อ init session state"""
    ss = st.session_state
    ss.setdefault("ai_provider",      PROVIDER_CLOUD)
    ss.setdefault("local_url",        "http://localhost:11434/v1")
    ss.setdefault("local_model",      "typhoon2-8b")
    ss.setdefault("onpremise_url",    "http://your-server:11434/v1")
    ss.setdefault("onpremise_model",  "typhoon2-8b")

    # Anthropic (Claude) API key — ใช้ Cloud AI ทุกหน้า
    try:    ss["anthropic_api_key"] = st.secrets["anthropic_api_key"]
    except: ss.setdefault("anthropic_api_key", os.getenv("ANTHROPIC_API_KEY", ""))


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

    # ── Cloud AI (Claude) ──
    if current == PROVIDER_CLOUD:
        claude_ok = bool(ss.get("anthropic_api_key"))
        st.markdown(
            f"<small style='color:rgba(255,255,255,0.65);'>"
            f"{'✅' if claude_ok else '❌'} Claude ({ANTHROPIC_MODEL})<br>"
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


# ─── Claude (Anthropic) adapter ──────────────────────────────────────────────
# หน้าเดิมเรียก client.chat.completions.create(...) แบบ OpenAI SDK
# adapter นี้ห่อ anthropic SDK ตัวจริงไว้ ให้ interface เดิมใช้ได้โดยไม่ต้องแก้หน้า

class _Message:
    def __init__(self, content): self.content = content

class _Choice:
    def __init__(self, content): self.message = _Message(content)

class _ChatResponse:
    def __init__(self, content): self.choices = [_Choice(content)]

class _Delta:
    def __init__(self, content): self.content = content

class _StreamChoice:
    def __init__(self, content): self.delta = _Delta(content)

class _ChatChunk:
    def __init__(self, content): self.choices = [_StreamChoice(content)]


def _split_messages(messages):
    """แยก OpenAI-style messages → (system_text, conversation)
    Anthropic รับ system เป็น top-level และ messages เฉพาะ user/assistant"""
    system_parts, conv = [], []
    for m in messages:
        role    = m.get("role")
        content = m.get("content", "")
        if role == "system":
            if content:
                system_parts.append(content)
        else:  # user / assistant
            conv.append({"role": role, "content": content})
    return "\n\n".join(system_parts), conv


class _ClaudeChatClient:
    """ห่อ anthropic.Anthropic ให้เรียกแบบ client.chat.completions.create(...)"""

    def __init__(self, api_key, model):
        import anthropic
        self._client = anthropic.Anthropic(api_key=api_key)
        self._model  = model
        # ให้ client.chat.completions.create(...) วิ่งมาที่ self.create
        self.chat = self
        self.completions = self

    def create(self, model=None, messages=None, stream=False,
               max_tokens=1024, **kwargs):
        # kwargs เช่น temperature / top_p ถูกละทิ้ง — Claude Sonnet 5 ไม่รับ sampling params
        system, conv = _split_messages(messages or [])
        mdl = model or self._model
        req = {"model": mdl, "max_tokens": max_tokens, "messages": conv}
        if system:
            req["system"] = system

        if stream:
            return self._stream(req)

        resp = self._client.messages.create(**req)
        text = "".join(b.text for b in resp.content if b.type == "text")
        return _ChatResponse(text)

    def _stream(self, req):
        with self._client.messages.stream(**req) as stream:
            for text in stream.text_stream:
                yield _ChatChunk(text)


def get_openai_client_and_model(page: str = "default"):
    """
    คืนค่า (client, model_name) ตาม provider ที่เลือก
    Cloud → Claude (Anthropic) ทุกหน้า
    Local / On-Premise → OpenAI-compatible (Ollama / vLLM)
    """
    init_provider_state()
    ss = st.session_state
    provider = ss.get("ai_provider", PROVIDER_CLOUD)

    if provider == PROVIDER_CLOUD:
        # ── Claude (Anthropic) ────────────────────────────────────────────────
        api_key = ss.get("anthropic_api_key", "") or os.getenv("ANTHROPIC_API_KEY", "")
        if not api_key:
            raise ValueError(
                "ไม่พบ anthropic_api_key ใน Streamlit Secrets\n\n"
                "กรุณาเพิ่มใน Secrets:\n"
                '• anthropic_api_key = "sk-ant-..."'
            )
        return _ClaudeChatClient(api_key, ANTHROPIC_MODEL), ANTHROPIC_MODEL

    elif provider == PROVIDER_LOCAL:
        from openai import OpenAI
        url   = ss.get("local_url", "http://localhost:11434/v1")
        model = ss.get("local_model", "typhoon2-8b")
        return OpenAI(api_key="ollama", base_url=url), model

    elif provider == PROVIDER_ONPREMISE:
        from openai import OpenAI
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
    if p == PROVIDER_CLOUD:    return "☁️ Cloud AI (Claude)"
    if p == PROVIDER_LOCAL:    return f"💻 Local ({ss.get('local_model','ollama')})"
    if p == PROVIDER_ONPREMISE: return f"🖥️ On-Premise ({ss.get('onpremise_model','')})"
    return "Unknown"
