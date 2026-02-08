import streamlit as st
import yt_dlp
import whisper
import os
import datetime

# إعدادات الصفحة
st.set_page_config(page_title="المفرغ الذكي الشامل", page_icon="🎙️")

# --- نظام الحماية ---
if "password_correct" not in st.session_state:
    st.session_state["password_correct"] = False

if not st.session_state["password_correct"]:
    st.title("🔒 الدخول محمي")
    password = st.text_input("أدخل الرمز السري:", type="password", placeholder="Password Required")
    if st.button("دخول"):
        if password == "777@jo":
            st.session_state["password_correct"] = True
            st.rerun()
        else:
            st.error("❌ الرمز السري غير صحيح!")
    st.stop()

# --- واجهة البرنامج الرئيسية ---
st.title("🎙️ المحول الشامل")

input_source = st.radio("اختر مصدر الصوت:", ["رابط من الإنترنت", "رفع ملف من الجهاز"])

video_url = ""
uploaded_file = None

if input_source == "رابط من الإنترنت":
    video_url = st.text_input("ضع الرابط هنا:")
else:
    uploaded_file = st.file_uploader("اختر ملف:", type=["mp4", "m4a", "mp3", "mov", "wav"])

show_timestamps = st.checkbox("عرض التوقيت الزمني؟", value=True)

if st.button("🚀 ابدأ المعالجة"):
    # سنستخدم اسماً بسيطاً جداً للملف لتجنب مشاكل الـ arguments
    audio_path = "audio_file.mp3"
    
    try:
        with st.spinner("⏳ جارٍ تجهيز الملف الصوتي..."):
            if input_source == "رابط من الإنترنت" and video_url:
                # إعدادات تحميل مبسطة جداً لتجنب خطأ الـ Postprocessing
                ydl_opts = {
                    'format': 'bestaudio/best',
                    'outtmpl': 'audio_file.%(ext)s', # نترك الامتداد للأصل أولاً
                    'quiet': True,
                }
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(video_url, download=True)
                    # الحصول على المسار الحقيقي للملف الذي تم تحميله
                    downloaded_file = ydl.prepare_filename(info)
                    audio_path = downloaded_file
            
            elif input_source == "رفع ملف من الجهاز" and uploaded_file:
                audio_path = "uploaded_audio.mp3"
                with open(audio_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
            else:
                st.warning("برجاء إدخال البيانات!")
                st.stop()

        # التحقق وبدء المعالجة
        if not os.path.exists(audio_path):
            st.error("❌ تعذر العثور على الملف المحمل.")
        else:
            with st.spinner("🧠 الذكاء الاصطناعي يحلل الكلام..."):
                model = whisper.load_model("base")
                result = model.transcribe(audio_path)

                final_text = ""
                for segment in result['segments']:
                    if show_timestamps:
                        start = str(datetime.timedelta(seconds=int(segment['start'])))
                        final_text += f"[{start}] {segment['text']}\n"
                    else:
                        final_text += f"{segment['text']} "

                st.success("✅ تم الانتهاء!")
                st.text_area("النص المستخرج:", value=final_text, height=350)
                st.download_button("📥 تحميل النص", final_text, file_name="transcript.txt")

        # تنظيف الملفات
        if os.path.exists(audio_path):
            os.remove(audio_path)

    except Exception as e:
        st.error(f"⚠️ حدث خطأ تقني: {e}")

if st.sidebar.button("تسجيل الخروج"):
    st.session_state["password_correct"] = False
    st.rerun()
