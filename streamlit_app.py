
import streamlit as st

from backend.config import (
    MAX_QUESTION_LENGTH,
    TOP_K,
    MIN_SIMILARITY,
)
from backend.services.retriever import Retriever
from backend.services.llm_service import create_answer, FALLBACK


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="DIEMS | Admission Assistant",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)


# --------------------------------------------------
# CUSTOM CSS
# --------------------------------------------------

st.markdown("""
<style>

/* Main background */
.stApp {
    background-color: #f4f6fb;
}

/* Remove default top spacing */
.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
    max-width: 1100px;
}

/* Main heading */
.main-heading {
    color: #142b50;
    font-size: 32px;
    font-weight: 750;
    margin-bottom: 5px;
}

.sub-heading {
    color: #65738a;
    font-size: 15px;
}

/* Hero section */
.hero {
    background: linear-gradient(120deg, #142b50, #244b7a);
    padding: 30px;
    border-radius: 18px;
    color: white;
    margin-bottom: 25px;
}

.hero h2 {
    color: white;
    font-size: 27px;
    margin-bottom: 8px;
}

.hero p {
    color: #e4ebf5;
    font-size: 15px;
    margin-bottom: 0;
}

/* Section headings */
.section-heading {
    color: #142b50;
    font-size: 19px;
    font-weight: 700;
    margin-top: 20px;
    margin-bottom: 12px;
}

/* Suggested questions */
div.stButton > button {
    border-radius: 10px;
    border: 1px solid #d8dfeb;
    background-color: white;
    color: #142b50;
    font-weight: 600;
    min-height: 48px;
    transition: 0.2s;
}

div.stButton > button:hover {
    border-color: #d5a33b;
    color: #142b50;
    background-color: #fffaf0;
}

/* Chat input */
.stChatInput textarea {
    border-radius: 12px;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background-color: #142b50;
}

section[data-testid="stSidebar"] * {
    color: white;
}

section[data-testid="stSidebar"] button {
    color: #142b50;
}

/* Chat messages */
div[data-testid="stChatMessage"] {
    background-color: #ffffff !important;
    border: 1px solid #e0e5ee;
    border-radius: 14px;
    padding: 14px;
    margin-bottom: 12px;
}

/* User and assistant message text */
div[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"],
div[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] p,
div[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] li {
    color: #182b49 !important;
}

/* Chat message headings */
div[data-testid="stChatMessage"] h1,
div[data-testid="stChatMessage"] h2,
div[data-testid="stChatMessage"] h3 {
    color: #142b50 !important;
}

/* Chat input text */
.stChatInput textarea {
    color: #182b49 !important;
    background-color: #ffffff !important;
}

/* Chat input placeholder */
.stChatInput textarea::placeholder {
    color: #778399 !important;
}

/* Small footer */
.footer {
    text-align: center;
    color: #8792a4;
    font-size: 12px;
    padding: 20px 0;
}

/* Professional college header */
.brand-header {
    display: flex;
    align-items: center;
    gap: 16px;
    background: white;
    padding: 18px 22px;
    border-radius: 15px;
    border: 1px solid #e1e6ef;
    margin-bottom: 22px;
}

.brand-logo {
    background: #142b50;
    color: #f4c65e;
    width: 58px;
    height: 58px;
    min-width: 58px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 23px;
    font-weight: 800;
}

.brand-name {
    color: #142b50;
    font-size: 21px;
    font-weight: 750;
}

.brand-subtitle {
    color: #69778c;
    font-size: 13px;
}

.online-status {
    margin-left: auto;
    color: #16834a;
    background: #e8f7ee;
    padding: 7px 12px;
    border-radius: 20px;
    font-size: 12px;
    white-space: nowrap;
}

</style>
""", unsafe_allow_html=True)


# --------------------------------------------------
# LOAD RETRIEVER
# --------------------------------------------------

@st.cache_resource(show_spinner="Loading DIEMS information...")
def get_retriever():
    engine = Retriever()

    if not engine.load():
        engine.build()

    return engine


# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------

if "messages" not in st.session_state:
    st.session_state.messages = []


# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

