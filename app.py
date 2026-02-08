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
    # تم تغيير الباسورد لـ 777@jo وإخفاء الهينت
    password = st.text_input("أدخل الرمز السري:", type="password", placeholder="Password Required")
    if st.button("دخول"):
        if password == "777@jo":
            st.session_state["password_correct"] = True
            st.rerun()
        else:
            st.error("❌ الرمز السري غير صحيح!")
    st.stop()

# --- واجهة البرنامج الرئيسية ---
st.title("🎙️ المحول الشامل (روابط + ملفات)")
st.write("يدعم YouTube, Vimeo, Facebook، أو رفع ملفات من موبايلك.")

# خيارات الإدخال
input_source = st.radio("اختر مصدر الصوت:", ["رابط من الإنترنت", "رفع ملف من الجهاز"])

video_url = ""
uploaded_file = None

if input_source == "رابط من الإنترنت":
    video_url = st.text_input("ضع الرابط هنا:", placeholder="https://...")
else:
    uploaded_file = st.file_uploader("اختر ملف فيديو أو صوت:", type=["mp4", "m4a", "mp3", "mov", "wav"])

st.divider()

# خيارات العرض
show_timestamps = st.checkbox("عرض التوقيت الزمني (00:00)؟", value=True)

if st.button("🚀 ابدأ المعالجة"):
    audio_path = "final_audio.mp3"
    
    try:
        # 1. مرحلة سحب أو تجهيز الصوت
        with st.spinner("⏳ جارٍ تجهيز الملف الصوتي..."):
            if input_source == "رابط من الإنترنت" and video_url:
                ydl_opts = {
                    'format': 'bestaudio/best',
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    }],
                    'outtmpl': 'final_audio', 
                    'quiet': True,
                }
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([video_url])
            
            elif input_source == "رفع ملف من الجهاز" and uploaded_file:
                with open(audio_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
            else:
                st.warning("برجاء إدخال الرابط أو الملف أولاً!")
                st.stop()

        # 2. التأكد من وجود الملف وبدء الكتابة
        if not os.path.exists(audio_path):
            st.error("❌ فشل في معالجة الملف الصوتي، تأكد من صحة الرابط.")
        else:
            with st.spinner("🧠 الذكاء الاصطناعي يحلل الكلام (موديل Base السريع)..."):
                # استخدام الموديل المتوافق مع مساحة السيرفر المجانية
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

                # 3. العرض والتحميل معاً
                st.write("### النص المستخرج:")
                st.text_area("", value=final_text, height=350)

                st.download_button(
                    label="📥 تحميل النص كملف TXT",
                    data=final_text,
                    file_name=f"transcript_{datetime.date.today()}.txt",
                    mime="text/plain"
                )

        # تنظيف الذاكرة وحذف الملف المؤقت
        if os.path.exists(audio_path):
            os.remove(audio_path)

    except Exception as e:
        st.error(f"⚠️ حدث خطأ تقني: {e}")

# تسجيل الخروج في القائمة الجانبية
if st.sidebar.button("تسجيل الخروج"):
    st.session_state["password_correct"] = False
    st.rerun()
