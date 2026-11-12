
import streamlit as st

from llm import generate_response, get_available_models


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="AI Playground",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)


# --------------------------------------------------
# CUSTOM DARK THEME
# --------------------------------------------------

st.markdown(
    """
    <style>
    .stApp {
        background-color: #0b0f19;
        color: #f1f5f9;
    }

    [data-testid="stSidebar"] {
        background-color: #111827;
        border-right: 1px solid #263244;
    }

    .main-title {
        font-size: 36px;
        font-weight: 750;
        color: #f8fafc;
        margin-bottom: 4px;
    }

    .subtitle {
        color: #94a3b8;
        font-size: 15px;
        margin-bottom: 25px;
    }

    .section-title {
        color: #c4b5fd;
        font-size: 14px;
        font-weight: 650;
        margin-bottom: 10px;
    }

    .metric-card {
        background: #151e2e;
        border: 1px solid #29364a;
        border-radius: 12px;
        padding: 16px;
        text-align: center;
    }

    .metric-label {
        color: #94a3b8;
        font-size: 12px;
    }

    .metric-value {
        color: #e2e8f0;
        font-size: 23px;
        font-weight: 700;
    }

    .stButton > button {
        border-radius: 9px;
        border: 1px solid #394760;
        background-color: #182337;
        color: #e2e8f0;
    }

    .stButton > button:hover {
        border-color: #8b5cf6;
        color: #c4b5fd;
    }

    div[data-testid="stChatMessage"] {
        border: 1px solid #263244;
        border-radius: 12px;
        padding: 12px;
        margin-bottom: 12px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------

if "messages" not in st.session_state:
    st.session_state.messages = []

if "last_metrics" not in st.session_state:
    st.session_state.last_metrics = None

if "pending_prompt" not in st.session_state:
    st.session_state.pending_prompt = None


# --------------------------------------------------
# MODEL LOADING
# --------------------------------------------------

@st.cache_data(ttl=300)
def load_models():
    return get_available_models()


# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

with st.sidebar:

    st.markdown("## ⚡ AI Playground")

    st.caption("Cloud-powered LLM experimentation")

    st.divider()

    st.markdown("### Model Configuration")

    try:
        available_models = load_models()

        if not available_models:
            st.error("No models were returned by Groq.")
            st.stop()

        selected_model = st.selectbox(
            "Choose an LLM",
            options=available_models
        )

    except Exception as error:
        st.error(f"Unable to load models: {error}")
        st.info("Check your Groq API key and internet connection.")
        st.stop()

    temperature = st.slider(
        "Temperature",
        min_value=0.0,
        max_value=2.0,
        value=0.7,
        step=0.1,
        help="Controls the randomness of model responses."
    )

    max_tokens = st.slider(
        "Maximum completion tokens",
        min_value=128,
        max_value=4096,
        value=1024,
        step=128,
        help="Sets the maximum response length."
    )

    st.divider()

    st.markdown("### Session")

    st.write(f"Messages: {len(st.session_state.messages)}")

    if st.button("🗑️ Clear conversation", use_container_width=True):
        st.session_state.messages = []
        st.session_state.last_metrics = None
        st.session_state.pending_prompt = None
        st.rerun()

    st.divider()

    st.caption("Powered by Streamlit + Groq")


# --------------------------------------------------
# MAIN HEADER
# --------------------------------------------------

st.markdown(
    '<div class="main-title">⚡ AI Playground</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'Experiment with hosted language models, prompts and inference settings.'
    '</div>',
    unsafe_allow_html=True
)


# --------------------------------------------------
# PROMPT SUGGESTIONS
# --------------------------------------------------

if not st.session_state.messages:

    st.markdown(
        '<div class="section-title">START WITH A PROMPT</div>',
        unsafe_allow_html=True
    )

    col1, col2 = st.columns(2)

    with col1:
        if st.button(
            "🧠 Explain Transformer architecture",
            use_container_width=True
        ):
            st.session_state.pending_prompt = (
                "Explain Transformer architecture with a simple example."
            )
            st.rerun()

        if st.button(
            "🔍 Explain RAG",
            use_container_width=True
        ):
            st.session_state.pending_prompt = (
                "Explain Retrieval-Augmented Generation and how it works."
            )
            st.rerun()

    with col2:
        if st.button(
            "💻 Generate Python code",
            use_container_width=True
        ):
            st.session_state.pending_prompt = (
                "Write a Python program to find duplicate elements in a list."
            )
            st.rerun()

        if st.button(
            "🤖 Explain AI agents",
            use_container_width=True
        ):
            st.session_state.pending_prompt = (
                "Explain how AI agents work and give a practical example."
            )
            st.rerun()


# --------------------------------------------------
# DISPLAY CONVERSATION
# --------------------------------------------------

for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        st.markdown(message["content"])

        if message["role"] == "assistant" and message.get("metrics"):

            metrics = message["metrics"]

            st.caption(
                f"Model: {metrics['model']} | "
                f"Time: {metrics['response_time']} seconds | "
                f"Tokens: {metrics['total_tokens']}"
            )


# --------------------------------------------------
# CHAT INPUT
# --------------------------------------------------

user_prompt = st.chat_input(
    "Ask a question or experiment with a prompt..."
)

if st.session_state.pending_prompt:

    user_prompt = st.session_state.pending_prompt
    st.session_state.pending_prompt = None


# --------------------------------------------------
# GENERATE RESPONSE
# --------------------------------------------------

if user_prompt:

    # Save and display user message

    st.session_state.messages.append({
        "role": "user",
        "content": user_prompt
    })

    with st.chat_message("user"):
        st.markdown(user_prompt)

    # Build conversation context

    conversation = [
        {
            "role": "system",
            "content": (
                "You are a helpful AI assistant. "
                "Provide clear, accurate and structured answers."
            )
        }
    ]

    for message in st.session_state.messages:
        conversation.append({
            "role": message["role"],
            "content": message["content"]
        })

    # Generate assistant response

    with st.chat_message("assistant"):

        with st.spinner("Generating response..."):

            try:

                result = generate_response(
                    messages=conversation,
                    model=selected_model,
                    temperature=temperature,
                    max_tokens=max_tokens
                )

                answer = result["response"]

                if not answer:
                    answer = "The model returned an empty response."

                st.markdown(answer)

                st.caption(
                    f"Model: {result['model']} | "
                    f"Time: {result['response_time']} seconds | "
                    f"Tokens: {result['total_tokens']}"
                )

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer,
                    "metrics": result
                })

                st.session_state.last_metrics = result

            except Exception as error:

                error_message = str(error)

                st.error(error_message)

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": f"Request failed: {error_message}"
                })


# --------------------------------------------------
# PERFORMANCE METRICS
# --------------------------------------------------

if st.session_state.last_metrics:

    metrics = st.session_state.last_metrics

    st.divider()

    st.markdown("### 📊 Latest Response Metrics")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Response Time",
        f"{metrics['response_time']} s"
    )

    col2.metric(
        "Prompt Tokens",
        metrics["prompt_tokens"]
    )

    col3.metric(
        "Completion Tokens",
        metrics["completion_tokens"]
    )

    col4.metric(
        "Total Tokens",
        metrics["total_tokens"]
    )


# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.divider()

st.caption(
    "AI Playground | Demo Deployment | "
    "Streamlit + Groq Cloud Inference"
)
