
import os
import inspect
import traceback
from datetime import datetime

import streamlit as st
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from retriever import load_vector_store
from rag_chain import generate_answer

load_dotenv()

st.set_page_config(
    page_title="PeoplePilot | AI HR Assistant",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded"
)

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

LANGUAGES = [
    "English", "Hindi", "Marathi", "Spanish", "French",
    "German", "Japanese", "Tamil", "Telugu", "Bengali"
]

THEMES = {
    "Midnight": {
        "bg": "#080D1A",
        "panel": "#111A2E",
        "card": "#16213A",
        "text": "#F4F7FF",
        "muted": "#9AA9C4",
        "accent": "#9B8CFF",
        "border": "#26334F"
    },
    "Light": {
        "bg": "#F4F7FC",
        "panel": "#FFFFFF",
        "card": "#EDF2FA",
        "text": "#17223B",
        "muted": "#68758C",
        "accent": "#635BDB",
        "border": "#DCE3EF"
    },
    "Ocean": {
        "bg": "#071A22",
        "panel": "#0D2934",
        "card": "#123743",
        "text": "#F0FCFF",
        "muted": "#9ABAC4",
        "accent": "#35C6C8",
        "border": "#20505B"
    },
    "Lavender": {
        "bg": "#171329",
        "panel": "#241E3B",
        "card": "#302849",
        "text": "#FBF7FF",
        "muted": "#C0B4D8",
        "accent": "#D5A8FF",
        "border": "#45375E"
    }
}

SUGGESTIONS = [
    "How do I request annual leave?",
    "What is the sick leave policy?",
    "What should I do if I arrive late?",
    "How does the performance review process work?"
]


