import streamlit as st

# --- 🎨 1. ตั้งค่าหน้าตาแอปให้ดูดี พรีเมียม และปุ่มใหญ่สะใจ ---
st.set_page_config(page_title="HomeworkCopyer - Python Hub", page_icon="💻", layout="wide")

# ตกแต่ง CSS ให้ปุ่มในเมนูและปุ่มกดต่างๆ ดูใหญ่ ใช้งานง่าย สไตล์แอปยุคใหม่
st.markdown("""
    <style>
    /* ขยายขนาดปุ่มทั่วไป */
    div.stButton > button {
        font-size: 22px !important;
        font-weight: bold !important;
        height: 60px !important;
        border-radius: 12px !important;
    }
    /* กล่องสำหรับฟีดโพสต์การบ้าน */
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

# --- 🕹️ 2. ระบบความจำหลังบ้าน (Session State) ---
# จำสถานะการล็อกอิน
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""

# คลังจำโพสต์ข้อความการบ้าน (จำข้อมูลไว้ในครั้งต่อๆ ไปตราบที่แอปยังรันอยู่)
if "homework_posts" not in st.session_state:
    st.session_state.homework_posts = [
        {"author": "Poor_dev (Admin)",
         "content": "ใบงานที่ 1: โค้ดคำนวณพื้นที่สี่เหลี่ยม\n\nwidth = int(input())\nlength = int(input())\nprint('พื้นที่คือ:', width * length)"}
    ]

# =======================================================
# 🔒 [ ระบบล็อกอิน / สร้างบัญชีจำชื่อ ]
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
    st.stop()  # หยุดทำงานตรงนี้ถ้ายังไม่ได้ล็อกอิน

# =======================================================
# 🗂️ 3. แถบเมนูด้านซ้ายมือสำหรับเลือกวิชา (ตามสั่ง)
# =======================================================
with st.sidebar:
    st.markdown(f"### 👋 สวัสดีคุณ: **{st.session_state.username}**")
    st.write("---")
    st.markdown("### 📚 เลือกรายวิชา")

    # ปุ่มเมนูขนาดใหญ่ด้านซ้ายมือ
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
# 📝 4. หน้าจอหลักตามเมนูที่เลือก (ตอนนี้เป็นวิชาคอม Python)
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
            # เพิ่มโพสต์ใหม่เข้าไปในระบบความจำ
            st.session_state.homework_posts.insert(0, {"author": st.session_state.username, "content": new_post})
            st.success("โพสต์ลงกระดานสำเร็จแล้วเพื่อนๆ เห็นแน่นอน!")
            st.rerun()
        else:
            st.warning("พิมพ์ข้อความก่อนกดโพสต์นะ!")

    st.write("---")

    # --- ส่วนที่ 4.2: ฟีดกระดานแสดงโพสต์การบ้าน (คล้ายๆ ฟีดเฟซบุ๊ก) ---
    st.subheader("📌 กระดานแนวทางการบ้านล่าสุด")

    for post in st.session_state.homework_posts:
        st.markdown(f"""
            <div class="post-card">
                <div class="post-author">👤 โพสต์โดย: {post['author']}</div>
                <div class="post-content">{post['content']}</div>
            </div>
        """, unsafe_allow_html=True)

else:
    # สำหรับวิชาอื่นๆ ที่ยังไม่ได้เปิด
    st.title(menu_selection)
    st.info("🚧 หน้านี้กำลังอยู่ระหว่างการพัฒนาโดย Poor_dev เดี๋ยวมาเขียนเพิ่มให้นะ!")