with st.sidebar:

    st.markdown(
        "<h2 style='text-align:center;'>🎓 DIEMS</h2>",
        unsafe_allow_html=True
    )

    st.markdown(
        "<p style='text-align:center;'>Admission Assistant</p>",
        unsafe_allow_html=True
    )

    st.divider()

    st.markdown("### About the Assistant")

    st.write(
        "Your digital admission enquiry assistant. "
        "Ask questions about DIEMS programmes, admissions, "
        "documents, fees and campus facilities."
    )

    st.divider()

    st.markdown("### What you can ask")

    st.markdown("""
    - College information
    - B.Tech and M.Tech programmes
    - Admission documents
    - Fee-related enquiries
    - Hostel facilities
    - Contact information
    """)

    st.divider()

    if st.button("🗑️ Clear Conversation", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.caption("DIEMS Admission Support Prototype")


# --------------------------------------------------
# MAIN HEADER
# --------------------------------------------------

st.markdown("""
<div class="brand-header">
    <div class="brand-logo">DI</div>
    <div>
        <div class="brand-name">DIEMS</div>
        <div class="brand-subtitle">
            College Admission Enquiry Assistant
        </div>
    </div>
    <div class="online-status">
        ● Assistant Ready
    </div>
</div>
""", unsafe_allow_html=True)


# --------------------------------------------------
# HERO SECTION
# --------------------------------------------------

if not st.session_state.messages:

    st.markdown("""
    <div class="hero">
        <h2>Welcome to DIEMS! 👋</h2>
        <p>
            Have questions about admission, programmes or campus facilities?
            I'm here to help you find the information you need.
        </p>
    </div>
    """, unsafe_allow_html=True)


# --------------------------------------------------
# LOAD KNOWLEDGE BASE
# --------------------------------------------------

try:
    retriever = get_retriever()

except Exception as exc:
    st.error("Unable to load the DIEMS knowledge base.")
    st.write(str(exc))
    st.stop()


# --------------------------------------------------
# SUGGESTED QUESTIONS
# --------------------------------------------------

# --------------------------------------------------
# QUICK ACCESS CATEGORIES
# --------------------------------------------------

if not st.session_state.messages:

    st.markdown(
        "<div class='section-heading'>Explore DIEMS</div>",
        unsafe_allow_html=True
    )

    categories = [
        ("🎓 Admissions", "What is the B.Tech admission process at DIEMS?"),
        ("📚 Courses", "Which programmes are offered at DIEMS?"),
        ("💰 Fees", "What fee information is available at DIEMS?"),
        ("📄 Documents", "What documents are required for B.Tech admission?"),
        ("🏠 Hostel", "What hostel facilities are available at DIEMS?"),
        ("📞 Contact", "How can I contact the DIEMS admission office?")
    ]

    selected_question = None

    for row in range(3):
        cols = st.columns(2)

        for col_index in range(2):
            index = row * 2 + col_index
            label, prompt = categories[index]

            with cols[col_index]:
                if st.button(
                    label,
                    key=f"category_{index}",
                    use_container_width=True
                ):
                    selected_question = prompt

else:
    selected_question = None

# --------------------------------------------------
# DISPLAY CHAT HISTORY
# --------------------------------------------------

for message in st.session_state.messages:

    avatar = "🎓" if message["role"] == "assistant" else "👤"

    with st.chat_message(message["role"], avatar=avatar):

        st.markdown(message["content"])

        if message.get("sources"):

            with st.expander("📚 View information sources"):

                for source in message["sources"]:
                    st.write("• " + source)


# --------------------------------------------------
# CHAT INPUT
# --------------------------------------------------

question = st.chat_input(
    "Ask anything about DIEMS admissions..."
)

if not question:
    question = selected_question


# --------------------------------------------------
# PROCESS QUESTION
# --------------------------------------------------

if question:

    question = question.strip()

    if not question:
        st.warning("Please enter a question.")

    elif len(question) > MAX_QUESTION_LENGTH:

        st.warning(
            f"Please keep your question under "
            f"{MAX_QUESTION_LENGTH} characters."
        )

    else:

        st.session_state.messages.append({
            "role": "user",
            "content": question
        })

        with st.chat_message("user", avatar="👤"):
            st.markdown(question)

        with st.chat_message("assistant", avatar="🎓"):

            with st.spinner("Finding the best answer..."):

                try:

                    matches = retriever.search(question, TOP_K)

                    reliable = [
                        item for item in matches
                        if item["score"] >= MIN_SIMILARITY
                    ]

                    if reliable:

                        answer, mode = create_answer(
                            question,
                            reliable
                        )

                    else:

                        answer = FALLBACK
                        mode = "fallback"

                    st.markdown(answer)

                    source_labels = []

                    for item in reliable:

                        metadata = item.get("metadata", {})

                        label = (
                            f"{metadata.get('source', 'DIEMS Records')} "
                            f"· {metadata.get('category', 'General')}"
                        )

                        if metadata.get("page"):
                            label += f" · Page {metadata['page']}"

                        if label not in source_labels:
                            source_labels.append(label)

                    if source_labels:

                        with st.expander("📚 View information sources"):

                            for source in source_labels:
                                st.write("• " + source)

                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": answer,
                        "sources": source_labels
                    })

                except Exception as exc:

                    st.error(
                        f"Something went wrong while processing "
                        f"your question: {exc}"
                    )

# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.markdown("""
<div class="footer">
    DIEMS Admission Assistant | College Enquiry Support
    <br>
    Please verify important admission information through official DIEMS notices.
</div>
""", unsafe_allow_html=True)
