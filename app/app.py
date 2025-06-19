# app.py (Streamlit)

import streamlit as st
import requests

# 🔧 Point to your FastAPI prefix
API_BASE = "http://localhost:8000/Rag"

st.set_page_config(layout="wide", page_title="Web‑KB Manager")
st.title("🔗 KaptureCX RAG UI")

tabs = st.tabs([
    "1. Create KB (Single Link)",
    "2. Create KB (Multiple Links)",
    "3. List Scraped URLs",
    "4. Q&A",
    "5. Check Status"
])

def call_api(path: str, payload: dict):
    url = f"{API_BASE}{path}"
    res = requests.post(url, json=payload)
    st.write(f"▶️ POST {url} → {res.status_code}")
    try:
        st.json(res.json())
    except Exception:
        st.text(res.text)

# --- Tab 1: Single Link KB Creation ---
with tabs[0]:
    st.header("1️⃣ Create KB (Single Link)")
    with st.form("form1"):
        name1   = st.text_input("KB Name")
        cmd1    = st.text_input("Client Cmd ID")
        link1   = st.text_input("Web Link")
        ok1     = st.form_submit_button("Create KB")
    if ok1:
        call_api("/web_link_to_knowledge", {
            "name": name1,
            "cmd_id": cmd1,
            "link": link1
        })

# --- Tab 2: Multiple Links KB Creation ---
with tabs[1]:
    st.header("2️⃣ Create KB (Multiple Links)")
    with st.form("form2"):
        name2    = st.text_input("KB Name", key="mname")
        cmd2     = st.text_input("Client Cmd ID", key="mcmd")
        links_in = st.text_area("One URL per line", height=150)
        ok2      = st.form_submit_button("Create Multi‑Link KB")
    if ok2:
        multi = [u.strip() for u in links_in.splitlines() if u.strip()]
        call_api("/Multiple_web_link_to_knowledge", {
            "name": name2,
            "cmd_id": cmd2,
            "multi_links": multi
        })

# --- Tab 3: Retrieve Scraped URLs ---
with tabs[2]:
    st.header("3️⃣ Retrieve Scraped URLs")
    with st.form("form3"):
        name3 = st.text_input("KB Name", key="rname")
        cmd3  = st.text_input("Client Cmd ID", key="rcmd")
        ok3   = st.form_submit_button("Get Scraped URLs")
    if ok3:
        call_api("/Scarped_website_links", {
            "name": name3,
            "cmd_id": cmd3
        })

# --- Tab 4: Question Answering ---
with tabs[3]:
    st.header("4️⃣ Ask a Question")
    with st.form("form4"):
        coll  = st.text_input("Collection Name", key="coll4")
        query = st.text_input("Your Question", key="query4")
        method = st.selectbox("Method", ["vector_search", "keyword_search", "hybrid_search"])
        ok4 = st.form_submit_button("Ask")
    if ok4:
        call_api(f"/{method}", {
            "coll": coll,
            "query": query
        })

# --- Tab 5: Check Ingestion Status ---
with tabs[4]:
    st.header("5️⃣ Check KB Status")
    with st.form("form5"):
        name5 = st.text_input("KB Name", key="sname")
        cmd5  = st.text_input("Client Cmd ID", key="scmd")
        ok5   = st.form_submit_button("Check Status")
    if ok5:
        call_api("/collection_status", {
            "name": name5,
            "cmd_id": cmd5
        })
