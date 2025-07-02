from flask import Flask, request, jsonify, render_template, redirect, session, url_for, flash
from pymongo import MongoClient
from dotenv import load_dotenv
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import os, uuid

from vector_store import query_vector_db, load_dataset
from llm_wrapper import query_ollama

# Load .env and dataset
load_dotenv()
load_dataset()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "tobacco_bot_secret")

mongo_client = MongoClient(os.getenv("MONGO_URI"))
db = mongo_client["tobacco_bot"]
chat_history = db["chats"]
users = db["users"]

@app.route("/")
def root():
    return redirect("/login")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username").strip().lower()
        password = request.form.get("password")
        if users.find_one({"username": username}):
            flash("Username already exists.", "danger")
            return render_template("register.html")
        hashed_pw = generate_password_hash(password)
        users.insert_one({"username": username, "password": hashed_pw})
        flash("Account created! Please login.", "success")
        return redirect("/login")
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username").strip().lower()
        password = request.form.get("password")
        user = users.find_one({"username": username})
        if user and check_password_hash(user["password"], password):
            session["user_id"] = username
            return redirect("/chat_ui")
        else:
            flash("Invalid credentials", "danger")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect("/login")

@app.route("/chat_ui")
def chat_ui():
    if "user_id" not in session:
        return redirect("/login")

    user_id = session["user_id"]
    session_id = request.args.get("session_id", "new")

    # If it's a new session request, create it and redirect
    if session_id == "new":
        new_session_id = str(uuid.uuid4())
        chat_history.insert_one({
            "user_id": user_id,
            "session_id": new_session_id,
            "title": "",
            "history": [],
            "created_at": datetime.utcnow()
        })
        return redirect(url_for("chat_ui", session_id=new_session_id))

    # Load all sessions
    user_sessions = list(chat_history.find({"user_id": user_id}))

    session_ids = []
    session_titles = {}
    session_previews = {}
    session_timestamps = {}

    for doc in user_sessions:
        sid = doc["session_id"]
        session_ids.append(sid)

        # Title: stored title > first message > session ID
        title = doc.get("title") or (doc["history"][0]["user_input"] if doc.get("history") else sid)
        session_titles[sid] = title

        preview = doc["history"][0]["response"] if doc.get("history") else ""
        session_previews[sid] = (preview[:50] + "...") if len(preview) > 50 else preview

        created_at = doc.get("created_at", datetime.utcnow())
        session_timestamps[sid] = created_at.strftime("%b %d, %H:%M")

    # Get history for this session
    chat = chat_history.find_one({"user_id": user_id, "session_id": session_id})
    history = chat.get("history", []) if chat else []

    return render_template(
        "chat.html",
        username=user_id,
        sessions=session_ids,
        current_session=session_id,
        history=history,
        session_titles=session_titles,
        session_previews=session_previews,
        session_timestamps=session_timestamps
    )

import time

@app.route("/chat", methods=["POST"])
def chat():
    overall_start = time.time()
    step = lambda label: print(f"{label}: {time.time() - overall_start:.2f}s")

    user_input = request.json.get("message")
    user_id = request.json.get("user_id")
    session_id = request.json.get("session_id")
    step("Parsed request")

    if not all([user_input, user_id, session_id]):
        return jsonify({"error": "Missing data"}), 400

    doc = chat_history.find_one({"user_id": user_id, "session_id": session_id})
    if not doc:
        return jsonify({"error": "Invalid session"}), 404
    step("Fetched session from MongoDB")

    if not doc.get("title") and len(doc.get("history", [])) == 0:
        chat_history.update_one(
            {"user_id": user_id, "session_id": session_id},
            {"$set": {"title": user_input[:40]}}
        )
        step("Set session title")

    recent = doc.get("history", [])[-3:]
    context = "\n".join([f"User: {msg['user_input']}\nBot: {msg['response']}" for msg in recent])
    
    retrieved = query_vector_db(user_input)
    step("Vector search completed")

    prompt = f"""
You are a helpful assistant for Zimbabwean small-scale tobacco farmers.
You ONLY answer questions related to tobacco farming or agriculture.
If the question is not related to tobacco farming, politely explain that you can only assist with tobacco-related topics.

Respond in the same language the user used.

Context:
{context}

Relevant Info:
{retrieved}

User: {user_input}
Bot:"""
    step("Prompt constructed")

    response = query_ollama(prompt)
    step("LLM response generated")

    chat_history.update_one(
        {"user_id": user_id, "session_id": session_id},
        {"$push": {
            "history": {
                "timestamp": datetime.utcnow(),
                "user_input": user_input,
                "response": response
            }
        }}
    )
    step("MongoDB updated with new message")

    print(f"✅ Total request time: {time.time() - overall_start:.2f}s")

    return jsonify({
        "response": response,
        "session_id": session_id
    })


@app.route("/rename_session", methods=["POST"])
def rename_session():
    data = request.get_json()
    user_id = data.get("user_id")
    session_id = data.get("session_id")
    new_title = data.get("new_title")
    if not all([user_id, session_id, new_title]):
        return jsonify({"error": "Missing data"}), 400

    result = chat_history.update_one(
        {"user_id": user_id, "session_id": session_id},
        {"$set": {"title": new_title}}
    )
    if result.modified_count:
        return jsonify({"success": True})
    return jsonify({"error": "Update failed"}), 404

@app.route("/delete_session", methods=["POST"])
def delete_session():
    data = request.get_json()
    user_id = data.get("user_id")
    session_id = data.get("session_id")
    result = chat_history.delete_one({"user_id": user_id, "session_id": session_id})
    return jsonify({"success": result.deleted_count == 1})

@app.route("/search_chats", methods=["POST"])
def search_chats():
    data = request.get_json()
    user_id = data.get("user_id")
    query = data.get("query", "").lower()
    if not user_id or not query:
        return jsonify({"results": []})

    results = []
    sessions = chat_history.find({"user_id": user_id})
    for s in sessions:
        sid = s["session_id"]
        title = s.get("title", sid)
        history = s.get("history", [])

        if query in title.lower():
            preview = history[0].get("response", "") if history else ""
            results.append({
                "session_id": sid,
                "title": title,
                "response": preview[:100],
                "timestamp": s.get("created_at", datetime.utcnow()).strftime("%b %d, %H:%M")
            })
            continue

        for entry in history:
            if query in entry.get("user_input", "").lower() or query in entry.get("response", "").lower():
                preview = entry.get("response", "")
                results.append({
                    "session_id": sid,
                    "title": title,
                    "response": preview[:100],
                    "timestamp": s.get("created_at", datetime.utcnow()).strftime("%b %d, %H:%M")
                })
                break

    return jsonify({"results": results})

if __name__ == "__main__":
    print(os.getenv("MONGO_URI"))
    app.run(debug=True)
