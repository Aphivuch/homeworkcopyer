import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

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
# 📊 [ ระบบฐานข้อมูลเชื่อมต่อไปยัง Google Sheets ]
# =======================================================

# สร้างตัวเชื่อมต่อหลัก
conn = st.connection("gsheets", type=GSheetsConnection)

try:
    sheet_url = st.secrets["connections"]["gsheets"]["spreadsheet"]
except:
    sheet_url = ""


# ฟังก์ชันสำหรับอ่านข้อมูลจาก Google Sheets
def load_posts_from_sheets():
    if sheet_url == "":
        return [
            {"author": "Poor_dev (Admin)", "content": "ใบงานที่ 1: ระบบยังไม่ได้เชื่อมต่อ Google Sheets บนคลาวด์จ้า"}]
    try:
        # อ่านข้อมูลสดใหม่ทุกครั้ง (ttl="0" เพื่อไม่ให้จำค่าแคชเก่าค้างไว้)
        df = conn.read(spreadsheet=sheet_url, ttl="0")

        # ตรวจสอบว่าตารางว่างเปล่าหรือไม่
        if df.empty:
            return []

        df = df.dropna(subset=['author', 'content'], how='all')  # ลบแถวว่าง
        df = df.fillna("")  # แปลงค่า NaN เป็นข้อความว่าง

        posts = df.to_dict(orient="records")
        return posts[::-1]  # เรียงจากโพสต์ล่าสุดขึ้นก่อน
    except Exception as e:
        return [{"author": "Poor_dev (Admin)", "content": f"เกิดข้อผิดพลาดในการโหลดข้อมูล: {e}"}]


# ฟังก์ชันเพิ่มข้อมูลลงตาราง (ปรับปรุงใหม่เพื่อแก้บั๊ก Running ค้าง)
def save_post_to_sheets(author, content):
    if sheet_url != "":
        try:
            # 1. ดึงข้อมูลตารางชุดปัจจุบันออกมาก่อน
            df = conn.read(spreadsheet=sheet_url, ttl="0")

            # 2. สร้างแถวข้อมูลใหม่
            new_row = pd.DataFrame([{"author": str(author), "content": str(content)}])

            # 3. นำข้อมูลใหม่ไปต่อท้ายตารางเดิม
            if df.empty:
                updated_df = new_row
            else:
                updated_df = pd.concat([df, new_row], ignore_index=True)

            # 4. อัปเดตข้อมูลกลับไปยัง Google Sheets ของจริงถาวร
            conn.update(spreadsheet=sheet_url, data=updated_df)
            return True
        except Exception as e:
            st.error(f"เซฟลงแผ่นงานไม่สำเร็จ: {e}")
            return False
    return False


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
            if sheet_url == "":
                st.warning("⚠️ โปรแกรมยังรันในโหมดจำลองอยู่ เนื่องจากยังไม่ได้ใส่ลิงก์ Google Sheets จ้า")
            else:
                # เรียกฟังก์ชันเซฟและตรวจเช็กสถานะการทำงาน
                success = save_post_to_sheets(st.session_state.username, new_post)
                if success:
                    st.success("โพสต์เซฟลงระบบคลาวด์ถาวรสำเร็จแล้ว!")
                    st.rerun()
        else:
            st.warning("พิมพ์ข้อความก่อนกดโพสต์นะ!")

    st.write("---")

    # --- ส่วนที่ 4.2: ดึงข้อมูลจากแผ่นงานมาแสดงบนหน้าฟีด ---
    st.subheader("📌 กระดานแนวทางการบ้านล่าสุด")

    all_posts = load_posts_from_sheets()

    if not all_posts:
        st.info("📌 ยังไม่มีใครโพสต์แนวทางการบ้านเลย คุณเดฟเจิมเป็นคนแรกได้นะ!")
    else:
        for post in all_posts:
            author_val = str(post.get('author', '')).strip()
            content_val = str(post.get('content', '')).strip()

            if author_val or content_val:
                if author_val == "":
                    author_val = "ไม่ระบุชื่อ"

                st.markdown(f"""
                    <div class="post-card">
                        <div class="post-author">👤 โพสต์โดย: {author_val}</div>
                        <div class="post-content">{content_val}</div>
                    </div>
                """, unsafe_allow_html=True)

else:
    st.title(menu_selection)
    st.info("🚧 หน้านี้กำลังอยู่ระหว่างการพัฒนาโดย Poor_dev จ้า เดี๋ยวมาเขียนเพิ่มให้นะ!")