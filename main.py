import json
import random
import time
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import requests
import threading
from pymino import Bot
from pymino.ext import Context
import openai
import os
import json
import uuid
import re
import list




# Constants
COOLDOWN_FILE = 'cooldown_history.json'
ACCOUNTS_FILE = 'bank_accounts.json'
LISTS_FILE = 'list.json'
SAVED_CHATS_FILE = 'saved_chats.json'
filename = 'bank_accounts.json'     
# OpenAI setup


# Bot setup
bot = Bot(
    service_key="Y2U0ZmNhOWI3YzYzMDFhOQ==",
    device_key="E7309ECC0953C6FA60005B2765F99DBBC965C8E9",
    signature_key="DFA5ED192DDA6E88A12FE12130DC6206B1251E44",
    command_prefix="/",
    community_id="3434136"
)



stocks = [
    {"id": "A", "name": "𝐀 ⧼ 𝐒𝐚𝐦𝐬𝐮𝐧𝐠 ", "price": random.randint(200, 500)},
    {"id": "B", "name": "𝐁 ⧼ 𝐀𝐥𝐤𝐡𝐭𝐲𝐛 ", "price": random.randint(200, 500)},
    {"id": "C", "name": "𝐂 ⧼ 𝐙𝐚𝐢𝐧 𝐢𝐧𝐜", "price": random.randint(200, 500)}
]

CARD_INFO = {
    'WHITE': {'image': 'white.png'},
    'BLUE': {'image': 'blue.png'},
    'BLACK': {'image': 'black.png'},
    'VIP': {'image': 'vip.png'}
}

marriage_proposals = {}
cooldowns = {}
user_stocks = {}
confirmation_list = []
commands_enabled = True
view_only_state = {}

price_update_interval = 360  # 5 minutes
last_price_update_time = time.time()
commands_enabled = True
# Load data
# Helper functions
# Example usage function


def save_lists():
    with open('list.json', 'w') as f:
        json.dump(lists, f, indent=4)

def create_circular_image(image_path, size):
    image = Image.open(image_path).convert("RGBA")
    image = image.resize(size, Image.LANCZOS)
    mask = Image.new('L', size, 0)
    draw = ImageDraw.Draw(mask)
    width, height = size
    draw.ellipse((0, 0, width, height), fill=255)
    circular_image = Image.new('RGBA', size)
    circular_image.paste(image, (0, 0), mask)
    return circular_image

def update_stock_prices():
    global last_price_update_time
    global last_price_update
    while True:
        time.sleep(price_update_interval)
        for stock in stocks:
            stock['price'] = random.randint(200, 500)
        last_price_update_time = time.time()
        last_price_update = time.time()
        
        # Reset purchase counts for all users
        for account in accounts:
            account['purchase_count'] = 0  


def load_json(filename):
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as file:
            return json.load(file)
    return {}

