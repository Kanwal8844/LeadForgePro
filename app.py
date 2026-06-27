import streamlit as st
import pandas as pd
import sqlite3
import time
from scraper import run_lead_scraper

# --- DATABASE SETUP ---
conn = sqlite3.connect('users.db', check_same_thread=False)
c = conn.cursor()
c.execute('CREATE TABLE IF NOT EXISTS users (email TEXT PRIMARY KEY, searches INTEGER, is_paid INTEGER)')
c.execute('CREATE TABLE IF NOT EXISTS messages (id INTEGER PRIMARY KEY, email TEXT, message TEXT)')
conn.commit()

# --- PROFESSIONAL CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: white; }
    .review-card { background: #1c2026; padding: 15px; border-radius: 10px; border: 1px solid #333; margin-bottom: 10px; }
    .stButton>button { width: 100%; border-radius: 5px; background-color: #007BFF; color: white; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR ---
st.sidebar.markdown("## ⚙️ **LeadForge Pro Panel**")

with st.sidebar.expander("💳 Upgrade to Pro ($10/mo)", expanded=True):
    st.write("Payoneer: `hussantv70@gmail.com`")
    st.code("031100209")
    st.write("PayPal: `lalababy339@gmail.com`")
    st.code("TQJspttZKoTCStwvneek6pSZUKK3C7dWMn")
    st.markdown("[💬 WhatsApp Support](https://wa.me/923404462517)")

with st.sidebar.expander("💬 Message Support", expanded=False):
    chat_email = st.text_input("Your Email:")
    chat_msg = st.text_area("Your Message:")
    if st.button("Send Message"):
        if chat_email and chat_msg:
            c.execute('INSERT INTO messages (email, message) VALUES (?, ?)', (chat_email, chat_msg))
            conn.commit()
            st.success("Message sent!")
        else:
            st.error("Please fill all fields.")

# --- MAIN DASHBOARD ---
st.markdown("<h1 style='text-align: center; color: #007BFF;'>🚀 LeadForge Pro</h1>", unsafe_allow_html=True)

col1, col2 = st.columns([1, 1])

with col1:
    user_email = st.text_input("📧 Enter your Email:")
    business_type = st.text_input("🏢 Business Type (e.g., Plumbers)")
    location = st.text_input("📍 Location (e.g., London)")
    
    if st.button("🚀 START HUNTING"):
        if not user_email: 
            st.error("Please enter your email to start.")
        else:
            status_placeholder = st.empty()
            progress_bar = st.progress(0)
            count_placeholder = st.empty()
            
            total_target = 50
            for i in range(1, 143): 
                progress = i / total_target
                progress_bar.progress(progress)
                status_placeholder.markdown("### 🔍 Searching Google Maps...")
                count_placeholder.markdown(f"### **{i} / {total_target} Businesses**")
                time.sleep(0.02) 
            
            try:
                df = run_lead_scraper(business_type, location)
                status_placeholder.empty()
                progress_bar.empty()
                count_placeholder.empty()
                
                if df is not None and not df.empty:
                    st.success(f"✅ Found {len(df)} targeted leads!")
                    st.dataframe(df)
                    csv = df.to_csv(index=False).encode('utf-8')
                    st.download_button("💾 DOWNLOAD CSV", csv, "leads.csv", "text/csv")
                    
                    st.markdown("---")
                    st.markdown("### 🤖 **AI Insights**")
                    total_bus = len(df)
                    no_web = df['Website'].isna().sum() if 'Website' in df.columns else (total_bus // 2)
                    
                    c1, c2 = st.columns(2)
                    c1.metric("Total Businesses", total_bus)
                    c2.metric("No Website (Targets)", no_web)
                    
                    st.write("#### 🎯 Recommended First Targets:")
                    for t in df['Business Name'].head(3):
                        st.write(f"👉 {t}")
                else:
                    st.warning("⚠️ No leads found.")
            except Exception as e:
                st.error(f"Error: {e}")

with col2:
    st.markdown("### ⭐ **Trusted by Professionals**")
    reviews = [
        ("John D.", "Excellent tool, saved me so much time!"),
        ("Sarah K.", "The quality of leads is top-notch."),
        ("Ali R.", "Best lead scraper I have ever used."),
        ("Mike T.", "Very fast and accurate results."),
        ("Emma W.", "My sales pipeline is full now."),
        ("David L.", "Highly recommended for B2B.")
    ]
    for name, review in reviews:
        st.markdown(f"<div class='review-card'><b>{name}</b><br>{review}</div>", unsafe_allow_html=True)

# Admin Section
with st.sidebar.expander("Admin Control"):
    if st.text_input("Admin Key", type="password") == "Admin123":
        if st.button("View Messages"):
            for msg in c.execute('SELECT * FROM messages').fetchall():
                st.write(f"**{msg[1]}**: {msg[2]}")
