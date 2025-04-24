#!/usr/bin/env python
# coding: utf-8

import telebot
from telebot import types
from aliexpress_api import AliexpressApi, models
import re

# إعداد البوت باستخدام مفتاح API الصحيح
bot = telebot.TeleBot('7538639989:AAE6lQKTyL0F_8wKHKtuKx5m6hGXVdTOszo')  # استبدل بـ مفتاح API الخاص بك

# إعداد تكامل AliExpress API
aliexpress = AliexpressApi(
    '514274',       # استبدل بـ مفتاح التطبيق الخاص بك
    'kZ94O1p3er1qXL8zCo3AgZpWDxxH9Wzv',    # استبدل بـ المفتاح السري الخاص بك
    models.Language.EN,
    models.Currency.EUR,
    'default'
)

# الترحيب بالمستخدم عند بدء المحادثة
@bot.message_handler(commands=['start'])
def welcome_user(message):
    bot.send_message(
        message.chat.id,
        "مرحبًا بك! أرسل لنا رابط المنتج الذي تريد شراءه للحصول على تفاصيله."
    )

# استخراج الروابط من النصوص
def extract_link(text):
    link_pattern = r'https?://\S+|www\.\S+'
    links = re.findall(link_pattern, text)
    return links[0] if links else None

# الوظيفة الرئيسية لجلب تفاصيل المنتج وإرسالها للمستخدم
def get_affiliate_links(message, message_id, link):
    try:
        # الحصول على تفاصيل المنتج
        product_details = aliexpress.get_products_details([link])

        if product_details:
            # تفاصيل المنتج
            product_image = product_details[0].product_main_image_url  # الصورة الرئيسية للمنتج
            product_title = product_details[0].product_title           # اسم المنتج
            product_price = getattr(product_details[0], 'sale_price', 'غير متوفر')  # السعر

            # معلومات المتجر
            store_rating = getattr(product_details[0], 'evaluate_rate', 'لا يوجد تقييم متاح')  # تقييم المتجر
            store_name = getattr(product_details[0], 'shop_name', 'اسم المتجر غير متوفر')
            store_url = getattr(product_details[0], 'shop_url', 'رابط المتجر غير متوفر')

            # رابط الشراء
            affiliate_links = aliexpress.get_affiliate_links(link)
            affiliate_link = affiliate_links[0].promotion_link  # رابط التسويق

            # حذف الرسالة السابقة
            bot.delete_message(message.chat.id, message_id)

            # إرسال رسالة تحتوي على جميع التفاصيل
            caption = (
                f"📦 المنتج: {product_title}\n\n"
                f"💰 السعر: {product_price} دولار\n\n"
                f"🏬 المتجر: {store_name}\n\n"
                f"⭐️ تقييم المتجر: {store_rating}% تقييمات إيجابية\n\n"
                f"🔗 رابط المتجر: {store_url}\n\n"
                f"🔗 رابط الشراء: {affiliate_link}\n\n"
                "🌟 استمتع بالتسوق الآن!"
            )
            bot.send_photo(message.chat.id, product_image, caption=caption)
        else:
            bot.delete_message(message.chat.id, message_id)
            bot.send_message(message.chat.id, "❌ لم يتم العثور على بيانات المنتج.")
    except Exception as e:
        print(f"❌ خطأ: {e}")
        bot.delete_message(message.chat.id, message_id)
        bot.send_message(message.chat.id, "حدث خطأ أثناء معالجة الرابط. يرجى المحاولة مرة أخرى.")

# معالجة الرسائل التي تحتوي على روابط
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    link = extract_link(message.text)
    sent_message = bot.send_message(message.chat.id, "⏳ جاري معالجة الرابط...")
    message_id = sent_message.message_id

    if link and "aliexpress.com" in link:
        get_affiliate_links(message, message_id, link)
    else:
        bot.delete_message(message.chat.id, message_id)
        bot.send_message(message.chat.id, "❌ الرابط غير صحيح! يرجى إرسال رابط منتج صالح.")

# بدء تشغيل البوت
bot.infinity_polling(timeout=10, long_polling_timeout=5)