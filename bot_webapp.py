import requests
import time
import json

TOKEN = "8605127523:AAEfSS1SmxWuhKrOsJELYpBOsnjhYuZ2_sI"
ADMIN_ID = "7016438694"
API_URL = f"https://api.telegram.org/bot{TOKEN}/"

# رابط التطبيق المصغر الخاص بك
WEBAPP_URL = "https://hussein2001th-hub.github.io/order-app/webapp.html"

def set_bot_menu_button():
    """تعيين زر ثابت في أسفل المحادثة يفتح التطبيق المصغر مباشرة"""
    url = API_URL + "setChatMenuButton"
    payload = {
        "menu_button": {
            "type": "web_app",
            "text": "طلب جديد 📦",
            "web_app": {
                "url": WEBAPP_URL
            }
        }
    }
    try:
        res = requests.post(url, json=payload)
        print("Menu button set:", res.json())
    except Exception as e:
        print("Error setting menu button:", e)

def get_updates(offset=None):
    url = API_URL + "getUpdates"
    params = {'timeout': 5, 'offset': offset}
    try:
        response = requests.get(url, params=params)
        return response.json()
    except Exception as e:
        print("خطأ في الاتصال:", e)
        return {'result': []}

def send_message_with_webapp(chat_id, text):
    url = API_URL + "sendMessage"
    
    keyboard = {
        "inline_keyboard": [
            [
                {
                    "text": "📱 افتح تطبيق الطلبات",
                    "web_app": {"url": WEBAPP_URL}
                }
            ]
        ]
    }
    
    params = {
        'chat_id': chat_id, 
        'text': text, 
        'parse_mode': 'HTML',
        'reply_markup': keyboard
    }
    
    try:
        requests.post(url, json=params)
    except Exception as e:
        print("Error sending message:", e)

def send_message(chat_id, text):
    url = API_URL + "sendMessage"
    params = {'chat_id': chat_id, 'text': text, 'parse_mode': 'HTML'}
    try:
        requests.post(url, json=params)
    except Exception as e:
        print("خطأ في إرسال الرسالة:", e)

def handle_updates(updates):
    for update in updates.get('result', []):
        if 'message' in update:
            message = update['message']
            chat_id = str(message['chat']['id'])
            first_name = message['from'].get('first_name', 'مجهول')
            
            # 1. استلام بيانات من التطبيق المصغر (Web App)
            if 'web_app_data' in message:
                data_str = message['web_app_data']['data']
                try:
                    data = json.loads(data_str)
                    order_number = data.get('order_number')
                    location = data.get('location')
                    
                    # رسالة تأكيد للزبون
                    confirm_text = (
                        "✅ <b>تم استلام طلبك بنجاح!</b>\n\n"
                        f"🔢 <b>رقم الطلب:</b> {order_number}\n"
                        f"📍 <b>موقع الزبون:</b> {location}\n\n"
                        "شكراً لتعاملك معنا ❤️"
                    )
                    send_message(chat_id, confirm_text)
                    
                    # إشعار للمسؤول (الآيدي الخاص بك)
                    admin_msg = (
                        "🚨 <b>طلب جديد من التطبيق المصغر!</b> 🚨\n\n"
                        f"🔢 <b>رقم الطلب:</b> {order_number}\n"
                        f"📍 <b>الموقع:</b> {location}\n"
                        f"👤 <b>صاحب الطلب:</b> {first_name} (ID: <code>{chat_id}</code>)"
                    )
                    send_message(ADMIN_ID, admin_msg)
                        
                except Exception as e:
                    print("Error parsing WebApp data:", e)
                    send_message(chat_id, "❌ حدث خطأ أثناء معالجة بيانات الطلب.")
                    
            # 2. استلام الأوامر النصية العادية
            elif 'text' in message:
                text = message['text']
                if text.startswith('/start'):
                    send_message_with_webapp(chat_id, "مرحباً بك! 👋\nاضغط على الزر بالأسفل لفتح <b>التطبيق المصغر</b> وإرسال طلبك بكل سهولة:")

def main():
    print("جاري تهيئة البوت وتثبيت زر التطبيق المصغر...")
    set_bot_menu_button()
    print("البوت يعمل الآن ومستعد لاستقبال الطلبات!")
    last_update_id = None
    while True:
        updates = get_updates(last_update_id)
        if updates.get('result'):
            last_update_id = updates['result'][-1]['update_id'] + 1
            handle_updates(updates)
        time.sleep(1)

if __name__ == '__main__':
    main()
