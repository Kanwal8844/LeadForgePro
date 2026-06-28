import streamlit as st
import pandas as pd
import sqlite3
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# --- DATABASE SETUP (Messages) ---
conn = sqlite3.connect('users.db', check_same_thread=False)
c = conn.cursor()
c.execute('CREATE TABLE IF NOT EXISTS messages (id INTEGER PRIMARY KEY, email TEXT, message TEXT)')
conn.commit()

# --- GOOGLE SHEET CONNECTION ---
scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets', "https://www.googleapis.com/auth/drive"]
# Yaad rakhein: VPS par bhi 'credentials.json' hona zaroori hai
creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
client = gspread.authorize(creds)

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
st.markdown("<h1 style='text-align: center; color: #007BFF;'>🚀 LeadForge Pro Dashboard</h1>", unsafe_allow_html=True)

if st.button("🔄 REFRESH LIVE DATA"):
    try:
        # Sheet se data read karein
        sheet = client.open("LeadData").sheet1
        # Sari values uthao
        raw_data = sheet.get_all_values() 
        
        if len(raw_data) > 1:
            # Pehli row ko headers aur baqi ko data banayein
            df = pd.DataFrame(raw_data[1:], columns=raw_data[0])
            
            # Khali rows ko hata dein
            df = df[df['Business Name'] != '']
            
            st.success(f"✅ Showing {len(df)} latest leads!")
            st.dataframe(df)
            
            # Download Button
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("💾 DOWNLOAD CSV", csv, "leads.csv", "text/csv")
        else:
            st.warning("⚠️ Sheet mein data nahi hai. Pehle apne PC se scraper chalayein!")
    except Exception as e:
        st.error(f"Error connecting to data: {e}")

# Reviews Section
st.markdown("### ⭐ **Trusted by Professionals**")
col_r1, col_r2 = st.columns(2)
reviews = [("John D.", "Excellent tool!"), ("Sarah K.", "Quality leads."), ("Ali R.", "Very fast."), ("Mike T.", "Accurate.")]
for i, (name, review) in enumerate(reviews):
    if i % 2 == 0: col_r1.markdown(f"<div class='review-card'><b>{name}</b><br>{review}</div>", unsafe_allow_html=True)
    else: col_r2.markdown(f"<div class='review-card'><b>{name}</b><br>{review}</div>", unsafe_allow_html=True)

# Admin Section
with st.sidebar.expander("Admin Control"):
    if st.text_input("Admin Key", type="password") == "Admin123":
        if st.button("View Messages"):
            for msg in c.execute('SELECT * FROM messages').fetchall():
                st.write(f"**{msg[1]}**: {msg[2]}")