def initialize_state():
    defaults = {
        "messages": [],
        "theme": "Midnight",
        "language": "English",
        "resources": None,
        "diagnostic_error": None,
        "questions_asked": 0
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def apply_theme(theme_name):
    colors = THEMES[theme_name]

    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@400;500;600;700;800&display=swap');

        :root {{
            --bg: {colors["bg"]};
            --panel: {colors["panel"]};
            --card: {colors["card"]};
            --text: {colors["text"]};
            --muted: {colors["muted"]};
            --accent: {colors["accent"]};
            --border: {colors["border"]};
        }}

        .stApp {{
            background: var(--bg);
            color: var(--text);
            font-family: 'DM Sans', sans-serif;
        }}

        [data-testid="stHeader"] {{
            background: transparent;
        }}

        [data-testid="stMainBlockContainer"] {{
            max-width: 1450px;
            padding-top: 1.5rem;
            padding-bottom: 2rem;
        }}

        [data-testid="stSidebar"] {{
            background: var(--panel);
            border-right: 1px solid var(--border);
        }}

        [data-testid="stSidebar"] * {{
            color: var(--text);
        }}

        h1, h2, h3 {{
            font-family: 'Manrope', sans-serif !important;
            color: var(--text) !important;
            letter-spacing: -0.5px;
        }}

        p, label, .stMarkdown {{
            color: var(--text);
        }}

        .brand {{
            font-family: 'Manrope', sans-serif;
            font-size: 27px;
            font-weight: 800;
            letter-spacing: -1.2px;
            color: var(--text);
        }}

        .brand span {{
            color: var(--accent);
        }}

        .eyebrow {{
            color: var(--accent);
            font-size: 11px;
            font-weight: 800;
            letter-spacing: 2px;
            text-transform: uppercase;
        }}

        .hero {{
            background: linear-gradient(135deg, var(--panel), var(--card));
            border: 1px solid var(--border);
            border-radius: 24px;
            padding: 32px;
            margin: 8px 0 24px 0;
        }}

        .hero h1 {{
            font-size: clamp(30px, 4vw, 44px);
            margin: 13px 0 10px 0;
            line-height: 1.15;
        }}

        .hero p {{
            color: var(--muted);
            font-size: 15px;
            line-height: 1.8;
            max-width: 760px;
        }}

        .status-pill {{
            display: inline-block;
            padding: 7px 12px;
            border-radius: 30px;
            background: var(--panel);
            border: 1px solid var(--border);
            color: var(--muted);
            font-size: 12px;
        }}

        .status-dot {{
            display: inline-block;
            width: 7px;
            height: 7px;
            margin-right: 7px;
            background: #42DCA2;
            border-radius: 50%;
        }}

        [data-testid="stChatMessage"] {{
            background: var(--panel);
            border: 1px solid var(--border);
            border-radius: 18px;
            padding: 16px;
            margin-bottom: 12px;
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
        }}

        [data-testid="stChatMessage"] p {{
            line-height: 1.75;
        }}

        .stButton > button {{
            border: 1px solid var(--border);
            border-radius: 12px;
            background: var(--panel);
            color: var(--text);
            min-height: 44px;
            font-weight: 600;
            white-space: normal;
            transition: all 0.2s ease;
        }}

        .stButton > button:hover {{
            border-color: var(--accent);
            color: var(--accent);
            transform: translateY(-1px);
        }}

        [data-testid="stChatInput"] {{
            border-color: var(--border);
        }}

        [data-testid="stChatInput"] textarea {{
            font-size: 15px;
            line-height: 1.6;
        }}

        [data-testid="stMetric"] {{
            background: var(--panel);
            border: 1px solid var(--border);
            padding: 16px;
            border-radius: 16px;
        }}

        [data-testid="stMetricLabel"] {{
            color: var(--muted);
        }}

        [data-testid="stMetricValue"] {{
            font-family: 'Manrope', sans-serif;
            font-weight: 800;
        }}

        [data-testid="stExpander"] {{
            background: var(--panel);
            border: 1px solid var(--border);
            border-radius: 14px;
        }}

        .muted {{
            color: var(--muted);
            font-size: 12px;
        }}

        hr {{
            border-color: var(--border);
        }}

        #MainMenu, footer {{
            visibility: hidden;
        }}

        @media (max-width: 768px) {{
            [data-testid="stMainBlockContainer"] {{
                padding-left: 1rem;
                padding-right: 1rem;
            }}

            .hero {{
                padding: 22px;
                border-radius: 18px;
            }}
        }}
        </style>
        """,
        unsafe_allow_html=True
    )


@st.cache_resource(show_spinner=False)
def get_resources():
    index, chunks = load_vector_store()
    embedding_model = SentenceTransformer(MODEL_NAME)
    return index, chunks, embedding_model


def get_answer(question):
    index, chunks, embedding_model = get_resources()

    parameters = inspect.signature(generate_answer).parameters
    accepts_language = (
        "response_language" in parameters
        or any(
            parameter.kind == inspect.Parameter.VAR_KEYWORD
            for parameter in parameters.values()
        )
    )

    if accepts_language:
        return generate_answer(
            question,
            index,
            chunks,
            embedding_model,
            response_language=st.session_state.language
        )

    return generate_answer(
        question,
        index,
        chunks,
        embedding_model
    )


def ask_question(question):
    question = question.strip()

    if not question:
        return

    if not os.getenv("GEMINI_API_KEY"):
        st.session_state.diagnostic_error = (
            "GEMINI_API_KEY is missing. Check your .env file."
        )
        return

    st.session_state.messages.append({
        "role": "user",
        "content": question,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

    st.session_state.diagnostic_error = None

    try:
        with st.status(
            "Preparing your answer...",
            expanded=True
        ) as status:
            st.write("Loading the policy knowledge base...")
            result = get_answer(question)

            st.write("Preparing your answer and source references...")

            if not isinstance(result, dict):
                raise TypeError(
                    "generate_answer() must return a dictionary "
                    "containing 'answer' and 'sources'."
                )

            answer = result.get("answer", "")
            sources = result.get("sources", [])

            if not isinstance(answer, str) or not answer.strip():
                answer = (
                    "I couldn't generate a reliable answer from "
                    "the available HR policy information."
                )

            if not isinstance(sources, list):
                sources = []

            st.session_state.messages.append({
                "role": "assistant",
                "content": answer.strip(),
                "sources": sources,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })

            st.session_state.questions_asked += 1

            status.update(
                label="Answer generated successfully",
                state="complete",
                expanded=False
            )

    except Exception as error:
        details = traceback.format_exc()

        st.session_state.diagnostic_error = (
            f"{type(error).__name__}: {error}\n\n{details}"
        )

        st.session_state.messages.append({
            "role": "assistant",
            "content": (
                "I couldn't complete that request. "
                "Please review the technical diagnostic details below."
            ),
            "sources": [],
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })


def render_sources(sources):
    if not sources:
        st.caption("No supporting source passages were returned.")
        return

    with st.expander(f"📚 Supporting sources ({len(sources)})"):
        for position, source in enumerate(sources, start=1):
            if not isinstance(source, dict):
                continue

            page = source.get("page_number", "Unknown")
            score = source.get("score")

            st.markdown(f"**Source {position} · Page {page}**")

            if isinstance(score, (int, float)):
                st.caption(f"Similarity score: {score:.3f}")

            text = source.get("text", "")

            if text:
                st.write(text)

            if position < len(sources):
                st.divider()


def render_sidebar():
    with st.sidebar:
        st.markdown(
            '<div class="brand">People<span>Pilot</span> ✦</div>',
            unsafe_allow_html=True
        )

        st.caption("INTELLIGENT HR POLICY ASSISTANT")
        st.divider()

        st.markdown("### Workspace")

        st.markdown(
            '<div class="status-pill">'
            '<span class="status-dot"></span>'
            'Ready for your questions'
            '</div>',
            unsafe_allow_html=True
        )

        st.markdown("### Appearance")

        theme_names = list(THEMES.keys())
        selected_theme = st.selectbox(
            "Choose your theme",
            theme_names,
            index=theme_names.index(st.session_state.theme)
        )

        if selected_theme != st.session_state.theme:
            st.session_state.theme = selected_theme
            st.rerun()

        st.markdown("### Response language")

        st.session_state.language = st.selectbox(
            "Answer in",
            LANGUAGES,
            index=LANGUAGES.index(st.session_state.language)
        )

        st.divider()
        st.markdown("### Knowledge base")
        st.markdown("**HR Policy Handbook**")
        st.caption("PDF · Semantic search · FAISS · Gemini")

        if st.button("＋ New conversation", use_container_width=True):
            st.session_state.messages = []
            st.session_state.diagnostic_error = None
            st.rerun()

        if st.session_state.messages:
            export_text = "\n\n".join(
                f'{message["role"].upper()}\n{message["content"]}'
                for message in st.session_state.messages
            )

            st.download_button(
                "↓ Export conversation",
                data=export_text,
                file_name="peoplepilot_conversation.txt",
                mime="text/plain",
                use_container_width=True
            )

        st.divider()
        st.caption("AI engineering portfolio project")
        st.caption("Demo handbook only. Verify important policies with HR.")


def render_header():
    st.markdown(
        """
        <div class="hero">
            <div class="eyebrow">✦ YOUR WORKPLACE KNOWLEDGE COMPANION</div>
            <h1>HR answers, made simple.</h1>
            <p>
                Ask questions in natural language and get clear answers
                grounded in your HR handbook. Explore the supporting
                passages so you can verify the information.
            </p>
            <div class="status-pill">
                <span class="status-dot"></span>
                AI assistant workspace
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    first, second, third = st.columns(3)

    with first:
        st.metric("Architecture", "RAG")

    with second:
        st.metric("Languages", len(LANGUAGES))

    with third:
        st.metric("Questions asked", st.session_state.questions_asked)


