import requests
import time

TOKEN = "8605127523:AAEfSS1SmxWuhKrOsJELYpBOsnjhYuZ2_sI"
ADMIN_ID = "7016438694"
API_URL = f"https://api.telegram.org/bot{TOKEN}/"

user_steps = {}
order_data = {}

def get_updates(offset=None):
    url = API_URL + "getUpdates"
    params = {'timeout': 5, 'offset': offset}
    try:
        response = requests.get(url, params=params)
        return response.json()
    except Exception as e:
        print("خطأ في الاتصال:", e)
        return {'result': []}

def send_message(chat_id, text):
    url = API_URL + "sendMessage"
    params = {'chat_id': chat_id, 'text': text, 'parse_mode': 'HTML'}
    try:
        requests.post(url, json=params)
    except Exception as e:
        print("خطأ في إرسال الرسالة:", e)

def handle_updates(updates):
    for update in updates.get('result', []):
        if 'message' in update and 'text' in update['message']:
            message = update['message']
            chat_id = str(message['chat']['id'])
            text = message['text']
            first_name = message['from'].get('first_name', 'مجهول')
            
            if text.startswith('/start'):
                send_message(chat_id, "مرحباً بك في بوت إدارة الطلبات! 📦\n\nلإضافة طلب جديد، أرسل /add_order")
            elif text.startswith('/add_order'):
                user_steps[chat_id] = 'wait_for_order_number'
                send_message(chat_id, "الرجاء إدخال <b>رقم الطلب</b>:")
            elif user_steps.get(chat_id) == 'wait_for_order_number':
                order_data[chat_id] = {'order_number': text}
                user_steps[chat_id] = 'wait_for_location'
                send_message(chat_id, "الرجاء إدخال <b>موقع الزبون</b>:")
            elif user_steps.get(chat_id) == 'wait_for_location':
                location = text
                order_number = order_data[chat_id]['order_number']
                
                # مسح حالة المستخدم
                user_steps[chat_id] = None
                
                # إرسال تأكيد للمستخدم
                send_message(chat_id, f"✅ تم حفظ الطلب بنجاح!\n\nرقم الطلب: {order_number}\nموقع الزبون: {location}")
                
                # إرسال إشعار للمسؤول
                admin_msg = f"🚨 <b>طلب جديد وصل!</b> 🚨\n\n🔹 رقم الطلب: {order_number}\n📍 موقع الزبون: {location}\n👤 أضيف بواسطة: {first_name}"
                if chat_id != ADMIN_ID:
                    send_message(ADMIN_ID, admin_msg)
                
                send_message(chat_id, "لإضافة طلب آخر أرسل /add_order")

def main():
    print("تم تشغيل البوت بنجاح! يعمل الآن في الخلفية...")
    last_update_id = None
    while True:
        updates = get_updates(last_update_id)
        if updates.get('result'):
            last_update_id = updates['result'][-1]['update_id'] + 1
            handle_updates(updates)
        time.sleep(1)

if __name__ == '__main__':
    main()
