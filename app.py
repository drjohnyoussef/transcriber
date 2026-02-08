import streamlit as st
import yt_dlp
import whisper
import os
import datetime
import gc 

st.set_page_config(page_title="المفرغ الذكي - الدقة القصوى", page_icon="💎")

# --- نظام الحماية (بدون هينت) ---
if "password_correct" not in st.session_state:
    st.session_state["password_correct"] = False

if not st.session_state["password_correct"]:
    st.title("🔒 الدخول محمي")
    # تم إزالة الـ placeholder تماماً بناءً على طلبك
    password = st.text_input("أدخل الرمز السري:", type="password")
    if st.button("دخول"):
        if password == "777@jo":
            st.session_state["password_correct"] = True
            st.rerun()
        else:
            st.error("❌ الرمز السري غير صحيح!")
    st.stop()

# --- واجهة البرنامج ---
st.title("💎 مفرغ النصوص الاحترافي")
st.info("هذه النسخة تعمل بأعلى دقة ممكنة (Medium Model).")

input_source = st.radio("مصدر الصوت:", ["رابط من الإنترنت", "رفع ملف"])
video_url = st.text_input("الرابط:") if input_source == "رابط من الإنترنت" else None
uploaded_file = st.file_uploader("الملف:", type=["mp4", "m4a", "mp3", "mov", "wav"]) if input_source == "رفع ملف" else None

show_timestamps = st.checkbox("عرض التوقيت الزمني؟", value=True)

if st.button("🚀 ابدأ المعالجة"):
    audio_path = "pro_audio.m4a"
    try:
        with st.spinner("⏳ جارٍ تجهيز الملف..."):
            if input_source == "رابط من الإنترنت" and video_url:
                ydl_opts = {'format': 'bestaudio/best', 'outtmpl': 'pro_audio.%(ext)s', 'quiet': True}
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(video_url, download=True)
                    audio_path = ydl.prepare_filename(info)
            elif input_source == "رفع ملف" and uploaded_file:
                audio_path = "uploaded_pro.m4a"
                with open(audio_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
            else:
                st.warning("أدخل البيانات أولاً!")
                st.stop()

        with st.spinner("🧠 ذكاء اصطناعي فائق (Medium) يكتب الآن..."):
            model = whisper.load_model("medium")
            # استخدام أعلى معايير الدقة
            result = model.transcribe(audio_path, language="ar", beam_size=5)

            final_text = ""
            for segment in result['segments']:
                if show_timestamps:
                    start = str(datetime.timedelta(seconds=int(segment['start'])))
                    final_text += f"[{start}] {segment['text']}\n"
                else:
                    final_text += f"{segment['text']} "

            st.success("✅ اكتملت المهمة بأعلى دقة!")
            st.text_area("النص المستخرج:", value=final_text, height=400)
            st.download_button("📥 تحميل ملف النص", final_text, file_name="perfect_transcript.txt")

            # تفريغ الذاكرة فوراً
            del model
            gc.collect() 
            if os.path.exists(audio_path): os.remove(audio_path)

    except Exception as e:
        st.error(f"⚠️ حدث خطأ: {e}")
