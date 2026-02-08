import streamlit as st
import yt_dlp
import whisper
import os
import datetime
import gc 

st.set_page_config(page_title="المفرغ الذكي - الدقة القصوى", page_icon="💎")

# --- نظام الحماية ---
if "password_correct" not in st.session_state:
    st.session_state["password_correct"] = False

if not st.session_state["password_correct"]:
    st.title("🔒 الدخول محمي")
    password = st.text_input("أدخل الرمز السري:", type="password", placeholder="777@jo")
    if st.button("دخول"):
        if password == "777@jo":
            st.session_state["password_correct"] = True
            st.rerun()
        else:
            st.error("❌ الرمز السري غير صحيح!")
    st.stop()

# --- البرنامج الرئيسي ---
st.title("💎 تفريغ نصي بأعلى دقة (Medium Model)")
st.info("ملاحظة: الموديل الدقيق قد يستغرق وقتاً أطول قليلاً في المعالجة للحصول على أفضل نتيجة.")

input_source = st.radio("اختر مصدر الصوت:", ["رابط من الإنترنت", "رفع ملف من الجهاز"])
video_url = st.text_input("ضع الرابط هنا:") if input_source == "رابط من الإنترنت" else None
uploaded_file = st.file_uploader("اختر ملف الفيديو/الصوت:", type=["mp4", "m4a", "mp3", "mov", "wav"]) if input_source == "رفع ملف من الجهاز" else None

show_timestamps = st.checkbox("عرض التوقيت الزمني؟", value=True)

if st.button("🚀 ابدأ المعالجة الاحترافية"):
    audio_path = "pro_audio.m4a"
    try:
        with st.spinner("⏳ جارٍ تجهيز الملف بأفضل جودة..."):
            if input_source == "رابط من الإنترنت" and video_url:
                ydl_opts = {'format': 'bestaudio/best', 'outtmpl': 'pro_audio.%(ext)s', 'quiet': True}
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(video_url, download=True)
                    audio_path = ydl.prepare_filename(info)
            elif input_source == "رفع ملف من الجهاز" and uploaded_file:
                audio_path = "uploaded_pro.m4a"
                with open(audio_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
            else:
                st.warning("برجاء إدخال الرابط أو الملف!")
                st.stop()

        with st.spinner("🧠 الذكاء الاصطناعي يحلل الكلام (الموديل الدقيق جداً)..."):
            # استخدام موديل Medium لضمان أدق كلام
            model = whisper.load_model("medium")
            
            # إجبار الموديل على معالجة اللغة العربية بدقة عالية
            # beam_size=5 يحسن الدقة بشكل كبير جداً في الكلمات الصعبة
            result = model.transcribe(audio_path, language="ar", beam_size=5)

            final_text = ""
            for segment in result['segments']:
                if show_timestamps:
                    start = str(datetime.timedelta(seconds=int(segment['start'])))
                    final_text += f"[{start}] {segment['text']}\n"
                else:
                    final_text += f"{segment['text']} "

            st.success("✅ تم استخراج النص بأعلى دقة ممكنة!")
            st.text_area("النص الناتج:", value=final_text, height=400)
            st.download_button("📥 تحميل النص النهائي", final_text, file_name=f"perfect_transcript.txt")

            # إجراءات أمان للسيرفر: مسح الموديل من الرام فوراً
            del model
            gc.collect() 
            if os.path.exists(audio_path): os.remove(audio_path)

    except Exception as e:
        if "Out of memory" in str(e):
            st.error("⚠️ الفيديو طويل جداً على السيرفر المجاني بالدقة القصوى. جرب فيديو أقصر أو اطلب مني تقليل الدقة قليلاً.")
        else:
            st.error(f"⚠️ حدث خطأ: {e}")
