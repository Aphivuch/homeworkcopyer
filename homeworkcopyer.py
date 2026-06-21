import streamlit as st
import sqlite3
import base64
from datetime import datetime

# --- 🎨 1. ตั้งค่าหน้าตาแอปให้ใหญ่พิเศษ (Extra Large GUI) ---
st.set_page_config(page_title="HomeworkCopyer - Full School Edition", page_icon="💻", layout="wide")

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
    .cal-card {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05);
        border-left: 6px solid #e74c3c;
        margin-bottom: 10px;
    }
    .post-title { font-size: 24px; color: #2ecc71; font-weight: bold; margin-bottom: 5px; }
    .cal-title { font-size: 22px; color: #e74c3c; font-weight: bold; margin-bottom: 5px; }
    .post-author { font-size: 14px; color: #7f8c8d; font-weight: bold; }
    .post-content { font-size: 18px; color: #2c3e50; margin-top: 10px; white-space: pre-wrap; }
    </style>
""", unsafe_allow_html=True)

# =======================================================
# 🗄️ [ ระบบฐานข้อมูล SQLite - รองรับการแยกรายวิชา ]
# =======================================================
DB_NAME = "homework.db"
# รายชื่อวิชาทั้งหมดในระบบ (แก้ไขตรงนี้ที่เดียวจะอัปเดตทุกจุดอัตโนมัติ)
ALL_SUBJECTS = [
    "🐍 Python วิชาคอม ม.2",
    "📐 คณิตศาสตร์",
    "🧪 วิทยาศาสตร์",
    "🇹🇭 ภาษาไทย",
    "🌍 สังคมศึกษา",
    "🙏 พระพุทธศาสนา",
    "📜 ประวัติศาสตร์",
    "💡 วิชา IS"
]


def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    # 1. ตารางโพสต์ปกติ (เพิ่มคอลัมน์ subject เพื่อแยกวิชา)
    c.execute('''
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject TEXT,
            author TEXT,
            title TEXT,
            content TEXT,
            image_base64 TEXT
        )
    ''')
    # 2. ตารางปฏิทินการบ้าน
    c.execute('''
        CREATE TABLE IF NOT EXISTS calendar_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            due_date TEXT,
            subject TEXT,
            title TEXT,
            created_by TEXT
        )
    ''')

    # ตรวจสอบและอัปเกรดโครงสร้างฐานข้อมูลตารางเก่าอัตโนมัติ
    columns = [row[1] for row in c.execute("PRAGMA table_info(posts)")]
    if "subject" not in columns:
        c.execute("ALTER TABLE posts ADD COLUMN subject TEXT")
    if "title" not in columns:
        c.execute("ALTER TABLE posts ADD COLUMN title TEXT")
    if "image_base64" not in columns:
        c.execute("ALTER TABLE posts ADD COLUMN image_base64 TEXT")

    conn.commit()
    conn.close()


# --- ฟังก์ชันจัดการโพสต์แยกตามวิชา ---
def load_posts_by_subject(subject_name):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    # ดึงเฉพาะโพสต์ที่ตรงกับวิชาที่ผู้ใช้กดเลือก
    c.execute("SELECT id, author, title, content, image_base64 FROM posts WHERE subject = ? ORDER BY id DESC",
              (subject_name,))
    rows = c.fetchall()
    conn.close()
    return [{"id": r[0], "author": r[1], "title": r[2], "content": r[3], "image": r[4]} for r in rows]


def save_post_to_db(subject, author, title, content, image_encoded=None):
    try:
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("INSERT INTO posts (subject, author, title, content, image_base64) VALUES (?, ?, ?, ?, ?)",
                  (subject, author, title, content, image_encoded))
        conn.commit()
        conn.close()
        return True
    except:
        return False


def delete_post(post_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM posts WHERE id = ?", (post_id,))
    conn.commit()
    conn.close()


# --- ฟังก์ชันจัดการปฏิทินการบ้าน ---
def save_cal_event(due_date, subject, title, created_by):
    try:
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("INSERT INTO calendar_events (due_date, subject, title, created_by) VALUES (?, ?, ?, ?)",
                  (due_date, subject, title, created_by))
        conn.commit()
        conn.close()
        return True
    except:
        return False


def load_cal_events():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT id, due_date, subject, title, created_by FROM calendar_events ORDER BY due_date ASC")
    rows = c.fetchall()
    conn.close()
    return [{"id": r[0], "due_date": r[1], "subject": r[2], "title": r[3], "created_by": r[4]} for r in rows]


def delete_cal_event(event_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM calendar_events WHERE id = ?", (event_id,))
    conn.commit()
    conn.close()


# เรียกใช้ฐานข้อมูล
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
# 🗂️ 3. แถบเมนูด้านซ้าย (Sidebar) - อัปเดตรายชื่อวิชาใหม่ทั้งหมด
# =======================================================
with st.sidebar:
    st.markdown(f"### 👋 สวัสดี: **{st.session_state.username}**")
    if st.session_state.is_admin:
        st.success("⭐ สถานะ: Admin (Poor_dev.)")

    st.write("---")

    # รวมเมนูทั้งหมดโดยเอาปฏิทินขึ้นก่อน และตามด้วยวิชาทั้งหมดที่คุณเดฟขอมา
    menu_selection = st.radio("เลือกเมนู:", ["📅 ปฏิทินการบ้าน"] + ALL_SUBJECTS)

    if st.button("🚪 ออกจากระบบ"):
        st.session_state.logged_in = False
        st.session_state.is_admin = False
        st.rerun()

    # --- 🔐 กล่องล็อกอิน Admin ---
    st.write("---")
    with st.expander("🛠️ สำหรับ Admin ล็อกอิน"):
        adm_user = st.text_input("User:")
        adm_pass = st.text_input("Pass:", type="password")
        if st.button("Login Admin"):
            if adm_user == "Poor_dev." and adm_pass == "210356่js":
                st.session_state.is_admin = True
                st.success("ล็อกอิน Admin สำเร็จแล้ว!")
                st.rerun()
            else:
                st.error("รหัสไม่ถูกต้อง!")

# =======================================================
# 📝 4. หน้าจอหลัก (เปลี่ยนตามเมนูที่กด)
# =======================================================

# ------ 📅 [ หน้าระบบปฏิทินการบ้าน ] ------
if menu_selection == "📅 ปฏิทินการบ้าน":
    st.title("📅 ปฏิทินแจ้งกำหนดส่งการบ้าน")
    st.write("ระบบบันทึกและดูวันครบกำหนดส่งงานของทุกวิชา")

    with st.container():
        st.subheader("➕ เพิ่มกำหนดส่งการบ้านใหม่")
        col_d, col_s = st.columns([1, 1])
        with col_d:
            due_date = st.date_input("🗓️ เลือกวัน/เดือน/ปี ที่ต้องส่ง:", min_value=datetime.today())
        with col_s:
            # ดึงรายชื่อวิชาทั้งหมดมาใส่ในตัวเลือกปฏิทิน
            subject = st.selectbox("📚 เลือกวิชา:", ALL_SUBJECTS)

        cal_title = st.text_input("📌 ตั้งชื่อหัวข้อการบ้านเอง:", placeholder="พิมพ์หัวข้อ เช่น แบบฝึกหัด1 เรื่อง abc")

        if st.button("💾 บันทึกลงปฏิทิน", use_container_width=True):
            if cal_title.strip() != "":
                if save_cal_event(str(due_date), subject, cal_title, st.session_state.username):
                    st.success("บันทึกกำหนดส่งการบ้านเรียบร้อย!")
                    st.rerun()
            else:
                st.warning("กรุณากรอกชื่อหัวข้อการบ้านด้วยนะครับคุณเดฟ!")

    st.write("---")

    st.subheader("📋 รายการส่งการบ้านที่กำลังจะมาถึง (เรียงตามกำหนดส่ง)")
    events = load_cal_events()

    if not events:
        st.info("🎉 ตอนนี้ยังไม่มีกำหนดส่งการบ้านใดๆ สบายใจได้!")
    else:
        for ev in events:
            date_obj = datetime.strptime(ev['due_date'], "%Y-%m-%d")
            formatted_date = date_obj.strftime("%d %B %Y")

            with st.container():
                st.markdown(f"""
                    <div class="cal-card">
                        <div class="cal-title">🚨 กำหนดส่ง: {formatted_date}</div>
                        <div class="post-author">📚 วิชา: {ev['subject']} | 👤 คนบันทึก: {ev['created_by']}</div>
                        <div class="post-content" style="font-weight: bold; color: #c0392b;">📝 งานที่ต้องส่ง: {ev['title']}</div>
                    </div>
                """, unsafe_allow_html=True)

                if st.session_state.is_admin:
                    if st.button(f"🗑️ ลบงานนี้ [{ev['title']}]", key=f"del_ev_{ev['id']}"):
                        delete_cal_event(ev['id'])
                        st.success("ลบรายการออกจากปฏิทินแล้ว!")
                        st.rerun()
                st.write("")

# ------ 📚 [ หน้าของทุกๆ วิชาแชร์การบ้าน ] ------
elif menu_selection in ALL_SUBJECTS:
    st.title(f"{menu_selection}")
    st.write(f"พื้นที่สำหรับแชร์ซอร์สโค้ด แนวทาง ใบงาน และการบ้านของวิชา {menu_selection}")

    with st.container():
        st.subheader("➕ แชร์แนวทางการบ้านใหม่")
        col_t, col_i = st.columns([2, 1])
        with col_t:
            new_title = st.text_input("📌 หัวข้อโพสต์ (เช่น แบบฝึกหัด1):", placeholder="พิมพ์ชื่อแบบฝึกหัดตรงนี้...")
        with col_i:
            uploaded_file = st.file_uploader("🖼️ แนบรูปภาพประกอบ (ถ้ามี):", type=["png", "jpg", "jpeg"])

        new_post = st.text_area("รายละเอียดงาน / แนวทางการทำ:", height=100,
                                placeholder="พิมพ์คำอธิบายโจทย์ หรือ วางแนวทางคำตอบที่นี่...")

        if st.button("📢 โพสต์ลงกระดาน", use_container_width=True):
            if new_title.strip() != "" and (new_post.strip() != "" or uploaded_file is not None):
                image_encoded = None
                if uploaded_file is not None:
                    image_encoded = base64.b64encode(uploaded_file.read()).decode("utf-8")

                # ทำการเซฟโดยระบุ "ชื่อวิชา" กำกับลงไปด้วย
                if save_post_to_db(menu_selection, st.session_state.username, new_title, new_post, image_encoded):
                    st.success(f"โพสต์ลงวิชา {menu_selection} สำเร็จ!")
                    st.rerun()
            else:
                st.warning("กรุณากรอก 'หัวข้อโพสต์' และเนื้อหาให้เรียบร้อยก่อนส่งนะจ๊ะ!")

    st.write("---")

    st.subheader(f"📌 รายการการบ้านวิชา {menu_selection} ล่าสุด")
    # ดึงโพสต์เฉพาะของวิชานี้ขึ้นมาโชว์
    all_posts = load_posts_by_subject(menu_selection)

    if not all_posts:
        st.info(f"📌 ยังไม่มีใครโพสต์แนวทางการบ้านของวิชานี้เลย คุณเดฟประเดิมโพสต์แรกได้นะ!")
    else:
        for post in all_posts:
            with st.container():
                author_val = post['author'] if post['author'] else "ไม่ระบุชื่อ"
                title_val = post['title'] if post['title'] else "ไม่มีหัวข้อ"

                st.markdown(f"""
                    <div class="post-card">
                        <div class="post-title">📁 {title_val}</div>
                        <div class="post-author">👤 โดย: {author_val}</div>
                        <div class="post-content">{post['content']}</div>
                    </div>
                """, unsafe_allow_html=True)

                if post['image']:
                    st.image(f"data:image/png;base64,{post['image']}", use_container_width=True)

                if st.session_state.is_admin:
                    if st.button(f"🗑️ ลบโพสต์ [{title_val}]", key=f"del_{post['id']}"):
                        delete_post(post['id'])
                        st.success("ลบโพสต์เรียบร้อย!")
                        st.rerun()
                st.write("---")