def save_json(filename, data):
    with open(filename, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

def get_cooldown_remaining(user_id, command, cooldown_period):
    current_time = time.time()
    if user_id in cooldown_history and command in cooldown_history[user_id]:
        last_used = cooldown_history[user_id][command]
        remaining_time = cooldown_period - (current_time - last_used)
        if remaining_time > 0:
            return remaining_time
    return 0

def update_cooldown(user_id, command):
    current_time = time.time()
    if user_id not in cooldown_history:
        cooldown_history[user_id] = {}
    cooldown_history[user_id][command] = current_time
    save_json(COOLDOWN_FILE, cooldown_history)


def start_chat(ctx, message, account_info):
    try:
        response = bot.make_request(
            method="POST",
            url="https://service.aminoapps.com/api/v1/x3434136/s/chat/thread",
            data={
                "type": 0,
                "inviteeUids": [ctx.author.uid],
                "initialMessageContent": message,
                "timestamp": int(time.time() * 1000)
            }
        )

        if response.get('api:statuscode') == 0 and response.get('api:message') == "OK":
            ctx.replay('تم بدء الدردشة بنجاح')
        elif "This user has disabled chat invite requests" in response.get('api:message', ''):
            print("This user has disabled chat invite requests.")
            ctx.reply("الرجاء فتح طلبات الدردشة أولاً ثم المحاولة مرة أخرى.")
        else:
            print(f"Failed to start chat. Response: {response}")
            ctx.reply("حدث خطأ ما أثناء محاولة بدء الدردشة. يرجى المحاولة مرة أخرى في وقت لاحق.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        if "This user has disabled chat invite requests" in str(e):
            ctx.reply("الرجاء فتح طلبات الدردشة أولاً ثم المحاولة مرة أخرى.")
        else:
            ctx.reply("حدث خطأ ما أثناء محاولة بدء الدردشة. يرجى المحاولة مرة أخرى في وقت لاحق.")

def load_accounts(filename):
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_accounts(filename, accounts):
    with open(filename, 'w') as f:
        json.dump(accounts, f, indent=4)

def determine_card_info(balance):
    if balance < 100_000_000:
        return CARD_INFO['BLUE']
    elif balance < 200_000_000_000:
        return CARD_INFO['WHITE']
    else:
        return CARD_INFO['BLACK']

def is_married(user_account):
    partner_roles = user_account.get('partner', {}).keys()
    return any(role in partner_roles for role in ["husband"])

def upload_sticker(ctx, filepath):
    try:
        response = bot.request.handler(
            method="POST",
            url="https://service.aminoapps.com/api/v1/g/s/media/upload/target/sticker",
            data=open(filepath, "rb").read(),
            content_type="image/jpg"
        )

        if 'mediaValue' not in response:
            ctx.reply("فشل تحميل الصورة. يرجى المحاولة مرة أخرى.")
            return

        link = response["mediaValue"]
        response = bot.make_request(
            method="POST",
            url=f"https://service.aminoapps.com/api/v1/x3434136/s/sticker-collection/c01e10b0-725b-45b9-b458-6cea65798ae0",
            data={
                "collectionType": 3,
                "description": "",
                "iconSourceStickerIndex": 0,
                "name": "Cards",
                "stickerList": [
                    {
                        "name": "Test",
                        "stickerId": "5a66e68f-c8cb-42d8-88d1-5c1ce423ddfc",
                        "icon": "http://st1.aminoapps.com/9075/4830880be5e5b7c88eecc7a3fee5a274bde2434ar6-256-256_00.jpeg"
                    },
                    {
                        "name": ctx.author.uid,
                        "icon": link
                    }
                ],
                "timestamp": int(time.time() * 1000)
            }
        )
        if 'stickerCollection' not in response:
            ctx.reply("فشل إنشاء ملصق. يرجى المحاولة مرة أخرى.")
            return

        stickerId = response["stickerCollection"]["stickerList"][1]["stickerId"]
        ctx.send_sticker(sticker_id=stickerId)
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        ctx.reply("حدث خطأ أثناء تحميل الصورة. يرجى المحاولة مرة أخرى لاحقًا.")

def generate_stocks():
    return str(random.randint(1000, 9999))

def create_account(accounts, ctx):
    for account in accounts:
        if account['uid'] == ctx.author.uid:
            ctx.reply(f"المستخدم '{ctx.author.username}' لديه حساب بالفعل.")
            return None

    try:
        initial_deposit = 0
        card_info = determine_card_info(initial_deposit)
        account_info = {
            'uid': ctx.author.uid,
            'username': ctx.author.username,
            'money': initial_deposit,
            'stocks': {},
            'card_image': card_info['image'],
            "stolen_money": 0,
            "partner": {}
        }
        accounts.append(account_info)
        save_accounts(ACCOUNTS_FILE, accounts)
        return account_info
    except Exception as e:
        print(f"An error occurred while creating account: {str(e)}")
        ctx.reply('حدث خطأ أثناء إنشاء الحساب. يرجى المحاولة مرة أخرى لاحقًا.')
        return None

def load_lists():
    try:
        with open(LISTS_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {"vip": ["efd2a89d-5b  ac0-4d66-a7d3-ecb456f3c079", "0d15d0a5-ca38-4cdf-8fd3-0ad0dc838414", "a29490cd-b8b1-46c2-a341-63c5278d80c2"], "blacklist": []}

def save_lists():
    with open(LISTS_FILE, 'w') as f:
        json.dump(lists, f, indent=4)

def is_blacklisted(user_id):
    return user_id in lists["blacklist"]

def is_vip(user_id):
    return user_id in lists["vip"]

def command_check(ctx: Context):
    if is_blacklisted(ctx.author.userId):
        bot.community.delete_message(chatId=ctx.chatId, messageId=ctx.message.messageId)
        return False

    if not commands_enabled:
        ctx.reply("تم تعطيل جميع الأوامر حالياً.")
        return False
    return True
def view_only(ctx):
    current_state = view_only_state.get(ctx.chatId, False)
    new_state = not current_state
    # Set new view-only state
    bot.community.set_view_only(chatId=ctx.chatId, viewOnly=new_state)
    # Update the state dictionary 
    view_only_state[ctx.chatId] = new_state
    return new_state
def resize_image(image_path, new_size=(1000, 600)):
    try:
        image = Image.open(image_path)
        resized_image = image.resize(new_size, Image.Resampling.LANCZOS)
        resized_image.save(image_path)
    except Exception as e:
        print(f"Error resizing image {image_path}: {e}")

def download_image(url, save_path):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            image = Image.open(BytesIO(response.content))
            image.save(save_path)
        else:
            print(f"Failed to download image from {url}")
    except Exception as e:
        print(f"Error downloading image from {url}: {e}")
def handle_confirmation(ctx, confirmation_list, accounts):
    user_id = ctx.author.userId
    confirmed = False

    for transfer in confirmation_list:
        if transfer['user1_id'] == user_id:
            user1_account = next((account for account in accounts if account['uid'] == user_id), None)
            user2_account = next((account for account in accounts if account['uid'] == transfer['user2_id']), None)
            
            if transfer['confirmed']:
                ctx.reply("هذه العملية قد تمت بالفعل.")
                return

            if user1_account and user2_account:
                if user1_account['money'] >= transfer['amount']:
                    user1_account['money'] -= transfer['amount']
                    user2_account['money'] += transfer['amount']
                    transfer['confirmed'] = True
                    confirmed = True
                    ctx.reply("تمت عملية التحويل بنجاح.")
                    save_accounts(filename,accounts)
                    confirmation_list.remove(transfer)
                else:
                    ctx.reply("لا يوجد رصيد كافي لإتمام عملية التحويل.")
                    return
    
    if not confirmed:
        ctx.reply("لم يتم العثور على عملية تحويل تنتظر التأكيد منك.")

  
cooldown_history = load_json(COOLDOWN_FILE)
accounts = load_accounts(ACCOUNTS_FILE)
lists = load_lists()
price_update_thread = threading.Thread(target=update_stock_prices, daemon=True)
price_update_thread.start()
@bot.on_text_message()

def on_text_message(ctx: Context, message: str):
    try:
        if is_blacklisted(ctx.author.userId):
            bot.community.delete_message(chatId=ctx.chatId, messageId=ctx.message.messageId)
            return
        user_id = ctx.author.userId
        if message.startswith('all'):
            if is_vip(ctx.author.userId):
                if not commands_enabled:
                    ctx.reply("تم تعطيل جميع الأوامر حالياً.")
                else:
                    chat_members_response = bot.community.fetch_chat_members(chatId=ctx.chatId, size=1000).json()
                    if 'memberList' in chat_members_response:
                        member_list = chat_members_response['memberList']
                        user_ids = [member['uid'] for member in member_list]
                        ctx.reply(content='\u200e\u200f@all\u202c\u202d',mentioned=user_ids)
                    else:
                        print("No memberList found in the response.")
        
        elif message.startswith('أسهمي'):
            user_account = next((account for account in accounts if account['uid'] == user_id), None)
            if user_account:
                user_stocks_data = user_account.get('stocks', {})
                if user_stocks_data:
                    stock_names = ', '.join([stock['name'] for stock in stocks if stock['id'] in user_stocks_data])
                    ctx.reply(f"⇜ أسهمك: {stock_names} ({user_stocks_data})")
                else:
                    ctx.reply("⇜ لا تملك أسهم.")
            else:
                 create_account(accounts=accounts, ctx=ctx)
        elif message.startswith('سطر'):
            if is_vip(ctx.author.userId):
                if not commands_enabled:
                    ctx.reply("تم تعطيل جميع الأوامر حالياً.")
                else:
                    ctx.send(content=list.mel)
                    ctx.send(content=list.mel)
                    ctx.send(content=list.mel)
                    ctx.send(content=list.mel)
        elif message.lower() in ['قبول', 'رفض']:
            if command_check(ctx):
                if ctx.author.userId in marriage_proposals:
                    proposal = marriage_proposals[ctx.author.userId]
                    husband_id = proposal["husband_id"]
                    dowry = proposal["dowry"]
                    if ctx.author.userId == husband_id:
                        ctx.reply("❌ لا يمكن للزوج قبول أو رفض عرض الزواج. يجب على الزوجة فقط الرد على العرض.")
                    else:
                        if message.lower() == 'قبول':
                            wife_id = ctx.author.userId
                            wife_account = next((account for account in accounts if account['uid'] == wife_id), None)
                            husband_account = next((account for account in accounts if account['uid'] == husband_id), None)
                            if husband_account and wife_account:
                                if husband_account['money'] >= dowry:
                                    if 'partner' in husband_account and len([p for p in husband_account['partner'].values() if p.get('role') == 'wife']) >= 4:
                                        ctx.reply("❌ عذرًا، الزوج وصل إلى الحد الأقصى من الزوجات (4).")
                                    else:
                                        husband_account['money'] -= dowry
                                        wife_account['money'] += dowry
                                        wife_count = len([p for p in husband_account.get('partner', {}).values() if p.get('role') == 'wife']) + 1
                                        wife_key = f'wife_{wife_count}'
                                        husband_account.setdefault('partner', {})[wife_key] = {
                                            'id': wife_id,
                                            'dowry': dowry,
                                            'name': wife_account['username'],
                                            'role': 'wife'
                                        }
                                        wife_account.setdefault('partner', {})['husband'] = {
                                            'id': husband_id,
                                            'dowry': dowry,
                                            'name': husband_account['username'],
                                            'role': 'husband'
                                        }
                                        del marriage_proposals[ctx.author.userId]
                                        ctx.reply(f"💖 تم الزواج بنجاح! مبروك {ctx.author.username} و {bot.community.fetch_user(husband_id).username}!")
                                        save_accounts(filename, accounts)
                                else:
                                    ctx.reply("❌ المهر غير كافي في حساب الزوج.")
                            else:
                                ctx.reply("❌ خطأ في العثور على حسابات الزوجين.")
                        else:
                            ctx.reply(f"💔 تم رفض طلب الزواج من {bot.community.fetch_user(husband_id).username}.")
                            del marriage_proposals[ctx.author.userId]
                else:
                    ctx.reply("❌ ليس لديك طلب زواج معلق.")

        elif message.startswith('زواج'):
            if command_check(ctx):
                parts = message.split()
                if len(parts) >= 2 and ctx.message.mentioned_user_ids:
                    partner_id = ctx.message.mentioned_user_ids[0]
                    user_account = next((account for account in accounts if account['uid'] == ctx.author.userId), None)
                    partner_account = next((account for account in accounts if account['uid'] == partner_id), None)
                    if is_married(user_account):
                        ctx.reply("🔒 لا يمكن للمرأة الزواج إذا كانت متزوجة بالفعل.")
                        return
                    if not user_account or not partner_account:
                        ctx.reply("❌ أحد الحسابات غير موجود.")
                        return
                    if partner_id == ctx.author.userId:
                        ctx.reply("🚫 لا يمكنك الزواج من نفسك!")
                        return
                    if any("wife" in partner for partner in partner_account.get('partner', {}).values()):
                        ctx.reply("🔒 لا يمكن الزواج من شخص متزوج بالفعل.")
                        return
                    wife_count = len([p for p in user_account.get('partner', {}).values() if p.get('role') == "wife"])
                    if wife_count >= 4:
                        ctx.reply("🔒 لقد وصلت إلى الحد الأقصى من الزوجات (4).")
                        return
                    if any(partner.get('id') == str(partner_id) for partner in user_account.get('partner', {}).values()):
                        ctx.reply("👩‍❤️‍👨 أنت متزوج بالفعل من هذا الشخص.")
                        return
                    if partner_id in marriage_proposals:
                        ctx.reply("💌 هناك بالفعل طلب زواج معلق لهذا الشخص.")
                        return
                    marriage_proposals[ctx.author.userId] = {"husband_id": ctx.author.userId, "partner_id": partner_id}
                    ctx.reply(f"💍 @{bot.community.fetch_user(partner_id).username} هل تقبل الزواج من {ctx.author.username}؟ يرجى إدخال مبلغ المهر.")
                else:
                    ctx.reply("👥 يرجى ذكر الشخص الذي تريد الزواج منه. مثال: زواج @username")
        elif ctx.author.userId in marriage_proposals:
            proposal = marriage_proposals[ctx.author.userId]
            husband_id = proposal.get("husband_id")
            if ctx.author.userId == husband_id and 'dowry' not in proposal:
                try:
                    dowry = int(message)
                    if dowry <= 0:
                        ctx.reply("❌ يجب أن يكون مبلغ المهر أكبر من صفر.")
                        return
                    wife_id = proposal["partner_id"]
                    husband_account = next((account for account in accounts if account['uid'] == husband_id), None)
                    if husband_account['money'] < dowry:
                        ctx.reply("❌ ليس لدى الزوج ما يكفي من المال للمهر.")
                        return
                    proposal["dowry"] = dowry
                    marriage_proposals[wife_id] = proposal  # Store the proposal details for the wife to respond
                    del marriage_proposals[husband_id]  # Remove the initial proposal entry
                    ctx.reply(f"💰 تم تسجيل المهر {dowry}. @{bot.community.fetch_user(wife_id).username}, هل تقبلين الزواج من {bot.community.fetch_user(husband_id).username}؟ يرجى الرد بقبول أو رفض.")
                except ValueError:
                    ctx.reply("❌ يرجى إدخال مبلغ صحيح للمهر.")
            
        elif message.startswith("الحرامية"):
            if command_check(ctx):
                sorted_thieves = sorted([account for account in accounts if account.get('stolen_money', 0) > 0], 
                        key=lambda x: x['stolen_money'], reverse=True)
                top_10 = sorted_thieves[:10]
                message = """ 🏴‍☠️ قائمة أكبر الحرامية:\n\n"""
                for i, thief in enumerate(top_10, 1):
                    username = thief['username']
                    stolen = thief['stolen_money']
                    if stolen >= 1000000000:
                        formatted_stolen = f"{stolen/1000000000:.2f}B"
                    elif stolen >= 1000000:
                        formatted_stolen = f"{stolen/1000000:.2f}M"
                    elif stolen >= 1000:
                        formatted_stolen = f"{stolen/1000:.2f}K"
                    else:
                        formatted_stolen = f"{stolen:.2f}"
                    message += f"""
[c]{i}.{username}
[c]{formatted_stolen} 💸
"""
                ctx.reply(message)
        elif message.startswith("توب"):
            if command_check(ctx):
                sorted_accounts = sorted(accounts, key=lambda x: x['money'], reverse=True)
                top_10 = sorted_accounts[:10]
                message = "🏆 قائمة أغنى 10 أشخاص:\n\n"
                for i, account in enumerate(top_10, 1):
                    username = account['username']
                    money = account['money']
                    if money >= 1000000000:
                        formatted_money = f"{money/1000000000:.2f}B"
                    elif money >= 1000000:
                        formatted_money = f"{money/1000000:.2f}M"
                    elif money >= 1000:
                        formatted_money = f"{money/1000:.2f}K"
                    else:
                        formatted_money = f"{money:.2f}"
                    message += f"""
[C]{i}. {username}
[C]{formatted_money} 💸
"""
                ctx.reply(message)
        elif message.startswith("مهور"):
            if command_check(ctx):
                married_accounts = [account for account in accounts if 'partner' in account and any(f'wife_{i}' in account['partner'] for i in range(1, 5))]
                all_wives = []
                for account in married_accounts:
                    husband_username = account.get('username', 'غير معروف')
                    for wife_key in ['wife_1', 'wife_2', 'wife_3', 'wife_4']:
                        if wife_key in account['partner']:
                            wife_info = account['partner'][wife_key]
                            all_wives.append({
                                'husband_username': husband_username,
                                'wife_username': wife_info.get('name', 'غير معروف'),
                                'dowry': wife_info['dowry']
                            })
                sorted_dowries = sorted(all_wives, key=lambda x: x['dowry'], reverse=True)
                top_10 = sorted_dowries[:10]
                message = "💍 قائمة أعلى 10 مهور:\n\n"
                for i, wife in enumerate(top_10, 1):
                    dowry = wife['dowry']
                    if dowry >= 1000000000:
                        formatted_dowry = f"{dowry/1000000000:.2f}B"
                    elif dowry >= 1000000:
                        formatted_dowry = f"{dowry/1000000:.2f}M"
                    elif dowry >= 1000:
                        formatted_dowry = f"{dowry/1000:.2f}K"
                    else:
                        formatted_dowry = f"{dowry:.2f}"
                    message += f"{i}. {wife['husband_username']} 🤵 & {wife['wife_username']} 👰 | {formatted_dowry} 💰\n"
                ctx.reply(message)
        elif message.startswith('بيع أسهمي'):
            parts = message.split()
            if len(parts) < 4:
                ctx.reply("يرجى تحديد رمز السهم والكمية للبيع.")
                return
            stock_id = parts[2].upper()  # Convert stock identifier to uppercase
            try:
                quantity = int(parts[3])
            except ValueError:
                ctx.reply("الكمية يجب أن تكون رقمًا صحيحًا.")
                return
            stock = next((s for s in stocks if s['id'] == stock_id), None)
            if not stock:
                ctx.reply(f"السهم {stock_id} غير متوفر للبيع.")
                return
            user_account = next((account for account in accounts if account['uid'] == ctx.author.userId), None)
            if not user_account:
                ctx.reply("لم يتم العثور على حساب المستخدم.")
                return
            if stock_id not in user_account['stocks']:
                ctx.reply(f"لا تمتلك أسهم {stock_id} للبيع.")
                return
            if user_account['stocks'][stock_id] < quantity:
                ctx.reply(f"الكمية المطلوبة من أسهم {stock_id} أكبر من ما تمتلكه.")
                return
            total_earning = stock['price'] * quantity
            user_account['money'] += total_earning
            user_account['stocks'][stock_id] -= quantity
            if user_account['stocks'][stock_id] == 0:
                del user_account['stocks'][stock_id]
            ctx.reply(f"""
    تم بيع {quantity} سهم من {stock['name']} بنجاح!
    المبلغ المحصل: {total_earning} دولار
    رصيدك الحالي: {user_account['money']} دولار
    """)
            save_accounts(filename,accounts)
        elif message.startswith('زرف'):
            cooldown_period = 7 * 60  # 7 minutes
            remaining_time = get_cooldown_remaining(user_id, 'زرف', cooldown_period)
            if remaining_time > 0:
                minutes, seconds = divmod(remaining_time, 60)
                ctx.reply(f" يا نصاب استنا {int(minutes)}:{int(seconds)}  توك زارف  ")
            else:
                if not commands_enabled:
                    ctx.reply("تم تعطيل جميع الأوامر حالياً.")
                else:
                    if ctx.message.mentioned_user_ids:
                        user_id = ctx.message.mentioned_user_ids[0]
                        if user_id != bot.userId:
                            user_account = next((account for account in accounts if account['uid'] == user_id), None)
                            user_account1 = next((account for account in accounts if account['uid'] == ctx.author.userId), None)
                            if user_account:
                                amount = random.randint(10, 2000)
                                if user_account['money'] <= 2000:
                                    ctx.reply("ما تقدر تزرف الفقراء")
                                else:
                                    user_account['money'] -= amount
                                    user_account1['money'] += amount
                                    user_account1['stolen_money'] = user_account1.get('stolen_money', 0) + amount  # Increment stolen money
                                    ctx.reply(f"⇜ تم سرقة {amount} دولار من {bot.community.fetch_user(user_id).username} بنجاح.")
                                    update_cooldown(ctx.author.userId, 'زرف')
                                    save_accounts(filename, accounts)
                            else:
                                ctx.reply("المستخدم غير موجود.")
                        else:
                            ctx.reply("لا يمكنك سرقة من البوت.")
                    else:
                        ctx.reply("يرجى ذكر مستخدم.")
        elif message.startswith('طلاق'):
            if command_check(ctx):
                if ctx.message.mentioned_user_ids:
                    wife_id = ctx.message.mentioned_user_ids[0]
                    husband_account = next((account for account in accounts if account['uid'] == ctx.author.userId), None)
                    wife_account = next((account for account in accounts if account['uid'] == wife_id), None)
                    
                    if husband_account and wife_account:
                        if 'partner' in husband_account and any(wife['id'] == wife_id for wife in husband_account['partner'].values()):
                            wife_to_divorce = next(wife for wife in husband_account['partner'].values() if wife['id'] == wife_id)
                            wife_role = next(key for key, value in husband_account['partner'].items() if value['id'] == wife_id)
                            del husband_account['partner'][wife_role]
                            if 'partner' in wife_account:
                                del wife_account['partner']
                            ctx.reply(f"تم الطلاق بنجاح من {bot.community.fetch_user(wife_id).username}.")
                            save_accounts(filename, accounts)
                        else:
                            ctx.reply("هذه المستخدمة ليست زوجتك.")
                    else:
                        ctx.reply("لم يتم العثور على أحد الحسابين.")
                else:
                    ctx.reply("يرجى ذكر الزوجة التي تريد طلاقها.")

        elif message.startswith('خلع'):
            if command_check(ctx):
                wife_account = next((account for account in accounts if account['uid'] == ctx.author.userId), None)
                
                if wife_account and 'partner' in wife_account:
                    for partner_key, partner_info in wife_account['partner'].items():
                        if partner_info['role'] == 'husband':
                            husband_id = partner_info['id']
                            husband_account = next((account for account in accounts if account['uid'] == husband_id), None)
                            
                            if husband_account:
                                del wife_account['partner'][partner_key]
                                if 'partner' in husband_account:
                                    husband_account['partner'] = {k: v for k, v in husband_account['partner'].items() if v['id'] != ctx.author.userId}
                                ctx.reply(f"تم الخلع بنجاح من {bot.community.fetch_user(husband_id).username}.")
                                save_accounts(filename, accounts)
                                return
                            else:
                                ctx.reply("لم يتم العثور على حساب الزوج.")
                                return
                    
                    ctx.reply("أنتِ غير متزوجة من رجل حالياً.")
                else:
                    ctx.reply("أنتِ غير متزوجة حالياً.")
            else:
                ctx.reply("لا يمكنك استخدام هذا الأمر.")
        elif message.startswith('شراء أسهم'):
            parts = message.split()
            if len(parts) < 3:
                ctx.reply("يرجى تحديد رمز السهم والكمية للشراء.")
                return
            stock_id = parts[2].upper()
            stock = next((s for s in stocks if s['id'] == stock_id), None)
            if not stock:
                ctx.reply(f"السهم {stock_id} غير متوفر للشراء.")
                return
            user_account = next((account for account in accounts if account['uid'] == ctx.author.userId), None)
            if not user_account:
                create_account(accounts=accounts, ctx=ctx)
            user_account = next((account for account in accounts if account['uid'] == ctx.author.userId), None)
            if not user_account:
                return  # Handle the case where user_account is still None
            
            if len(parts) < 4:
                ctx.reply("يرجى تحديد الكمية للشراء.")
                return
            
            # Check if the stock prices have changed
            if 'last_price_update' not in globals():
                global last_price_update
                last_price_update = time.time()
            
            current_time = time.time()
            if current_time - last_price_update > 3600:  # 1 hour
                # Reset purchase counts for all users
                for account in accounts:
                    account['purchase_count'] = 0
                last_price_update = current_time
            
            if 'purchase_count' not in user_account:
                user_account['purchase_count'] = 0
            
            if user_account['purchase_count'] >= 300:
                ctx.reply(f"لقد وصلت إلى الحد الأقصى للشراء. يرجى الانتظار حتى يتم تحديث أسعار الأسهم.")
                return
            
            if parts[3] == 'فلوسي':
                quantity = min(int(user_account['money'] // stock['price']), 300 - user_account['purchase_count'])
            else:
                try:
                    quantity = min(int(parts[3]), 300 - user_account['purchase_count'])
                    print(quantity)
                except ValueError:
                    ctx.reply("يرجى تحديد كمية صحيحة للشراء.")
                    return
            
            if stock['price'] == 0:
                ctx.reply(f"لا يمكن شراء أسهم {stock['name']} حالياً لأن سعرها صفر.")
                return
            
            if quantity == 0:
                ctx.reply(f"الكمية المحددة غير صحيحة. يجب أن تكون أكبر من صفر.")
                return
            
            total_cost = stock['price'] * quantity
            if user_account['money'] < total_cost:
                ctx.reply(f"لا يوجد لديك ما يكفي لشراء {quantity} سهم من {stock['name']}.")
                return
            if 'quantity' in stock:
                available_quantity = min(stock['quantity'], 300 - user_account['purchase_count'])
                if available_quantity < quantity:
                    quantity = available_quantity
                    total_cost = stock['price'] * quantity
            else:
                available_quantity = 300 - user_account['purchase_count']
                if available_quantity < quantity:
                    quantity = available_quantity
                    total_cost = stock['price'] * quantity
            
            user_account['money'] -= total_cost
            if 'quantity' in stock:
                stock['quantity'] -= quantity
            if stock['id'] in user_account['stocks']:
                user_account['stocks'][stock['id']] += quantity
            else:
                user_account['stocks'][stock['id']] = quantity
            
            user_account['purchase_count'] += quantity
            
            ctx.reply(f"""
    تم شراء {quantity} سهم من {stock['name']} بنجاح!
    المبلغ المستخدم: {total_cost} دولار
    رصيدك الحالي: {user_account['money']} دولار
    """)
            save_accounts(filename, accounts)
        elif message.startswith("تحويل"):
            if not commands_enabled:
                ctx.reply("تم تعطيل جميع الأوامر حالياً.")
            else:
                link = None
                amount = None
                user2 = None
                if "http" in message:
                    link_pattern = r"http[s]?://[^\s]+"
                    link_match = re.search(link_pattern, message)
                    link = link_match.group(0) if link_match else None
                    user2 = bot.community.fetch_object_info(link).objectId
                    if ctx.author.userId == user2:
                        ctx.reply("لا يمكنك التحويل لنفسك")
                    else:
                        amount_pattern = r"\b\d+\b"
                        amount_match = re.search(amount_pattern, message)
                        if amount_match:
                            amount = int(amount_match.group(0))
                            ctx.send_embed(
                        message=f"تحويل مبلغ {amount} الى {bot.community.fetch_user(userId=user2).username}",
                        content="- ضع بطاقتك لتأكيد عملية التحويل",
                        title=" ",
                        image="nfc.png"
                    )
                        else:
                            ctx.reply("يرجى كتابة رقم صحيح.")
                            return
                else:
                    if ctx.message.mentioned_user_ids:
                        user_id = ctx.message.mentioned_user_ids[0]
                        if user_id != bot.userId:
                            user2 = user_id
                            amount_pattern = r"@?\s*(\d+)"
                            amount_match = re.search(amount_pattern, message)
                            if amount_match:
                                amount = int(amount_match.group(1))
                            else:
                                ctx.reply("يرجى كتابة رقم صحيح.")
                                return
                            if user2 and amount:
                                user_account = next((account for account in accounts if account['uid'] == ctx.author.userId), None)
                                user_account2 = next((account for account in accounts if account['uid'] == user2), None)
                            if user_account:
                                confirmation_list.append({
                        'user1_id': ctx.author.userId,
                        'user2_id': user2,
                        'amount': amount,
                        'confirmed': False
                    })
                                ctx.send_embed(
                        message=f"            تحويل مبلغ {amount} الى {bot.community.fetch_user(userId=user2).username}",
                        content="- ضع بطاقتك لتأكيد عملية التحويل",
                        title="\u200e\u200f",
                        image="nfc.png"
                    )
                            else:
                                create_account(ctx=ctx, accounts=accounts)

        elif message.startswith('شريك'):
             if not commands_enabled:
                    ctx.reply("تم تعطيل جميع الأوامر حالياً.")
             else:
                usernames = []
                for i in range(0, 1000, 100):
                    names = bot.community.fetch_chat_members(chatId=ctx.chatId,size=100, start=i).members.nickname
                    if not names:
                        break
                    for name in names:
                        usernames.append(name)
                name = random.choice(usernames)
                ctx.reply(f'شريك حياتك ← {name}')
                    
        elif message.startswith('راتب'):
            cooldown_period = 20 * 60  # 20 minutes
            remaining_time = get_cooldown_remaining(user_id, 'راتب', cooldown_period)
            if remaining_time > 0:
                minutes, seconds = divmod(remaining_time, 60)
                ctx.reply(f"لقد استلمت راتبك بالفعل. الرجاء الانتظار {int(minutes)}:{int(seconds)} دقيقة  قبل طلبه مرة أخرى.")
            else:
                amount = random.randint(2500, 5000)  # Random amount between 2500 and 5000 dollars
                user_account = next((account for account in accounts if account['uid'] == ctx.author.userId), None)
                if user_account:
                    user_account['money'] += amount
                    ctx.reply(f"""
شعار ايداع \u200e\u200f{ctx.author.username}\u202c\u202d                               
المبلغ: {amount} دولار
وظيفتك: {list.pick_random_job()}
نوع العملية: اضافة راتب
رصيدك الحين: {user_account['money']} دولار 💸
                """)
                    save_accounts(filename, accounts)
                    update_cooldown(user_id, 'راتب')
                else:
                    create_account(ctx=ctx,accounts=accounts)
        elif message.startswith("عرض"):
            if is_vip(ctx.author.userId):
                if not commands_enabled:
                    ctx.reply("تم تعطيل جميع الأوامر حالياً.")
                else:
                    new_state = view_only(ctx)
                    print(new_state)
                    if new_state:
                        ctx.reply("تم تفعيل وضع العرض فقط.")
                    else:
                        ctx.reply("تم تعطيل وضع العرض فقط.")
                    
        

        elif message.startswith("سوق الأسهم"):
            if not commands_enabled:
                ctx.reply("تم تعطيل جميع الأوامر حالياً.")
            else:
                current_time = time.time()
                price_time_left = int(price_update_interval - (current_time - last_price_update_time))
                price_minutes_left, price_seconds_left = divmod(price_time_left, 60)

                stocks_info = "\n[C]".join([f"{stock['name']} ↝ {stock['price']}$" for stock in stocks])
                ctx.reply(f"""[Uc]               𝐂𝐮𝐫𝐫𝐞𝐧𝐭 𝐒𝐭𝐨𝐜𝐤          
[C]{stocks_info}
[Cu]
[Cu]التحديث السِعر التالي في : {price_minutes_left} دقيقة و {price_seconds_left} ثانية  
[Scu]
""")        
        elif message.startswith('بطاقتي'):
            if not commands_enabled:
                    ctx.reply("تم تعطيل جميع الأوامر حالياً.")
            else:
                 user_account = next((account for account in accounts if account['uid'] == ctx.author.userId), None)
                 if user_account:
                     upload_sticker(ctx=ctx,filepath=user_account['card_image'])
                 else:
                     create_account(ctx=ctx,accounts=accounts)
        elif message.startswith('فلوسي'):
            if not commands_enabled:
                    ctx.reply("تم تعطيل جميع الأوامر حالياً.")
            else:
                user_account = next((account for account in accounts if account['uid'] == ctx.author.userId), None)
                if user_account:
                    ctx.reply(f"⇜ فلوسك  {user_account['money']:,} دولار 💸")
        elif message.startswith('حذف حسابي'):
            account_index = next((index for index, account in enumerate(accounts) if account['uid'] == ctx.author.userId), None)
            if account_index is not None:
                del accounts[account_index]
                ctx.reply("تم حذف حسابك بنجاح.")
            else:
                ctx.reply("لا يوجد حساب لحذفه.")
        elif message.startswith('بقشيش'):
            cooldown_period = 15 * 60  # 6 minutes
            remaining_time = get_cooldown_remaining(user_id, 'بخشيش', cooldown_period)
            if remaining_time > 0:
                minutes, seconds = divmod(remaining_time, 60)
                ctx.reply(f"لقد استلمت بقشيشك بالفعل. الرجاء الانتظار {int(minutes)}:{int(seconds)} دقيقة  قبل طلبه مرة أخرى.")
            else:
                amount = random.randint(50, 3000)  # Random amount between 50 and 3000
                user_account = next((account for account in accounts if account['uid'] == ctx.author.userId), None)
                if user_account:
                    user_account['money'] += amount
                    ctx.reply(f"⇜ دلعتك وعطيتك {amount} دولار 💸")
                    save_accounts(filename, accounts)
                    update_cooldown(user_id, 'بخشيش')
                else:
                    create_account(ctx=ctx,accounts=accounts)
        elif message.startswith('حظ'):
            cooldown_period = 10 * 60  # 10 minutes
            remaining_time = get_cooldown_remaining(user_id, 'حظ', cooldown_period)
            if remaining_time > 0:
                minutes, seconds = divmod(remaining_time, 60)
                ctx.reply(f"لقد قمت بالحظ بالفعل. الرجاء الانتظار {int(minutes)}:{int(seconds)} دقيقة  قبل طلبه مرة أخرى.")
            else:
                try:
                    amount_to_gamble = message.split()[1]
                    user_account = next((account for account in accounts if account['uid'] == ctx.author.userId), None)
                    if user_account:
                        if amount_to_gamble == "فلوسي":
                            amount_to_gamble = user_account['money']
                        else:
                            amount_to_gamble = int(amount_to_gamble)
                        
                        if amount_to_gamble > user_account['money']:
                            ctx.reply("لا تملك المال الكافي للقيام بالحظ.")
                            return

                        success = random.random() < 0.5  # 50% chance of success
                        if success:
                            new_balance = user_account['money'] + amount_to_gamble
                            user_account['money'] = new_balance
                            ctx.reply(f"""
⇜ حظك حلو!
⇜ ربحت ↢ ( {amount_to_gamble} دولار )
⇜ فلوسك صارت ↢ ( {new_balance} دولار 💸 )
                            """)
                            save_accounts(filename, accounts)
                            update_cooldown(user_id, 'حظ')
                        else:
                            new_balance = user_account['money'] - amount_to_gamble
                            if new_balance < 0:
                                new_balance = 0
                            user_account['money'] = new_balance
                            ctx.reply(f"""
⇜ حظك سيء!
⇜ خسرت ↢ ( {amount_to_gamble} دولار )
⇜ فلوسك صارت ↢ ( {new_balance} دولار 💸 )
                            """)
                            save_accounts(filename, accounts)
                            update_cooldown(user_id, 'حظ')
                    else:
                        create_account(ctx=ctx,accounts=accounts)
                except ValueError:
                    ctx.reply("يرجى إدخال مبلغ صحيح.")
        elif message.startswith('استثمار'):
            cooldown_period = 6 * 60  # 6 minutes
            remaining_time = get_cooldown_remaining(user_id, 'استثمار', cooldown_period)
            if remaining_time > 0:
                minutes, seconds = divmod(remaining_time, 60)
                ctx.reply(f"لقد قمت بالأستثمار بالفعل. الرجاء الانتظار {int(minutes)}:{int(seconds)} دقيقة  قبل طلبه مرة أخرى.")
            else:
                try:
                    amount_to_invest = message.split()[1]
                    user_account = next((account for account in accounts if account['uid'] == ctx.author.userId), None)
                    if user_account:
                        if amount_to_invest == "فلوسي":
                            amount_to_invest = user_account['money']
                        else:
                            amount_to_invest = int(amount_to_invest)
                        
                        if amount_to_invest > user_account['money']:
                            ctx.reply("لا تملك المال الكافي للقيام بالاستثمار.")
                            return

                        success = random.random() < 0.9  # 90% chance of success
                        if success:
                            profit_percentage = random.randint(1, 15)
                            profit_amount = int(amount_to_invest * (profit_percentage / 100))
                            new_balance = user_account['money'] + profit_amount
                            user_account['money'] = new_balance
                            ctx.reply(f"""
⇜ استثمار ناجح!
⇜ نسبة الربح ↢ {profit_percentage}%
⇜ مبلغ الربح ↢ ( {profit_amount} دولار )
⇜ فلوسك صارت ↢ ( {new_balance} دولار 💸 )
                            """)
                            update_cooldown(user_id, 'استثمار')
                        else:
                            new_balance = user_account['money'] - amount_to_invest
                            if new_balance < 0:
                                new_balance = 0
                            user_account['money'] = new_balance
                            ctx.reply(f"""
⇜ استثمار فاشل!
⇜ خسرت مبلغ ↢ ( {amount_to_invest} دولار )
⇜ فلوسك صارت ↢ ( {new_balance} دولار 💸 )
                            """)
                            update_cooldown(user_id, 'استثمار')
                    else:
                        create_account(ctx=ctx,accounts=accounts)
                except ValueError:
                    ctx.reply("يرجى إدخال مبلغ استثمار صحيح.")
        elif message.startswith('حسابي'):
            if not commands_enabled:
                    ctx.reply("تم تعطيل جميع الأوامر حالياً.")
            else:
                user_account = next((account for account in accounts if account['uid'] == ctx.author.userId), None)
                if user_account:
                    rank = sorted(accounts, key=lambda x: x['money'], reverse=True).index(user_account) + 1
                    card_type = next((name for name, info in CARD_INFO.items() if info['image'] == user_account['card_image']), 'Unknown')
                    card_type_display = {
                    'VIP': 'VIP',
                    'BLUE': 'Platinum',
                    'WHITE': 'Gold',
                    'BLACK': 'Diamond'
                }.get(card_type, 'Unknown')
                    ctx.reply(f"""
⇜ الاسم ↢ {ctx.author.username}
⇜ الرصيد ↢ ( {user_account['money']} دولار💸 )
⇜ التصنيف ↢ ({rank})
⇜ نوع ↢ ({card_type_display})
                """)
                else:
                    create_account(ctx=ctx,accounts=accounts)


    except Exception as e:
        print(e)
        ctx.reply('حدث خطأ في خادم أمينو، يرجى المحاولة مرة أخرى.')
@bot.on_sticker_message()
def on_sticker_message(ctx: Context):
    if is_blacklisted(ctx.author.userId):
        bot.community.delete_message(chatId=ctx.chatId, messageId=ctx.message.messageId)
        return
    else:
        command_check(ctx)
        sticker_name = ctx.message.extensions['sticker']['name']
        user_id_prefix = ctx.author.userId[:10]  # Get the first 10 characters of the user ID
        sticker_prefix = sticker_name[:10]  # Get the first 10 characters of the sticker name
        
        # Check if the first 10 characters of sticker_name match the first 10 characters of the user ID
        if sticker_prefix == user_id_prefix:
            try:
                handle_confirmation(ctx, confirmation_list, accounts)
            except Exception as e:
                print(e)
        else:
            # Handle other actions if needed when sticker name prefixes don't match
            pass


@bot.command("قائمة")
def command_list(ctx: Context):
    if command_check(ctx):
        admin_commands = """
🛡️ أوامر الأدمن:
• run - تفعيل الأوامر
• sleep - تعطيل الأوامر
• عرض - تفعيل/تعطيل وضع العرض فقط
• all - منشن للجميع
"""

        bank_commands = """
💰 أوامر البنك:
• فلوسي - عرض رصيدك
• تحويل - تحويل الأموال
• راتب - استلام الراتب
• بقشيش - الحصول على بقشيش
• استثمار - استثمار الأموال
• حظ - المقامرة
• زرف - سرقة الأموال
• توب - قائمة أغنى الأشخاص
• الحرامية - قائمة أكبر السارقين
• حسابي - عرض معلومات الحساب
• بطاقتي - عرض بطاقتك البنكية
"""

        voice_image_commands = """
🎤🖼️ أوامر الصوتيات والصور:
• vc - بدء المكالمة الصوتية
• end_vc - إنهاء المكالمة الصوتية
"""

        game_commands = """
🎮 أوامر الألعاب:
• شريك - اختيار شريك حياة عشوائي
"""

        stock_commands = """
📈 أوامر الأسهم:
• سوق الأسهم - عرض أسعار الأسهم الحالية
• شراء أسهم - شراء أسهم
• بيع أسهمي - بيع أسهم
• أسهمي - عرض الأسهم المملوكة
"""

        marriage_commands = """
💍 أوامر الزواج:
• زواج - طلب الزواج
• طلاق - طلب الطلاق
• خلع - طلب الخلع
• مهور - عرض أعلى المهور
"""

        message = f"{admin_commands}\n{bank_commands}\n{voice_image_commands}\n{game_commands}\n{stock_commands}\n{marriage_commands}"
        ctx.reply(message)

@bot.command(name="run", cooldown=1)
def enable_commands(ctx: Context):
    global commands_enabled
    if is_vip(ctx.author.userId):
        commands_enabled = True
        ctx.reply("تم تفعيل جميع الأوامر.")
    else:
        ctx.reply("ليس لديك إذن لتفعيل الأوامر.")

@bot.command(name="sleep", cooldown=1)
def disable_commands(ctx: Context):
    global commands_enabled
    if is_vip(ctx.author.userId):
        commands_enabled = False
        ctx.reply("تم تعطيل جميع الأوامر.")
    else:
        ctx.reply("ليس لديك إذن لتعطيل الأوامر.")

@bot.command('end_vc')
def end_vc(ctx: Context):
    if is_vip(ctx.author.userId):
        if command_check(ctx):
            bot.community.stop_vc(chatId=ctx.chatId, comId=ctx.comId)

@bot.command('إضافة')
def join(ctx: Context , message :str):
    if is_vip(ctx.author.userId):
        if command_check(ctx):
            print(message)
            chatId=bot.community.fetch_object_info(message).objectId
            bot.community.join_chat(chatId=chatId)
            bot.community.send_message(chatId=chatId,content="ميا المزة انضمت")
            ctx.reply("أنضمت ميا الى الدردشة")

@bot.command('مغادرة')
def join(ctx: Context , message :str):
    if is_vip(ctx.author.userId):
        if command_check(ctx):
            chatId=bot.community.fetch_object_info(message).objectId
            bot.community.leave_chat(chatId=chatId)  
            ctx.reply("غادرت ميا الدردشة")    
@bot.command('vc')
def vc(ctx: Context):
    if is_vip(ctx.author.userId):
        if command_check(ctx):
            bot.community.start_vc(chatId=ctx.chatId, comId=ctx.comId)
@bot.command(name="ping", cooldown=166)
def ping(ctx: Context):
    if command_check(ctx):
        ctx.reply("pong!")
        bot.community.kick(userId="55e92b67-9cdc-4f47-9cac-5068836491eb", chatId=ctx.chatId,allowRejoin=False)
@bot.command(name="kiss", cooldown=1)
def kiss(ctx: Context):
    try:
        if command_check(ctx):
            user_men = ctx.message.mentioned_user_ids[0]
            download_image(bot.community.fetch_user(user_men).icon, 'mu.png')
            new_size = (250, 250)
            circular_image = create_circular_image('mu.png', new_size)
            kiss=Image.open("kis.png")
            main_image = Image.open("kiss.png")
            position_1 = (380, 190)
            position_2 = (517, 353)
            size=(90,90)
            kiss = kiss.resize(size, Image.Resampling.LANCZOS)
            main_image.paste(circular_image, position_1, circular_image)
            main_image.paste(kiss, position_2, kiss)
            main_image.save('mai.png')
            resize_image('mai.png')
            ctx.send_link_snippet(
            message=f"[C].          {ctx.author.username} -`💋´- {bot.community.fetch_user(user_men).username}       ",
            image='mai.png',
            link=f"ndc://user-profile/{ctx.author.userId}"
        )
    except Exception as e:
        print(f"An error occurred: {str(e)}")

@bot.command(name="lv", cooldown=1)
def love(ctx: Context):
    try:
        if command_check(ctx):
            # Assuming download_image and create_circular_image are defined elsewhere
            download_image(ctx.author.icon, 'user.png')
            user_men = ctx.message.mentioned_user_ids[0]
            download_image(bot.community.fetch_user(user_men).icon, 'user1.png')
            
            new_size = (370, 370)
            circular_image_1 = create_circular_image('user.png', new_size)
            circular_image_2 = create_circular_image('user1.png', new_size)

            position_1 = (223, 283)  # Example position for the first image
            position_2 = (1314, 283)  # Example position for the second image 
            love_percentage = random.randint( -50, 100)
            if 90 <= love_percentage <=  100:
                image_filename = 'love.png'
            elif 60 <= love_percentage < 90:
                image_filename = 'lov.png'
            elif 40 <= love_percentage < 60:
                image_filename = 'lo.png'
            else:
                image_filename = 'l.png'

            # Open the main image
            main_image = Image.open(image_filename)
            
            # Paste the circular images onto the main image
            main_image.paste(circular_image_1, position_1, circular_image_1)
            main_image.paste(circular_image_2, position_2, circular_image_2)
            
            # Add text to the image
            draw = ImageDraw.Draw(main_image)
            font = ImageFont.truetype("font.ttf", 150)
            text = f"{love_percentage}%"
            text_position = (main_image.width // 2, 841)  # Example position for the text
            text_color = (0, 0, 0)  # Black color for the text
            draw.text(text_position, text, font=font, fill=text_color, anchor="ms")
            
            # Save the resulting image
            main_image.save('main.png')
            resize_image('main.png')
            ctx.send_link_snippet(
            message=f"[C].          {ctx.author.username} -`♡´- {bot.community.fetch_user(user_men).username}       ",
            image='main.png',
            link=f"ndc://user-profile/{ctx.author.userId}"
        )

            # Send the image in the Discord channel
    except Exception as e:
        ctx.reply(f"An error occurred: {str(e)}")

@bot.command(name="طرد")
def kick(ctx: Context):
    if command_check(ctx):
        try:
            if is_vip(ctx.author.userId):
                if ctx.message.mentioned_user_ids:
                    user_id = ctx.message.mentioned_user_ids[0]
                    if user_id == bot.userId:
                        ctx.reply("روح نام")
                    else:
                        bot.community.kick(userId=user_id,chatId=ctx.chatId)
                        ctx.reply("تم الطرد")
        except Exception as e:
            print(e)
@bot.command(name="up")
def up(ctx: Context):
    if command_check(ctx):
        try:
            if is_vip(ctx.author.userId):
                print(bot.community.invite_to_vc(userId=ctx.author.userId,chatId=ctx.chatId))
            else:
                ctx.reply("You need to be a VIP to use this command.")
        except Exception as e:
            print(e)
@bot.command(name="bank", cooldown=1)
def bank(ctx: Context):
    if command_check(ctx):
        try:
            create_account(accounts=accounts, ctx=ctx)
        except Exception as e:
            print(f"An error occurred while executing the bank command: {str(e)}")


@bot.command(name="a-black", cooldown=1)
def add_to_blacklist(ctx: Context):
    if is_vip(ctx.author.userId):
        if ctx.message.mentioned_user_ids:
            user_id = ctx.message.mentioned_user_ids[0]
            if user_id != bot.userId:
                if not is_vip(user_id):
                    if user_id not in lists["blacklist"]:
                        lists["blacklist"].append(user_id)
                        save_lists()
                        ctx.reply(f"تمت إضافة المستخدم إلى القائمة السوداء.")
                    else:
                        ctx.reply("المستخدم موجود بالفعل في القائمة السوداء.")
                else:
                    ctx.reply("لا يمكنك إضافة شخصية مهمة إلى القائمة السوداء.")
            else:
                ctx.reply("لا يمكنك إضافة البوت إلى القائمة السوداء.")
        else:
            ctx.reply("يرجى ذكر مستخدم.")
    else:
        ctx.reply("ليس لديك إذن لإضافة المستخدمين إلى القائمة السوداء.")

@bot.command(name="r-black", cooldown=1)
def remove_from_blacklist(ctx: Context):
    if is_vip(ctx.author.userId):
        if ctx.message.mentioned_user_ids:
            user_id = ctx.message.mentioned_user_ids[0]
            test=bot.community.fetch_user(user_id)
            print(test)
            if user_id in lists["blacklist"]:
                lists["blacklist"].remove(user_id)
                save_lists()
                ctx.reply(f"تمت إزالة المستخدم من القائمة السوداء.")
            else:
                ctx.reply("المستخدم غير موجود في القائمة السوداء.")
        else:
            ctx.reply("يرجى ذكر مستخدم.")
    else:
        ctx.reply("ليس لديك إذن لإزالة المستخدمين من القائمة السوداء.")

@bot.on_member_join()
def join(ctx: Context):
    if is_vip(ctx.author.userId):
        ctx.reply('ولكم عمي وعم الجميع')
    else:
        try:
            ctx.reply("[C] -لا تُسِئ اللفظ وإن ضَاق عليك الرَّد .")
        except Exception as e:
            print(f"Error in on_member_join function: {e}")

try:
    bot.run(
    )
except Exception as e:
    print(f"Error during bot execution: {e}")
