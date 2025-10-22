import os
import subprocess
import streamlit as st
from groq import Groq

# --- CONFIG ---
MODEL_NAME = "llama-3.3-70b-versatile"
TEMPERATURE = 0.3
MAX_TOKENS = 300

# --- APP SETUP ---
st.set_page_config(
    page_title="AI Git Commit Assistant", page_icon="🤖", layout="centered"
)

st.title("🤖 AI Git Commit Message Generator")
st.write(
    "Automatically generate clear, conventional commit messages using **Groq LLaMA 3.3**."
)

# --- SESSION STATE ---
if "commit_message" not in st.session_state:
    st.session_state.commit_message = ""
if "diff" not in st.session_state:
    st.session_state.diff = ""

# --- INPUT ---
repo_path = st.text_input(
    "📁 Repository Path",
    value="",  # Default to the current directory
    help="Defaults to the current directory. Change if you want to analyze another local repository.",
)
generate_btn = st.button("🔍 Detect Changes & Generate Commit Message")


# --- HELPER FUNCTIONS ---
def get_git_diff(repo_path: str) -> str:
    """Fetch git diff (staged or unstaged)"""
    if not os.path.exists(repo_path):
        st.error(f"❌ Path not found: {repo_path}")
        return ""

    try:
        subprocess.check_output(
            ["git", "rev-parse", "--is-inside-work-tree"], cwd=repo_path, text=True
        )
    except subprocess.CalledProcessError:
        st.error(f"❌ '{repo_path}' is not a Git repository.")
        return ""

    try:
        diff = subprocess.check_output(
            ["git", "diff", "--cached"], cwd=repo_path, text=True
        )
        if not diff.strip():
            diff = subprocess.check_output(["git", "diff"], cwd=repo_path, text=True)
        return diff.strip()
    except subprocess.CalledProcessError:
        st.error("❌ Failed to get git diff.")
        return ""


def generate_commit_message(diff: str, api_key: str) -> str:
    """Generate commit message using Groq API."""
    client = Groq(api_key=api_key)
    prompt = f"""
You are an expert software engineer and technical writer.
Your task is to generate a clear, concise, and meaningful Git commit message based on the provided `git diff`.

Follow these strict rules:
1. Read the diff carefully and identify what was changed, added, removed, or refactored.
2. Summarize the purpose of the change, not just what was modified.
3. Use present tense (e.g., add, fix, update, remove) in the message.
4. Keep the first line (the commit title) under 72 characters.
5. If there are multiple logical changes, summarize them in short, separate sentences in the commit body (one per line).
6. Do NOT include bullet points, asterisks, markdown formatting, or code blocks.
7. Do NOT include backticks or quotation marks around filenames.
8. If you detect bug fixes, improvements, or new features, label them appropriately in the title.
9. The message must follow this format exactly:

<type>: <short summary>

<optional longer description or multiple lines, one per logical change>

Where <type> can be one of:
feat: for a new feature
fix: for a bug fix
refactor: for code restructuring
docs: for documentation updates
style: for code style or formatting changes
test: for adding or updating tests
chore: for build, dependency, or config updates

Git diff:
{diff}

{diff}
"""
    completion = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": prompt}],
        temperature=TEMPERATURE,
        max_completion_tokens=MAX_TOKENS,
        top_p=1,
    )
    return completion.choices[0].message.content.strip()


def commit_changes(repo_path: str, message: str):
    """Stage and commit all changes safely."""
    try:
        subprocess.run(["git", "add", "."], cwd=repo_path, check=True)
        subprocess.run(["git", "commit", "-m", message], cwd=repo_path, check=True)
        return True, "✅ Commit created successfully!"
    except subprocess.CalledProcessError as e:
        return False, f"❌ Commit failed: {e}"


# --- MAIN LOGIC ---
if generate_btn:
    api_key = os.getenv("MY_API_KEY")
    if not api_key:
        st.error("❌ Environment variable `MY_API_KEY` not found.")
    else:
        with st.spinner("🧠 Analyzing changes..."):
            diff = get_git_diff(repo_path)
            if not diff:
                st.warning("No changes detected in this repository.")
            else:
                st.session_state.diff = diff
                commit_message = generate_commit_message(diff, api_key)
                st.session_state.commit_message = commit_message
                st.success("✅ Commit message generated!")


# --- DISPLAY GENERATED MESSAGE ---
if st.session_state.commit_message:
    st.text_area(
        "📝 Suggested Commit Message", st.session_state.commit_message, height=150
    )

    col1, col2 = st.columns(2)
    with col1:
        if st.button("💾 Commit Changes"):
            success, msg = commit_changes(repo_path, st.session_state.commit_message)
            if success:
                st.success(msg)
            else:
                st.error(msg)

    with col2:
        if st.button("🔁 Refresh Diff"):
            st.session_state.diff = get_git_diff(repo_path)
            if st.session_state.diff:
                st.info("🔄 Diff refreshed successfully.")
            else:
                st.warning("No changes detected after refresh.")


st.markdown(
    """
    <hr style="margin-top: 2em; margin-bottom: 1em;">
    <div style="text-align: center; font-size: 15px; color: #6c757d;">
        💡 Developed with ❤️ by 
        <a href="https://github.com/AliGohar2151" target="_blank" style="color: #4a90e2; text-decoration: none; font-weight: bold;">
            Ali Gohar
        </a>
    </div>
    """,
    unsafe_allow_html=True,
)
