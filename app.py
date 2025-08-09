import streamlit as st
import pandas as pd
from datetime import datetime
import sqlite3

       # تعریف وزن‌ها
WEIGHTS = {
           "عوامل مربوط به منبع روشنایی": 0.30,
           "ویژگی‌های محیط": 0.20,
           "منبع روشنایی طبیعی": 0.15,
           "عوامل فردی": 0.10,
           "عوامل مربوط به کار": 0.10,
           "ایمنی منابع": 0.05,
           "خیرگی و فلیکر": 0.05,
           "تأثیرات زیستی و بازده انرژی": 0.05
       }

       # تعریف استانداردها
STANDARDS = {
           "کار دفتری": {"min_lux": 300, "optimal_lux": 500, "max_lux": 750}
       }

       # تابع دسته‌بندی نمره
def categorize_score(score):
           if 0 <= score <= 20: return "بسیار نامطلوب (نیاز فوری)"
           elif 20 < score <= 40: return "نامطلوب (بازنگری جدی)"
           elif 40 < score <= 60: return "متوسط (بهبود لازم)"
           elif 60 < score <= 80: return "مطلوب (نظارت)"
           else: return "بسیار مطلوب (استاندارد)"

def calculate_category_score(answers):
           return sum(answers) / len(answers) if answers else 0

def save_to_database(final_score, rank, mean_lux, recommendation):
           conn = sqlite3.connect('lighting_database.db')
           cursor = conn.cursor()
           cursor.execute('''
               CREATE TABLE IF NOT EXISTS assessments (
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   date_time TEXT,
                   final_score REAL,
                   rank TEXT,
                   mean_lux REAL,
                   recommendation TEXT
               )
           ''')
           cursor.execute('''
               INSERT INTO assessments (date_time, final_score, rank, mean_lux, recommendation)
               VALUES (?, ?, ?, ?, ?)
           ''', (datetime.now().strftime('%Y-%m-%d %H:%M'), final_score, rank, mean_lux, recommendation))
           conn.commit()
           conn.close()

       # رابط گرافیکی
st.title("ابزار ارزیابی پیشرفته روشنایی")

       # ورودی روشنایی
lux_input = st.text_input("مقادیر روشنایی (لوکس، با کاما جدا کنید)", "300, 450, 500")
lux_data = [float(x) for x in lux_input.split(",") if x.strip()]
compliance = {"mean_lux": 0, "recommendation": ""}
if lux_data:
           compliance["mean_lux"] = sum(lux_data) / len(lux_data)
           std = STANDARDS["کار دفتری"]
           if compliance["mean_lux"] < std["min_lux"]:
               compliance["recommendation"] = f"روشنایی کمتر از حد استاندارد است ({std['min_lux']} لوکس)."
           elif compliance["mean_lux"] > std["max_lux"]:
               compliance["recommendation"] = f"روشنایی بیش از حد استاندارد است ({std['max_lux']} لوکس)."
           else:
               compliance["recommendation"] = "روشنایی در محدوده استاندارد است."

       # چک‌لیست
