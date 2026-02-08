import streamlit as st
import yt_dlp
import whisper
import os
import datetime

# إعدادات الصفحة
st.set_page_config(page_title="المفرغ الذكي الآمن", page_icon="🔐")

# --- نظام الحماية المحدث ---
def check_password():
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False

    if not st.session_state["password_correct"]:
        st.title("🔒 نظام الدخول الآمن")
        # تم تغيير الباسورد وإخفاء الهينت هنا
        password = st.text_input("برجاء إدخال كلمة المرور الخاصة بك:", type="password", placeholder="أدخل الرمز السري")
        if st.button("دخول"):
            if password == "777@jo":
                st.session_state["password_correct"] = True
                st.rerun()
            else:
                st.error("❌ الرمز السري غير صحيح!")
        return False
    return True

if check_password():
    st.title("🎙️ المحول الشامل (نسخة خاصة)")
    
    # --- خيارات الإدخال ---
    input_source = st.radio("اختر مصدر الفيديو/الصوت:", ["رابط من الإنترنت", "رفع ملف من الجهاز"])
    
    video_url = ""
    uploaded_file = None

    if input_source == "رابط من الإنترنت":
        video_url = st.text_input("ضع الرابط هنا:")
    else:
        uploaded_file = st.file_uploader("اختر ملف من موبايلك:", type=["mp4", "m4a", "mp3", "mov", "wav"])

    st.divider()

    # --- خيارات العرض ---
    col1, col2 = st.columns(2)
    with col1:
        show_timestamps = st.checkbox("عرض التوقيت الزمني؟", value=True)
    with col2:
        output_format = st.radio("طريقة الاستلام:", ["عرض فقط", "تحميل ملف", "الاثنين معا"])

    st.divider()

    if st.button("🚀 ابدأ المعالجة"):
        audio_path = "temp_audio.m4a"
        
        try:
            if input_source == "رابط من الإنترنت" and video_url:
                with st.spinner("⏳ جارٍ سحب الصوت..."):
                    ydl_opts = {'format': 'm4a/bestaudio/best', 'outtmpl': 'temp_audio', 'quiet': True}
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        ydl.download([video_url])
                    audio_path = "temp_audio.m4a"
            
            elif input_source == "رفع ملف من الجهاز" and uploaded_file:
                with st.spinner("⏳ جارٍ تجهيز الملف..."):
                    with open("temp_upload", "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    audio_path = "temp_upload"
            else:
                st.warning("من فضلك أدخل رابطاً أو ارفع ملفاً!")
                st.stop()

            with st.spinner("🧠 الذكاء الاصطناعي يحلل الكلام..."):
                model = whisper.load_model("medium")
                result = model.transcribe(audio_path)

                final_text = ""
                for segment in result['segments']:
                    if show_timestamps:
                        start = str(datetime.timedelta(seconds=int(segment['start'])))
                        final_text += f"[{start}] {segment['text']}\n"
                    else:
                        final_text += f"{segment['text']} "

                st.success("✅ تم بنجاح!")

                if "عرض" in output_format or "الاثنين" in output_format:
                    st.text_area("النص المستخرج:", value=final_text, height=400)

                if "تحميل" in output_format or "الاثنين" in output_format:
                    st.download_button(label="📥 تحميل النص (TXT)", data=final_text, file_name=f"transcript_{datetime.date.today()}.txt", mime="text/plain")

            if os.path.exists(audio_path):
                os.remove(audio_path)

        except Exception as e:
            st.error(f"حدث خطأ: {e}")

    if st.sidebar.button("تسجيل الخروج"):
        st.session_state["password_correct"] = False
        st.rerun()
