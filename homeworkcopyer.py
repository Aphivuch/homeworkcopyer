import streamlit as st
import sqlite3
import os

# --- 🎨 1. ตั้งค่าหน้าตาแอปให้ใหญ่พิเศษ (Extra Large GUI) ---
st.set_page_config(page_title="HomeworkCopyer - Python Hub", page_icon="💻", layout="wide")

st.markdown("""
    <style>
    div.stButton > button {
        font-size: 22px !important;
        font-weight: bold !important;
        height: 60px !important;
        border-radius: 12px !important;
    }
    .post-card {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05);
        border-left: 6px solid #2ecc71;
        margin-bottom: 20px;
    }
    .post-author { font-size: 16px; color: #7f8c8d; font-weight: bold; }
    .post-content { font-size: 20px; color: #2c3e50; margin-top: 5px; white-space: pre-wrap; }
    </style>
""", unsafe_allow_html=True)

# =======================================================
# 🗄️ [ ระบบฐานข้อมูล SQLite ของจริงหลังบ้าน - แก้ไขคำสั่ง SQL ]
# =======================================================
DB_NAME = "homework.db"


def init_db():
    """ฟังก์ชันสร้างตารางฐานข้อมูลถ้ายังไม่มี (แก้ไข syntax เรียบร้อย)"""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            author TEXT,
            content TEXT
        )
    ''')
    # ตรวจเช็กว่าถ้าไม่มีโพสต์แรก ให้สร้างโพสต์เริ่มต้นของ Admin ไว้ก่อน
    c.execute("SELECT COUNT(*) FROM posts")
    if c.fetchone()[0] == 0:
        c.execute("INSERT INTO posts (author, content) VALUES (?, ?)",
                  ("Poor_dev (Admin)",
                   "ใบงานที่ 1: โค้ดคำนวณพื้นที่สี่เหลี่ยม\n\nwidth = int(input())\nlength = int(input())\nprint('พื้นที่คือ:', width * length)"))
    conn.commit()
    conn.close()


def load_posts_from_db():
    """ดึงข้อมูลโพสต์ทั้งหมดเรียงจากใหม่สุดไปเก่าสุด"""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT author, content FROM posts ORDER BY id DESC")
    rows = c.fetchall()
    conn.close()

    posts = [{"author": row[0], "content": row[1]} for row in rows]
    return posts


def save_post_to_db(author, content):
    """บันทึกโพสต์ใหม่ลงฐานข้อมูลถาวร"""
    try:
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("INSERT INTO posts (author, content) VALUES (?, ?)", (author, content))
        conn.commit()
        conn.close()
        return True
    except:
        return False


# เรียกใช้งานฐานข้อมูลให้พร้อมทำงาน
init_db()

# --- 🕹️ 2. ระบบความจำชั่วคราวสำหรับตัวบุคคล (Session State) ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""

# =======================================================
# 🔒 [ หน้าล็อกอิน ]
# =======================================================
if not st.session_state.logged_in:
    st.columns([1, 2, 1])[1].markdown("<h1 style='text-align: center;'>🔐 เข้าสู่ระบบ HomeworkCopyer</h1>",
                                      unsafe_allow_html=True)
    st.columns([1, 2, 1])[1].write("ระบบคลังแชร์แนวทาง Python ม.2 เพื่อเพื่อนๆ")

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        user_input = st.text_input("พิมพ์ชื่อเล่นหรือชื่อผู้ใช้ของคุณ:", placeholder="ตัวอย่าง: เดฟเตรียมน้อม")
        st.write("")
        if st.button("🚀 เข้าสู่ระบบและจำบัญชีนี้", use_container_width=True):
            if user_input.strip() != "":
                st.session_state.username = user_input
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("กรุณาพิมพ์ชื่อก่อนเข้าใช้งานนะจ๊ะ!")
    st.stop()

# =======================================================
# 🗂️ 3. แถบเมนูด้านซ้ายมือสำหรับเลือกวิชา
# =======================================================
with st.sidebar:
    st.markdown(f"### 👋 สวัสดีคุณ: **{st.session_state.username}**")
    st.write("---")
    st.markdown("### 📚 เลือกรายวิชา")

    menu_selection = st.radio(
        "ไปที่วิชา:",
        ["🐍 Python วิชาคอม ม.2", "📐 คณิตศาสตร์ (ยังไม่เปิด)", "🧪 วิทยาศาสตร์ (ยังไม่เปิด)"],
        index=0
    )

    st.write("---")
    if st.button("🚪 ออกจากระบบ"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.rerun()

# =======================================================
# 📝 4. หน้าจอหลัก (วิชาคอม Python)
# =======================================================
if menu_selection == "🐍 Python วิชาคอม ม.2":
    st.title("💻 Python Learning & Homework Hub")
    st.write("พื้นที่สำหรับแชร์ซอร์สโค้ดและแนวทางการบ้านวิชาคอมพิวเตอร์ ม.2")
    st.write("---")

    # --- ส่วนที่ 4.1: กล่องสำหรับสร้างโพสต์ใหม่ ---
    st.subheader("➕ แชร์ข้อความการบ้าน/โค้ดอันใหม่")
    new_post = st.text_area("พิมพ์ข้อความ หรือ วางโค้ด Python ที่นี่เลยคุณเดฟ:", height=150,
                            placeholder="พิมพ์โจทย์และแนวทางลงตรงนี้...")

    if st.button("📢 กดโพสต์ลงฟีดกระดานดำ", use_container_width=True):
        if new_post.strip() != "":
            success = save_post_to_db(st.session_state.username, new_post)
            if success:
                st.success("โพสต์เซฟลงระบบฐานข้อมูลสำเร็จแล้ว!")
                st.rerun()
            else:
                st.error("เกิดข้อผิดพลาดในการบันทึกข้อมูลหลังบ้าน")
        else:
            st.warning("พิมพ์ข้อความก่อนกดโพสต์นะ!")

    st.write("---")

    # --- ส่วนที่ 4.2: ดึงข้อมูลจากฐานข้อมูล SQLite มาแสดงผลบนหน้าฟีด ---
    st.subheader("📌 กระดานแนวทางการบ้านล่าสุด")

    all_posts = load_posts_from_db()

    if not all_posts:
        st.info("📌 ยังไม่มีใครโพสต์แนวทางการบ้านเลย คุณเดฟเจิมเป็นคนแรกได้นะ!")
    else:
        for post in all_posts:
            st.markdown(f"""
                <div class="post-card">
                    <div class="post-author">👤 โพสต์โดย: {post['author']}</div>
                    <div class="post-content">{post['content']}</div>
                </div>
            """, unsafe_allow_html=True)

else:
    st.title(menu_selection)
    st.info("🚧 หน้านี้กำลังอยู่ระหว่างการพัฒนาโดย Poor_dev จ้า เดี๋ยวมาเขียนเพิ่มให้นะ!")