categories = {
           "عوامل مربوط به منبع روشنایی": [
               "دمای رنگ (K) (4000-4500K=10، 3500-4000K=7، 4500-6500K=8، <3000K=0)",
               "شاخص تجلی رنگ (CRI) (≥90=10، 80-90=8، 70-80=5، <70=0)",
               "ضریب بهره نوری (≥100=10، 80-100=8، 50-80=5، <50=0)",
               "نوع منبع (LED=10، فلورسنت=7، هالوژن=4، لامپ رشته‌ای=0)",
               "یکنواختی روشنایی (≥0.7=10، 0.5-0.7=6، <0.5=0)"
           ],
           "ویژگی‌های محیط": [
               "ضرایب انعکاس (دیوار 0.5-0.7، سقف 0.7-0.9، کف 0.2-0.4=10، خارج=0)",
               "تمیزی محیط (هفتگی=10، ماهانه=6، سالانه=2، هرگز=0)",
               "موانع نوری (بدون=10، متوسط=5، زیاد=0)"
           ],
           "منبع روشنایی طبیعی": [
               "تعداد پنجره‌ها (0=0، 1=3، 2=6، 3-4=8، ≥5=10)",
               "جهت‌گیری پنجره (شمالی=10، شرقی/غربی=7، جنوبی=5)",
               "کنترل نور طبیعی (کامل=10، جزئی=5، بدون=0)"
           ],
           "عوامل فردی": [
               "میانگین سن (<30=10، 30-50=7، 50-65=5، >65=3)",
               "مشکلات بینایی (<5%=10، 5-20%=7، 20-40%=4، >40%=0)",
               "ترجیحات شخصی (کامل=10، نسبی=6، بدون=0)"
           ],
           "عوامل مربوط به کار": [
               "نوع کار (دقیق=10، عمومی=7، دستی=4، نامطابق=0)",
               "روشنایی مورد نیاز (300-500 لوکس=10، 200-300=7، <200=0)",
               "مدت زمان کار (<4 ساعت=10، 4-8 ساعت=7، >8 ساعت=4)"
           ],
           "ایمنی منابع": [
               "ایمنی الکتریکی (کامل=10، نسبی=5، غیرایمن=0)",
               "خطر آتش‌سوزی (بدون=10، متوسط=5، بالا=0)",
               "سیستم اضطراری (کامل=10، جزئی=5، بدون=0)"
           ],
           "خیرگی و فلیکر": [
               "شاخص خیرگی (UGR<19=10، 19-22=6، 22-28=3، >28=0)",
               "فلیکر (بدون=10، کم=7، متوسط=4، شدید=0)"
           ],
           "تأثیرات زیستی و بازده انرژی": [
               "تأثیر ریتم شبانه‌روزی (بهینه=10، قابل قبول=7، نامناسب=0)",
               "بازده انرژی (≥100 لومن/وات=10، 80-100=8، 50-80=5، <50=0)"
           ]
       }

entry_fields = {}
for category, questions in categories.items():
           with st.expander(category):
               entry_fields[category] = [st.number_input(q, min_value=0.0, max_value=10.0, step=0.1) for q in questions]

       # دکمه ارزیابی
if st.button("ارزیابی"):
           report_data = []
           total_score = 0
           for category, entries in entry_fields.items():
               scores = [float(entry) for entry in entries]
               category_score = calculate_category_score(scores)
               weighted_score = category_score * WEIGHTS[category]
               total_score += weighted_score
               report_data.append({
                   "دسته": category,
                   "میانگین نمره": round(category_score, 2),
                   "وزن": WEIGHTS[category],
                   "نمره وزنی": round(weighted_score, 2)
               })

           final_score = total_score * 10
           rank = categorize_score(final_score)

           report_data.append({"دسته": "نمره کل", "میانگین نمره": round(final_score, 2), "وزن": "", "نمره وزنی": ""})
           report_data.append({"دسته": "رتبه‌بندی", "میانگین نمره": rank, "وزن": "", "نمره وزنی": ""})
           if lux_data:
               report_data.append({
                   "دسته": "میانگین روشنایی (لوکس)",
                   "میانگین نمره": round(compliance["mean_lux"], 2),
                   "وزن": "",
                   "نمره وزنی": compliance["recommendation"]
               })

           save_to_database(final_score, rank, compliance["mean_lux"] if lux_data else None, compliance["recommendation"])

           st.write("### نتایج ارزیابی")
           for row in report_data:
               st.write(f"{row['دسته']}: {row['میانگین نمره']}")
               if row["وزن"]:
                   st.write(f"  (وزن: {row['وزن']})")
               if row["نمره وزنی"]:
                   st.write(f"  -> نمره وزنی: {row['نمره وزنی']}")

           conn = sqlite3.connect('lighting_database.db')
           all_reports = pd.read_sql_query("SELECT * FROM assessments", conn)
           if not all_reports.empty:
               avg_score = all_reports["final_score"].mean()
               st.write(f"### آمار کلی")
               st.write(f"میانگین نمرات کل: {round(avg_score, 2)}")
           conn.close()