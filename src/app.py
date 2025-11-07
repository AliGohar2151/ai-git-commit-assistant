import os
import subprocess
import streamlit as st
from typing import Tuple
from groq import Groq

# --- CONFIG ---
MODEL_NAME = "llama-3.3-70b-versatile"
TEMPERATURE = 0.5
MAX_TOKENS = 300

# --- APP SETUP ---
st.set_page_config(
    page_title="AI Git Commit Assistant",
    page_icon="🤖",
    layout="centered",
)

st.title("🤖 AI Git Commit Message Generator")
st.write(
    "Automatically generate **clear, conventional Git commit messages** using **Groq LLaMA 3.3**."
)

# --- SESSION STATE ---
if "commit_message" not in st.session_state:
    st.session_state.commit_message = ""

if "diff" not in st.session_state:
    st.session_state.diff = ""

if "repo_path" not in st.session_state:
    st.session_state.repo_path = ""

if "api_key" not in st.session_state:
    st.session_state.api_key = os.getenv("MY_API_KEY", "")


# --- INPUT ---
with st.expander("⚙️ Configuration", expanded=True):
    st.session_state.repo_path = st.text_input(
        "📁 Repository Path",
        value=st.session_state.repo_path,
        placeholder="Enter your local Git repository path...",
        help="Enter the full path to your local Git repository.",
    )

    st.session_state.api_key = st.text_input(
        "🔑 Groq API Key",
        type="password",
        value=st.session_state.api_key,
        help="Get your API key from https://console.groq.com/keys",
    )

generate_btn = st.button("🔍 Detect Changes & Generate Commit Message", type="primary")


# --- HELPER FUNCTIONS ---
def get_git_diff(repo_path: str) -> Tuple[str, str]:
    """Fetch git diff (staged or unstaged). Returns (diff, error_message)."""
    if not os.path.exists(repo_path):
        return "", f"Path not found: {repo_path}"

    try:
        subprocess.check_output(
            ["git", "rev-parse", "--is-inside-work-tree"],
            cwd=repo_path,
            stderr=subprocess.PIPE,
        )
    except subprocess.CalledProcessError:
        return "", f"'{repo_path}' is not a valid Git repository."

    try:
        diff = subprocess.check_output(
            ["git", "diff", "--cached"],
            cwd=repo_path,
            text=True,
            encoding="utf-8",
            errors="replace",
        ).strip()

        if not diff:
            diff = subprocess.check_output(
                ["git", "diff"],
                cwd=repo_path,
                text=True,
                encoding="utf-8",
                errors="replace",
            ).strip()

        return diff, ""
    except subprocess.CalledProcessError as e:
        return "", f"Failed to get git diff: {e.stderr or str(e)}"


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
"""
    completion = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": prompt}],
        temperature=TEMPERATURE,
        max_completion_tokens=MAX_TOKENS,
        top_p=1,
    )
    return completion.choices[0].message.content.strip()


def commit_changes(repo_path: str, message: str) -> Tuple[bool, str]:
    """Stage and commit all changes safely."""
    try:
        subprocess.run(["git", "add", "."], cwd=repo_path, check=True, capture_output=True)
        subprocess.run(
            ["git", "commit", "--file=-"],
            input=message,
            text=True,
            cwd=repo_path,
            check=True,
            capture_output=True,
        )
        return True, "✅ Commit created successfully!"
    except subprocess.CalledProcessError as e:
        return False, f"❌ Commit failed: {e.stderr or str(e)}"


# --- MAIN LOGIC ---
if generate_btn:
    if not st.session_state.api_key:
        st.error("❌ Please enter your Groq API key.")
    elif not st.session_state.repo_path:
        st.error("❌ Please enter your repository path.")
    else:
        with st.spinner("🧠 Analyzing changes..."):
            diff, error = get_git_diff(st.session_state.repo_path)
            if error:
                st.error(f"❌ {error}")
            elif not diff:
                st.warning("✅ No changes detected in this repository.")
            else:
                st.session_state.diff = diff
                try:
                    commit_message = generate_commit_message(diff, st.session_state.api_key)
                    st.session_state.commit_message = commit_message
                    st.success("✅ Commit message generated!")
                except Exception as e:
                    st.error(f"❌ Failed to generate message: {e}")


# --- DISPLAY GENERATED MESSAGE ---
if st.session_state.commit_message:
    st.text_area(
        "📝 Suggested Commit Message",
        st.session_state.commit_message,
        height=160,
    )

    col1, col2, = st.columns([1, 2])

    with col1:
        if st.button("💾 Commit Changes"):
            success, msg = commit_changes(
                st.session_state.repo_path, st.session_state.commit_message
            )
            if success:
                st.success(msg)
                st.session_state.commit_message = ""
                st.session_state.diff = ""
                st.rerun()
            else:
                st.error(msg)

    

    with col2:
        if st.button("🔄 Refresh Diff & Regenerate"):
            if not st.session_state.repo_path:
                st.error("❌ Please enter your repository path first.")
            elif not st.session_state.api_key:
                st.error("❌ Please enter your Groq API key.")
            else:
                with st.spinner("🔁 Refreshing and regenerating..."):
                    diff, error = get_git_diff(st.session_state.repo_path)
                    if error:
                        st.error(f"❌ {error}")
                    elif not diff:
                        st.warning("✅ No changes detected in this repository.")
                    else:
                        st.session_state.diff = diff
                        try:
                            commit_message = generate_commit_message(diff, st.session_state.api_key)
                            st.session_state.commit_message = commit_message
                            st.success("✅ Commit message regenerated!")
                        except Exception as e:
                            st.error(f"❌ Failed to regenerate: {e}")






# --- FOOTER ---
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
