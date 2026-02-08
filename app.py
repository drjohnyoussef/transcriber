import streamlit as st
import yt_dlp
import whisper
import os
import datetime

# إعدادات الصفحة
st.set_page_config(page_title="محلل فيديوهات فيمو المطور", page_icon="📝")

# --- نظام الحماية بباسورد ---
def check_password():
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False

    if not st.session_state["password_correct"]:
        st.title("🔒 الدخول محمي")
        password = st.text_input("أدخل كلمة المرور (7777):", type="password")
        if st.button("دخول"):
            if password == "7777":
                st.session_state["password_correct"] = True
                st.rerun()
            else:
                st.error("❌ كلمة المرور غير صحيحة")
        return False
    return True

if check_password():
    st.title("🚀 محول الفيديو إلى نص")
    
    # 1. إدخال الرابط (متغير)
    video_url = st.text_input("ضع رابط الفيديو الجديد هنا:", placeholder="https://vimeo.com/...")

    st.divider()

    # 2. الأسئلة والخيارات (الواجهة الجديدة)
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("### ⏱️ خيارات الوقت")
        show_timestamps = st.checkbox("عرض النص مفصل بالوقت؟", value=True)
    
    with col2:
        st.write("### 📄 خيارات العرض")
        output_format = st.radio("ماذا تفضل بعد الانتهاء؟", ["عرض النص فقط", "تحميل ملف فقط", "الاثنين معاً"])

    st.divider()

    # زر التشغيل
    if st.button("ابدأ المعالجة الآن"):
        if not video_url:
            st.warning("من فضلك أدخل الرابط أولاً!")
        else:
            try:
                with st.spinner("⏳ جارٍ سحب الصوت من الرابط..."):
                    ydl_opts = {'format': 'm4a/bestaudio/best', 'outtmpl': 'temp_audio.m4a', 'quiet': True}
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        ydl.download([video_url])
                
                with st.spinner("🧠 الذكاء الاصطناعي يكتب النص الآن..."):
                    model = whisper.load_model("medium")
                    result = model.transcribe("temp_audio.m4a", language="ar")

                    # بناء النص حسب اختيار المستخدم (وقت أو لا)
                    final_text = ""
                    for segment in result['segments']:
                        if show_timestamps:
                            start = str(datetime.timedelta(seconds=int(segment['start'])))
                            final_text += f"[{start}] {segment['text']}\n"
                        else:
                            final_text += f"{segment['text']} "

                    st.success("✅ تم الانتهاء بنجاح!")

                    # تنفيذ رغبة المستخدم في العرض أو التحميل
                    if output_format in ["عرض النص فقط", "الاثنين معاً"]:
                        st.write("### النص المستخرج:")
                        st.text_area("", value=final_text, height=300)

                    if output_format in ["تحميل ملف فقط", "الاثنين معاً"]:
                        st.download_button(
                            label="📥 اضغط هنا لتحميل ملف النص",
                            data=final_text,
                            file_name=f"transcript_{datetime.date.today()}.txt",
                            mime="text/plain"
                        )

                # حذف ملف الصوت المؤقت لتوفير مساحة السيرفر
                if os.path.exists("temp_audio.m4a"):
                    os.remove("temp_audio.m4a")

            except Exception as e:
                st.error(f"حدث خطأ: {e}")

    # خروج
    if st.sidebar.button("تسجيل الخروج"):
        st.session_state["password_correct"] = False
        st.rerun()
