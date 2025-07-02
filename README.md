
# Tobacco Farmers Chatbot 🧑🏽‍🌾💬

A **local AI assistant** for small-scale tobacco farmers in Zimbabwe.  
Answers tobacco-related questions in **Shona** or **English**, works offline once set up, and helps farmers improve yield, budgeting, and good practices.

---

## 📌 **Table of Contents**

1. [Overview](#overview)
2. [Features](#features)
3. [System Requirements](#system-requirements)
4. [Installation](#installation)
5. [Project Structure](#project-structure)
6. [How to Run](#how-to-run)
7. [How to Use](#how-to-use)
8. [MongoDB Setup](#mongodb-setup)
9. [FAQ & Troubleshooting](#faq--troubleshooting)
10. [Future Improvements](#future-improvements)
11. [License & Author](#license--author)

---

## ✅ **Overview**

This project helps Zimbabwean tobacco farmers by providing:
- Accurate answers to common questions
- Farm practice tips
- Basic budgeting calculations
- Context-aware, local knowledge retrieval

It runs entirely **offline** after setup using:
- **Flask** (Python web server)
- **MongoDB** (chat history)
- **ChromaDB** (vector store for RAG)
- **Ollama** (to run Llama/Mistral locally)

---

## ✅ **Features**

- 🗣️ Responds in **Shona or English**
- 🔍 Uses **retrieval-augmented generation** from your own CSV knowledge base
- 💬 Saves chat sessions in MongoDB
- 📝 Sessions can be **renamed**, **deleted**, and **searched**
- ⚡ Word-by-word typing effect with **typing indicator**
- 📱 Fully responsive **Bootstrap UI** with collapsible sidebar

---

## ✅ **System Requirements**

- **OS:** Windows / Linux / macOS
- **Python:** 3.10+
- **MongoDB:** installed locally or Atlas
- **Ollama:** installed and your local model pulled (`mistral` recommended)
- **ChromaDB:** installed via Python

---

## ✅ **Installation**

### 1️⃣ Clone the repo

```bash
git clone https://github.com/yourusername/tobacco_chatbot.git
cd tobacco_chatbot
```

### 2️⃣ Create & activate virtual environment

```bash
python -m venv venv
# Linux/Mac:
source venv/bin/activate
# Windows:
venv\Scripts\activate
```

### 3️⃣ Install dependencies

```bash
pip install -r requirements.txt
```

### 4️⃣ Install & run MongoDB

- Install [MongoDB Community](https://www.mongodb.com/try/download/community)
- Start it:
  ```bash
  mongod
  ```

### 5️⃣ Install Ollama and pull model

```bash
ollama pull mistral
ollama run mistral
```

---

## ✅ **Project Structure**

```plaintext
📂 tobacco_chatbot/
│
├── app.py              # Main Flask app
├── llm_wrapper.py      # Handles Ollama subprocess calls
├── vector_store.py     # Loads and queries ChromaDB
├── requirements.txt    # Python dependencies
├── .env                # Contains MongoDB URI & Flask secrets
├── 📂 data/
│   └── tobacco_faq.csv # Local Q&A knowledge base
├── 📂 templates/
│   ├── layout.html     # Base HTML layout
│   ├── chat.html       # Full chat UI
│   ├── login.html      # User login page
│   └── register.html   # User registration page
└── 📂 static/          # (Optional) Extra CSS/JS if needed

```

---

## ✅ **How to Run**

```bash
# Activate virtualenv first!
python app.py
```

Visit 👉 [http://127.0.0.1:5000/chat_ui](http://127.0.0.1:5000/chat_ui)

---

## ✅ **How to Use**

1. Click **New Chat** in the sidebar.
2. Type your question — e.g.:
   ```
   Ndinga wedzera sei goho retobacco rangu?
   ```
3. The bot:
   - Retrieves relevant answers from `tobacco_faq.csv`
   - Passes them to the LLM
   - Streams reply **word by word**
4. Rename sessions using the dropdown.
5. Search old sessions using the **Search** button.
6. Collapse sidebar using ☰ on small screens.

---

## ✅ Install & run MongoDB

- **For local MongoDB**:
  - Download [MongoDB Community Server](https://www.mongodb.com/try/download/community)
  - Install and start it with:
    ```bash
    mongod
    ```
  - Create your database, user, and password if needed.

---

## ✅ **MongoDB Atlas Setup (Optional)**

If you prefer **MongoDB Atlas** instead of local MongoDB:

1. Sign up at [mongodb.com](https://www.mongodb.com/cloud/atlas).
2. Create a **Free Shared Cluster**.
3. Create a **Database User** with username and password.
4. Add your **IP address** to the IP Access List (e.g., `0.0.0.0/0` for all).
5. Copy the **Connection String** (SRV) and update your `.env` file like so:

```env
MONGO_URI=mongodb+srv://<username>:<password>@<cluster-name>.mongodb.net/?retryWrites=true&w=majority
```

6. Replace `<username>`, `<password>`, and `<cluster-name>` with your actual details.

---

## ✅ **FAQ & Troubleshooting**

| Problem | Solution |
|---------|-----------|
| ⚡ **Bot is slow** | Use a lighter model, check CPU usage |
| 🗂️ **No chat history saved** | Make sure MongoDB is running |
| ❌ **CSV load error** | Ensure `tobacco_faq.csv` is UTF-8 |
| 🔗 **Vector search not working** | Double-check `load_dataset()` runs at startup |
| 🧹 **UI glitches** | Clear browser cache, check console |

---

## ✅ **Future Improvements**

- User accounts & multi-user support
- Admin dashboard to update Q&A
- Integration with phone SMS
- Farm expense tracking
- Leaf disease photo analysis

---

## ✅ **License & Author**

**Author:** Munashe Mudabura  
**License:** MIT — free to modify, use, and share.

---

## ✅ **Screenshots**

*(Add your screenshots here once you’re ready)*

---

**💡 Good luck & happy coding!**
