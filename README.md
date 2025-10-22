# 🤖 AI Git Commit Assistant

Automatically generate clear, conventional commit messages using **Groq LLaMA 3.3**. This Streamlit application helps developers craft meaningful Git commit messages based on their staged or unstaged changes, adhering to conventional commit guidelines.

## ✨ Features

- **Detect Changes**: Automatically detects changes in a specified Git repository.
- **AI-Powered Commit Message Generation**: Utilizes the Groq API with the LLaMA 3.3 model to generate concise and descriptive commit messages.
- **Conventional Commit Format**: Generates messages following a structured format (`<type>: <short summary>`) with an optional longer description.
- **Direct Commit**: Allows users to commit changes directly from the Streamlit interface.
- **User-Friendly Interface**: Built with Streamlit for an interactive and easy-to-use experience.

## 🚀 Technologies Used

- **Python**: The core programming language.
- **Streamlit**: For building the interactive web application.
- **Groq API**: Powers the AI commit message generation using LLaMA 3.3.
- **Git**: For interacting with local repositories.

## 🛠️ Setup and Installation

Follow these steps to get the project up and running on your local machine.

### Prerequisites

- Python 3.8+
- Git installed on your system
- A Groq API Key

### Installation

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/AliGohar2151/ai-git-commit-assistant
    cd ai-git-commit-assistant
    ```

2.  **Create a virtual environment (recommended):**

    ```bash
    python -m venv .venv
    source .venv/bin/activate  # On Windows: .venv\Scripts\activate
    ```

3.  **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up your Groq API Key:**
    Create a file named `.env` in the root of your project and add your Groq API key:
    ```
    MY_API_KEY="YOUR_GROQ_API_KEY_HERE"
    ```

## 🏃 How to Run

1.  **Activate your virtual environment** (if not already active):

    ```bash
    source .venv/bin/activate # On Windows: .venv\Scripts\activate
    ```

2.  **Run the Streamlit application:**

    ```bash
    streamlit run app.py
    ```

    Your browser should automatically open to the Streamlit app (usually `http://localhost:8501`).

## 🤝 Contributing

Feel free to fork the repository, open issues, or submit pull requests.

## 👤 Author

- **Ali Gohar** - [GitHub Profile](https://github.com/AliGohar2151)
