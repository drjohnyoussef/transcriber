import streamlit as st
import yt_dlp
import whisper
import os
import datetime

st.set_page_config(page_title="المفرغ الذكي", page_icon="🎙️")

# --- نظام الحماية ---
if "password_correct" not in st.session_state:
    st.session_state["password_correct"] = False

if not st.session_state["password_correct"]:
    st.title("🔒 الدخول محمي")
    password = st.text_input("أدخل الرمز السري:", type="password")
    if st.button("دخول"):
        if password == "777@jo":
            st.session_state["password_correct"] = True
            st.rerun()
        else:
            st.error("❌ الرمز السري غير صحيح!")
    st.stop()

# --- البرنامج الرئيسي ---
st.title("🎙️ المحول الشامل")
input_source = st.radio("المصدر:", ["رابط من الإنترنت", "رفع ملف"])

video_url = ""
uploaded_file = None

if input_source == "رابط من الإنترنت":
    video_url = st.text_input("ضع الرابط هنا:")
else:
    uploaded_file = st.file_uploader("اختر ملف:", type=["mp4", "m4a", "mp3", "mov", "wav"])

show_timestamps = st.checkbox("عرض التوقيت؟", value=True)

if st.button("🚀 ابدأ"):
    try:
        with st.spinner("⏳ جارٍ التجهيز..."):
            if input_source == "رابط من الإنترنت" and video_url:
                ydl_opts = {'format': 'm4a/bestaudio/best', 'outtmpl': 'temp_audio', 'quiet': True}
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([video_url])
                audio_path = "temp_audio.m4a"
            elif input_source == "رفع ملف" and uploaded_file:
                with open("temp_upload", "wb") as f:
                    f.write(uploaded_file.getbuffer())
                audio_path = "temp_upload"
            else:
                st.warning("أدخل بيانات!")
                st.stop()

        with st.spinner("🧠 الذكاء الاصطناعي يكتب (نسخة خفيفة)..."):
            # التعديل الجوهري هنا: استخدام base بدلاً من medium
            model = whisper.load_model("base") 
            result = model.transcribe(audio_path)

            final_text = ""
            for segment in result['segments']:
                if show_timestamps:
                    start = str(datetime.timedelta(seconds=int(segment['start'])))
                    final_text += f"[{start}] {segment['text']}\n"
                else:
                    final_text += f"{segment['text']} "

            st.success("✅ تم!")
            st.text_area("النص:", value=final_text, height=300)
            
            st.download_button("📥 تحميل النص", final_text, file_name="transcript.txt")
            
            if os.path.exists(audio_path): os.remove(audio_path)

    except Exception as e:
        st.error(f"⚠️ حصلت مشكلة تقنية: {e}")