def render_suggestions():
    st.markdown("### What can I help you with?")
    st.caption("Choose a suggested question or type your own below.")

    first_column, second_column = st.columns(2)

    for position, suggestion in enumerate(SUGGESTIONS):
        target_column = first_column if position % 2 == 0 else second_column

        with target_column:
            if st.button(
                suggestion,
                key=f"suggestion_{position}",
                use_container_width=True
            ):
                st.session_state.pending_question = suggestion
                st.rerun()


def render_conversation():
    st.markdown("### Conversation")

    if not st.session_state.messages:
        st.info(
            "Your conversation starts here. Try asking about annual leave, "
            "attendance, workplace policies, or performance reviews."
        )

    for position, message in enumerate(st.session_state.messages):
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

            if message["role"] == "assistant":
                render_sources(message.get("sources", []))

    if st.session_state.diagnostic_error:
        with st.expander("Technical diagnostic details", expanded=True):
            st.code(st.session_state.diagnostic_error)


def main():
    initialize_state()
    apply_theme(st.session_state.theme)
    render_sidebar()
    render_header()
    render_suggestions()

    st.divider()
    render_conversation()

    question = st.chat_input("Ask your HR policy question...")

    if question:
        ask_question(question)
        st.rerun()

    if "pending_question" in st.session_state:
        pending_question = st.session_state.pop("pending_question")
        ask_question(pending_question)
        st.rerun()

    st.divider()

    st.markdown(
        '<p class="muted">'
        'PeoplePilot may make mistakes. Review the cited policy passages '
        'and contact HR when an official decision is required.'
        '</p>',
        unsafe_allow_html=True
    )


main()
