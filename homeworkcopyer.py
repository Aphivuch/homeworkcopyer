import streamlit as st
import sqlite3
import base64

# --- 🎨 1. ตั้งค่าหน้าตาแอปให้ใหญ่พิเศษ (Extra Large GUI) ---
st.set_page_config(page_title="HomeworkCopyer - Admin Edition", page_icon="💻", layout="wide")

st.markdown("""
    <style>
    div.stButton > button {
        font-size: 18px !important;
        font-weight: bold !important;
        border-radius: 10px !important;
    }
    .post-card {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05);
        border-left: 6px solid #2ecc71;
        margin-bottom: 5px;
    }
    .post-title { font-size: 24px; color: #2ecc71; font-weight: bold; margin-bottom: 5px; }
    .post-author { font-size: 14px; color: #7f8c8d; font-weight: bold; }
    .post-content { font-size: 18px; color: #2c3e50; margin-top: 10px; white-space: pre-wrap; }
    </style>
""", unsafe_allow_html=True)

# =======================================================
# 🗄️ [ ระบบฐานข้อมูล SQLite - เพิ่มคอลัมน์ Title ]
# =======================================================
DB_NAME = "homework.db"


def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            author TEXT,
            title TEXT,
            content TEXT,
            image_base64 TEXT
        )
    ''')

    # อัปเกรดฐานข้อมูล: เพิ่มคอลัมน์ title และ image_base64 ถ้ายังไม่มี
    columns = [row[1] for row in c.execute("PRAGMA table_info(posts)")]
    if "title" not in columns:
        c.execute("ALTER TABLE posts ADD COLUMN title TEXT")
    if "image_base64" not in columns:
        c.execute("ALTER TABLE posts ADD COLUMN image_base64 TEXT")

    conn.commit()
    conn.close()


def load_posts_from_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT id, author, title, content, image_base64 FROM posts ORDER BY id DESC")
    rows = c.fetchall()
    conn.close()
    return [{"id": r[0], "author": r[1], "title": r[2], "content": r[3], "image": r[4]} for r in rows]


def save_post_to_db(author, title, content, image_encoded=None):
    try:
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("INSERT INTO posts (author, title, content, image_base64) VALUES (?, ?, ?, ?)",
                  (author, title, content, image_encoded))
        conn.commit()
        conn.close()
        return True
    except:
        return False


def delete_post(post_id):
    """ฟังก์ชันสำหรับ Admin ลบโพสต์"""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM posts WHERE id = ?", (post_id,))
    conn.commit()
    conn.close()


init_db()

# --- 🕹️ 2. ระบบความจำ Session ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "is_admin" not in st.session_state:
    st.session_state.is_admin = False

# =======================================================
# 🔒 [ หน้าล็อกอินนักเรียน ]
# =======================================================
if not st.session_state.logged_in:
    st.columns([1, 2, 1])[1].markdown("<h1 style='text-align: center;'>🔐 เข้าสู่ระบบ HomeworkCopyer</h1>",
                                      unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        user_input = st.text_input("ชื่อเล่นของคุณ:", placeholder="ตัวอย่าง: เดฟ")
        if st.button("🚀 เข้าใช้งานระบบ", use_container_width=True):
            if user_input.strip() != "":
                st.session_state.username = user_input
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("กรุณาใส่ชื่อก่อนนะ!")
    st.stop()

# =======================================================
# 🗂️ 3. แถบเมนูด้านซ้าย (Sidebar)
# =======================================================
with st.sidebar:
    st.markdown(f"### 👋 สวัสดี: **{st.session_state.username}**")
    if st.session_state.is_admin:
        st.success("⭐ สถานะ: ผู้ดูแลระบบ (Admin)")

    st.write("---")
    menu_selection = st.radio("ไปที่วิชา:", ["🐍 Python วิชาคอม ม.2", "📐 คณิตศาสตร์", "🧪 วิทยาศาสตร์"])

    if st.button("🚪 ออกจากระบบ"):
        st.session_state.logged_in = False
        st.session_state.is_admin = False
        st.rerun()

    # --- 🔐 ส่วน Admin Login (ขวาล่างของแถบเมนู) ---
    st.write("---")
    with st.expander("🛠️ สำหรับ Admin"):
        adm_user = st.text_input("User:")
        adm_pass = st.text_input("Pass:", type="password")
        if st.button("Login Admin"):
            if adm_user == "Poor_dev." and adm_pass == "210356่js":
                st.session_state.is_admin = True
                st.success("ล็อกอิน Admin สำเร็จ!")
                st.rerun()
            else:
                st.error("รหัสไม่ถูกต้อง!")

# =======================================================
# 📝 4. หน้าจอหลัก
# =======================================================
if menu_selection == "🐍 Python วิชาคอม ม.2":
    st.title("💻 Python Learning Hub")

    # --- ส่วนที่ 4.1: สร้างโพสต์ใหม่ ---
    with st.container():
        st.subheader("➕ แชร์แนวทางการบ้านใหม่")
        col_t, col_i = st.columns([2, 1])
        with col_t:
            new_title = st.text_input("📌 หัวข้อโพสต์:", placeholder="เช่น แบบฝึกหัดที่ 1, สอบเก็บคะแนน")
        with col_i:
            uploaded_file = st.file_uploader("🖼️ แนบรูปภาพ:", type=["png", "jpg", "jpeg"])

        new_post = st.text_area("เนื้อหา/โค้ด Python:", height=100, placeholder="อธิบายแนวทางหรือวางโค้ดที่นี่...")

        if st.button("📢 โพสต์ลงกระดาน", use_container_width=True):
            if new_title.strip() != "" and (new_post.strip() != "" or uploaded_file is not None):
                image_encoded = None
                if uploaded_file is not None:
                    image_encoded = base64.b64encode(uploaded_file.read()).decode("utf-8")

                if save_post_to_db(st.session_state.username, new_title, new_post, image_encoded):
                    st.success("โพสต์เรียบร้อย!")
                    st.rerun()
            else:
                st.warning("กรุณาใส่หัวข้อและเนื้อหาด้วยนะ!")

    st.write("---")

    # --- ส่วนที่ 4.2: แสดงผลฟีด ---
    st.subheader("📌 รายการการบ้านล่าสุด")
    all_posts = load_posts_from_db()

    for post in all_posts:
        with st.container():
            # ตกแต่งการ์ดโพสต์
            st.markdown(f"""
                <div class="post-card">
                    <div class="post-title">📁 {post['title']}</div>
                    <div class="post-author">👤 โดย: {post['author']}</div>
                    <div class="post-content">{post['content']}</div>
                </div>
            """, unsafe_allow_html=True)

            if post['image']:
                st.image(f"data:image/png;base64,{post['image']}", use_container