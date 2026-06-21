import streamlit as st
import sqlite3
import base64

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
    .post-image { margin-top: 15px; border-radius: 10px; max-width: 100%; height: auto; }
    </style>
""", unsafe_allow_html=True)

# =======================================================
# 🗄️ [ ระบบฐานข้อมูล SQLite - เพิ่มคอลัมน์เก็บรูปภาพ ]
# =======================================================
DB_NAME = "homework.db"


def init_db():
    """ฟังก์ชันสร้างตารางฐานข้อมูลและเพิ่มคอลัมน์ภาพ"""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            author TEXT,
            content TEXT
        )
    ''')

    # ตรวจสอบและเพิ่มคอลัมน์ image_base64 เข้าไปในตารางเดิมอย่างปลอดภัย
    try:
        c.execute("ALTER TABLE posts ADD COLUMN image_base64 TEXT")
    except sqlite3.OperationalError:
        # ถ้ามีคอลัมน์นี้อยู่แล้วจะไม่ทำอะไรข้ามไปเลย
        pass

    conn.commit()
    conn.close()


def load_posts_from_db():
    """ดึงข้อมูลโพสต์และรูปภาพทั้งหมด"""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT author, content, image_base64 FROM posts ORDER BY id DESC")
    rows = c.fetchall()
    conn.close()

    posts = [{"author": row[0], "content": row[1], "image": row[2]} for row in rows]
    return posts


def save_post_to_db(author, content, image_encoded=None):
    """บันทึกโพสต์พร้อมรหัสรูปภาพลงฐานข้อมูล"""
    try:
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("INSERT INTO posts (author, content, image_base64) VALUES (?, ?, ?)",
                  (author, content, image_encoded))
        conn.commit()
        conn.close()
        return True
    except:
        return False


# เรียกใช้งานฐานข้อมูลให้พร้อมระบบใหม่
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

    # --- ส่วนที่ 4.1: กล่องสำหรับสร้างโพสต์ใหม่และอัปโหลดรูปภาพ ---
    st.subheader("➕ แชร์ข้อความการบ้าน/โค้ดอันใหม่")
    new_post = st.text_area("พิมพ์ข้อความ หรือ วางโค้ด Python ที่นี่เลยคุณเดฟ:", height=120,
                            placeholder="พิมพ์โจทย์และแนวทางลงตรงนี้...")

    # 📸 ช่องอัปโหลดรูปภาพ รองรับ png, jpg, jpeg
    uploaded_file = st.file_uploader("🖼️ แนบรูปภาพประกอบการบ้าน (ถ้ามี):", type=["png", "jpg", "jpeg"])

    if st.button("📢 กดโพสต์ลงฟีดกระดานดำ", use_container_width=True):
        # โพสต์ได้ถ้ามีข้อความ หรือมีรูปภาพอย่างใดอย่างหนึ่ง
        if new_post.strip() != "" or uploaded_file is not None:

            image_encoded = None
            # ถ้าผู้ใช้อัปโหลดรูปมา -> แปลงรูปเป็นรหัสข้อความ Base64
            if uploaded_file is not None:
                file_bytes = uploaded_file.read()
                image_encoded = base64.b64encode(file_bytes).decode("utf-8")

            success = save_post_to_db(st.session_state.username, new_post, image_encoded)
            if success:
                st.success("โพสต์เซฟลงระบบฐานข้อมูลสำเร็จแล้ว!")
                st.rerun()
            else:
                st.error("เกิดข้อผิดพลาดในการบันทึกข้อมูลหลังบ้าน")
        else:
            st.warning("กรุณาพิมพ์ข้อความหรือแนบรูปภาพก่อนกดโพสต์นะ!")

    st.write("---")

    # --- ส่วนที่ 4.2: แสดงผลฟีดข่าวสารพร้อมรูปภาพ ---
    st.subheader("📌 กระดานแนวทางการบ้านล่าสุด")

    all_posts = load_posts_from_db()

    if not all_posts:
        st.info("📌 ยังไม่มีใครโพสต์แนวทางการบ้านเลย คุณเดฟเจิมเป็นคนแรกได้นะ!")
    else:
        for post in all_posts:
            author_val = post['author'] if post['author'] else "ไม่ระบุชื่อ"
            content_val = post['content']
            img_val = post['image']

            # 1. แสดงกล่องข้อความโพสต์
            st.markdown(f"""
                <div class="post-card">
                    <div class="post-author">👤 โพสต์โดย: {author_val}</div>
                    <div class="post-content">{content_val}</div>
                </div>
            """, unsafe_allow_html=True)

            # 2. ถ้าโพสต์นั้นมีรูปภาพ ให้แปลงรหัสกลับมาเป็นรูปภาพแสดงผลต่อท้ายทันที
            if img_val:
                st.image(f"data:image/png;base64,{img_val}", use_container_width=True)

else:
    st.title(menu_selection)
    st.info("🚧 หน้านี้กำลังอยู่ระหว่างการพัฒนาโดย Poor_dev จ้า เดี๋ยวมาเขียนเพิ่มให้นะ!")