"""
تطبيق شحن كروت فكة - النسخة النهائية للـ APK
المطور: Hamada Ali | رقم التواصل: 01019466176
"""

import flet as ft
import requests
import json
import sqlite3
import hashlib
import threading
import os
import re
from datetime import datetime

# ======================== إعدادات التطبيق ========================
STAR_PRICE = 2.5
MIN_STARS_PURCHASE = 40
SUPPORT_PHONE = "01019466176"
DEVELOPER_NAME = "Hamada Ali"

# ======================== قائمة الكروت (27 كرت - كاملة) ========================
PRODUCTS = [
    {"id": "Fakka_2.5_Unite", "name": "45 وحدة - يوم", "price": "2.5"},
    {"id": "Fakka_4.25_Unite", "name": "190 وحدة - يوم", "price": "4.25"},
    {"id": "Fakka_5_Unite", "name": "225 وحدة - يوم", "price": "5"},
    {"id": "Fakka_6_Unite", "name": "225 وحدة - يوم", "price": "6"},
    {"id": "Fakka_7_Unite", "name": "400 وحدة - 4 أيام", "price": "7"},
    {"id": "Fakka_9_Unite", "name": "400 وحدة - 4 أيام", "price": "9"},
    {"id": "Fakka_10_Unite", "name": "450 وحدة - 7 أيام", "price": "10"},
    {"id": "Fakka_10.5_Unite", "name": "450 وحدة - 7 أيام", "price": "10.5"},
    {"id": "Fakka_11.5_Unite", "name": "450 وحدة - 7 أيام", "price": "11.5"},
    {"id": "Fakka_12_Unite", "name": "625 وحدة - 7 أيام", "price": "12"},
    {"id": "Fakka_12.5_Unite", "name": "625 وحدة - 7 أيام", "price": "12.5"},
    {"id": "Fakka_13_Unite", "name": "650 وحدة - 10 أيام", "price": "13"},
    {"id": "Fakka_13.5_Unite", "name": "650 وحدة - 10 أيام", "price": "13.5"},
    {"id": "Fakka_15_Unite", "name": "650 وحدة - 10 أيام", "price": "15"},
    {"id": "Fakka_15.5_Unite", "name": "750 وحدة - 10 أيام", "price": "15.5"},
    {"id": "Fakka_16.5_Unite", "name": "750 وحدة - 10 أيام", "price": "16.5"},
    {"id": "Fakka_17.5_Unite", "name": "650 وحدة - 10 أيام", "price": "17.5"},
    {"id": "Fakka_20_Unite", "name": "750 وحدة - 10 أيام", "price": "20"},
    {"id": "Fakka_26_Unite", "name": "750 وحدة - 10 أيام", "price": "26"},
    {"id": "Fakka_5_NewUnite", "name": "باقة جديدة - 5", "price": "5"},
    {"id": "Fakka_6_NewUnite", "name": "باقة جديدة - 6", "price": "6"},
    {"id": "Fakka_10_NewUnite", "name": "باقة جديدة - 10", "price": "10"},
    {"id": "Fakka_15_NewUnite", "name": "باقة جديدة - 15", "price": "15"},
    {"id": "Fakka_19.5_NewUnite", "name": "باقة جديدة - 19.5", "price": "19.5"},
    {"id": "Mared_10_Minuts", "name": "ماريد - 10 دقائق", "price": "10"},
    {"id": "Mared_10_Flexs", "name": "ماريد - 10 فليكس", "price": "10"},
    {"id": "Mared_10_Social", "name": "ماريد - 10 سوشيال", "price": "10"},
]

# ======================== دوال API فودافون (الأصلية) ========================
def get_seamless_and_msisdn():
    url = "http://mobile.vodafone.com.eg/checkSeamless/realms/vf-realm/protocol/openid-connect/auth"
    params = {'client_id': "cash-app"}
    headers = {
        'User-Agent': "okhttp/4.12.0", 'Connection': "Keep-Alive", 'Accept-Encoding': "gzip",
        'x-agent-operatingsystem': "16", 'clientId': "AnaVodafoneAndroid", 'Accept-Language': "ar",
        'x-agent-device': "Samsung SM-A165F", 'x-agent-version': "2025.11.1", 'x-agent-build': "1063",
        'digitalId': "", 'device-id': "b26ba335813fad21", 'If-Modified-Since': "Thu, 02 Apr 2026 09:09:07 GMT"
    }
    resp = requests.get(url, params=params, headers=headers, timeout=30)
    if resp.status_code != 200:
        raise Exception("فشل seamlessToken - تأكد من أن الداتا مفتوحة من شريحة فودافون")
    data = resp.json()
    raw_msisdn = data.get("msisdn")
    if raw_msisdn and raw_msisdn.startswith('1'):
        formatted_msisdn = '0' + raw_msisdn
    else:
        formatted_msisdn = raw_msisdn
    return data.get("seamlessToken"), formatted_msisdn

def get_access_token(seamless_token):
    url = "https://mobile.vodafone.com.eg/auth/realms/vf-realm/protocol/openid-connect/token"
    payload = {
        'grant_type': "password",
        'client_secret': "b86e30a8-ae29-467a-a71f-65c73f2ff5e3",
        'client_id': "cash-app"
    }
    headers = {
        'User-Agent': "okhttp/4.12.0", 'Accept': "application/json, text/plain, */*", 'Accept-Encoding': "gzip",
        'silentLogin': "true", 'CRP': "false", 'seamlessToken': seamless_token, 'firstTimeLogin': "true",
        'x-agent-operatingsystem': "16", 'clientId': "AnaVodafoneAndroid", 'Accept-Language': "ar",
        'x-agent-device': "Samsung SM-A165F", 'x-agent-version': "2025.11.1", 'x-agent-build': "1063",
        'digitalId': "", 'device-id': "b26ba335813fad21"
    }
    resp = requests.post(url, data=payload, headers=headers, timeout=30)
    if resp.status_code != 200:
        raise Exception("فشل access_token")
    return resp.json().get("access_token")

def purchase_product(selected_product, msisdn_sender, receiver, pin, access_token):
    url_order = "https://mobile.vodafone.com.eg/services/dxl/pom/productOrder"
    payload_order = {
        "channel": {"name": "MobileApp"},
        "orderItem": [{
            "action": "insert",
            "id": selected_product,
            "product": {
                "characteristic": [
                    {"name": "PaymentMethod", "value": "VFCash"},
                    {"name": "USE_EMONEY", "value": "False"},
                    {"name": "MerchantCode", "value": "81841829"}
                ],
                "id": selected_product,
                "relatedParty": [
                    {"id": msisdn_sender, "name": "MSISDN", "role": "Subscriber"},
                    {"id": receiver, "name": "Receiver", "role": "Receiver"}
                ]
            },
            "@type": selected_product,
            "eCode": 0
        }],
        "relatedParty": [{"id": pin, "name": "pin", "role": "Requestor"}],
        "@type": "CashFakkaAndMared"
    }
    headers_order = {
        'User-Agent': "okhttp/4.12.0", 'Accept': "application/json", 'Accept-Encoding': "gzip",
        'api-host': "ProductOrderingManagement", 'useCase': "CashFakkaAndMared",
        'X-Request-ID': "bb81cbe5-0c77-4673-945e-d2c0de90007a", 'device-id': "b26ba335813fad21",
        'api-version': "v2", 'msisdn': msisdn_sender,
        'Authorization': f"Bearer {access_token}",
        'Accept-Language': "ar", 'x-agent-operatingsystem': "16", 'clientId': "AnaVodafoneAndroid",
        'x-agent-device': "Samsung SM-A165F", 'x-agent-version': "2025.11.1", 'x-agent-build': "1063",
        'digitalId': "", 'Content-Type': "application/json; charset=UTF-8"
    }
    resp = requests.post(url_order, data=json.dumps(payload_order), headers=headers_order, timeout=60)
    return resp

# ======================== قاعدة البيانات ========================
DB_NAME = "fakka_app.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        stars INTEGER DEFAULT 0,
        is_admin INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        receiver TEXT,
        product TEXT,
        status TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS star_purchases (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        stars_added INTEGER,
        amount_paid REAL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS settings (
        key TEXT PRIMARY KEY,
        value TEXT
    )''')
    c.execute("INSERT OR IGNORE INTO settings VALUES ('star_price', '2.5')")
    
    hashed = hashlib.sha256("admin123".encode()).hexdigest()
    c.execute("INSERT OR IGNORE INTO users (username, password, stars, is_admin) VALUES (?, ?, ?, ?)",
              ("admin", hashed, 999999, 1))
    c.execute("INSERT OR IGNORE INTO users (username, password, stars, is_admin) VALUES (?, ?, ?, ?)",
              ("test", hashed, 50, 0))
    conn.commit()
    conn.close()

def get_user(username):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT id, username, password, stars, is_admin FROM users WHERE username = ?", (username,))
    user = c.fetchone()
    conn.close()
    return user

def get_user_by_id(user_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT id, username, stars, is_admin FROM users WHERE id = ?", (user_id,))
    user = c.fetchone()
    conn.close()
    return user

def add_user(username, password, is_admin=0):
    hashed = hashlib.sha256(password.encode()).hexdigest()
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users (username, password, stars, is_admin) VALUES (?, ?, ?, ?)",
                  (username, hashed, 0, is_admin))
        conn.commit()
        return True
    except:
        return False
    finally:
        conn.close()

def add_stars(user_id, stars, amount_paid):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("UPDATE users SET stars = stars + ? WHERE id = ?", (stars, user_id))
    c.execute("INSERT INTO star_purchases (user_id, stars_added, amount_paid) VALUES (?, ?, ?)",
              (user_id, stars, amount_paid))
    conn.commit()
    conn.close()

def deduct_star(user_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("UPDATE users SET stars = stars - 1 WHERE id = ? AND stars > 0", (user_id,))
    affected = c.rowcount
    conn.commit()
    conn.close()
    return affected > 0

def log_transaction(user_id, receiver, product, status):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO transactions (user_id, receiver, product, status) VALUES (?, ?, ?, ?)",
              (user_id, receiver, product, status))
    conn.commit()
    conn.close()

def get_user_stars(user_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT stars FROM users WHERE id = ?", (user_id,))
    row = c.fetchone()
    conn.close()
    return row[0] if row else 0

def update_user_stars(user_id, new_stars):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("UPDATE users SET stars = ? WHERE id = ?", (new_stars, user_id))
    conn.commit()
    conn.close()

def delete_user(user_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM users WHERE id = ? AND is_admin = 0", (user_id,))
    conn.commit()
    conn.close()

def get_all_users():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT id, username, stars, is_admin FROM users")
    users = c.fetchall()
    conn.close()
    return users

def get_transactions(limit=50):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''SELECT t.id, u.username, t.receiver, t.product, t.status, t.created_at 
                 FROM transactions t JOIN users u ON t.user_id = u.id 
                 ORDER BY t.created_at DESC LIMIT ?''', (limit,))
    rows = c.fetchall()
    conn.close()
    return rows

def get_star_price():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT value FROM settings WHERE key = 'star_price'")
    row = c.fetchone()
    conn.close()
    return float(row[0]) if row else 2.5

def set_star_price(price):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("UPDATE settings SET value = ? WHERE key = 'star_price'", (str(price),))
    conn.commit()
    conn.close()

init_db()

# ======================== واجهة التطبيق الاحترافية ========================
def main(page: ft.Page):
    page.title = "شحن كروت فكه - Hamada Ali"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = ft.Colors.BLACK
    page.window_width = 400
    page.window_height = 700
    page.window_resizable = False
    page.padding = 0

    session_user_id = None
    session_username = None
    session_is_admin = False
    session_user_stars = 0

    def show_snackbar(msg, is_error=False):
        page.snack_bar = ft.SnackBar(
            content=ft.Text(msg, color=ft.Colors.WHITE),
            bgcolor=ft.Colors.RED_400 if is_error else ft.Colors.GREEN_400,
            duration=3000
        )
        page.snack_bar.open = True
        page.update()

    def perform_charge(product_id, product_name, receiver, pin):
        nonlocal session_user_stars
        try:
            seamless_token, msisdn_sender = get_seamless_and_msisdn()
            access_token = get_access_token(seamless_token)
            response = purchase_product(product_id, msisdn_sender, receiver, pin, access_token)

            success = False
            if response.status_code == 200:
                try:
                    resp_json = response.json()
                    if resp_json.get("code") in [None, "0000", "0", "200"]:
                        success = True
                except:
                    success = True
            elif response.status_code in [201, 202, 204]:
                success = True

            if success:
                if deduct_star(session_user_id):
                    session_user_stars -= 1
                    log_transaction(session_user_id, receiver, product_name, "نجاح")
                    show_snackbar(f"✅ تم شحن {product_name} بنجاح")
                    return True
                else:
                    show_snackbar("❌ فشل خصم النجمة", True)
                    return False
            else:
                log_transaction(session_user_id, receiver, product_name, "فشل")
                show_snackbar("❌ فشل الشحن - تأكد من الرقم السري", True)
                return False
        except Exception as e:
            show_snackbar(f"❌ خطأ: {str(e)[:50]}", True)
            return False

    # شاشة تسجيل الدخول
    def login_screen():
        nonlocal session_user_id, session_username, session_is_admin, session_user_stars
        page.controls.clear()

        username_field = ft.TextField(
            hint_text="اسم المستخدم",
            width=300,
            bgcolor=ft.Colors.GREY_900,
            border_radius=30,
            text_align=ft.TextAlign.CENTER,
            prefix_icon=ft.Icons.PERSON,
            color=ft.Colors.WHITE,
        )
        password_field = ft.TextField(
            hint_text="الرقم السري",
            width=300,
            bgcolor=ft.Colors.GREY_900,
            border_radius=30,
            text_align=ft.TextAlign.CENTER,
            prefix_icon=ft.Icons.LOCK,
            password=True,
            can_reveal_password=True,
            color=ft.Colors.WHITE,
        )

        def do_login(e):
            nonlocal session_user_id, session_username, session_is_admin, session_user_stars
            username = username_field.value.strip()
            password = password_field.value

            if not username or not password:
                show_snackbar("❌ أدخل اسم المستخدم والرقم السري", True)
                return

            user = get_user(username)
            if user and user[2] == hashlib.sha256(password.encode()).hexdigest():
                session_user_id = user[0]
                session_username = user[1]
                session_is_admin = user[4] == 1
                session_user_stars = user[3]
                show_snackbar(f"✅ مرحباً {username}")
                if session_is_admin:
                    admin_screen()
                else:
                    main_screen()
            else:
                show_snackbar("❌ اسم المستخدم أو الرقم السري غير صحيح", True)

        page.add(
            ft.Container(
                expand=True,
                gradient=ft.LinearGradient(
                    begin=ft.alignment.top_center,
                    end=ft.alignment.bottom_center,
                    colors=[ft.Colors.BLACK, ft.Colors.GREY_900]
                ),
                content=ft.Column(
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Icon(ft.Icons.PHONE_ANDROID, size=80, color=ft.Colors.AMBER),
                        ft.Text("شحن كروت فكه", size=28, weight=ft.FontWeight.BOLD, color=ft.Colors.AMBER),
                        ft.Text("لأي رقم", size=18, color=ft.Colors.GREY_400),
                        ft.Container(height=40),
                        username_field,
                        ft.Container(height=16),
                        password_field,
                        ft.Container(height=24),
                        ft.ElevatedButton(
                            "دخول",
                            width=200,
                            style=ft.ButtonStyle(
                                bgcolor=ft.Colors.AMBER,
                                color=ft.Colors.BLACK,
                                shape=ft.RoundedRectangleBorder(radius=30),
                            ),
                            on_click=do_login
                        ),
                        ft.Container(height=30),
                        ft.Row(
                            alignment=ft.MainAxisAlignment.CENTER,
                            controls=[
                                ft.Icon(ft.Icons.SUPPORT_AGENT, size=16, color=ft.Colors.GREY_500),
                                ft.Text(f"📞 للشحن والدعم: {SUPPORT_PHONE}", size=12, color=ft.Colors.GREY_500),
                            ]
                        ),
                        ft.Text(f"المطور: {DEVELOPER_NAME} © 2026", size=10, color=ft.Colors.GREY_600),
                    ]
                )
            )
        )
        page.update()

    # الشاشة الرئيسية
    def main_screen():
        page.controls.clear()

        stars_text = ft.Text(f"⭐ {session_user_stars} نجمة", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.AMBER)
        selected_product_index = 0

        product_list = ft.Column()
        for i, product in enumerate(PRODUCTS):
            product_list.controls.append(
                ft.Container(
                    content=ft.Row([
                        ft.Text(product["name"], expand=True, color=ft.Colors.WHITE),
                        ft.Text(f"{product['price']} جنيه", color=ft.Colors.AMBER, weight=ft.FontWeight.BOLD),
                    ]),
                    padding=12,
                    bgcolor=ft.Colors.AMBER_800 if i == 0 else ft.Colors.GREY_900,
                    border_radius=12,
                    margin=ft.margin.only(bottom=8),
                    on_click=lambda e, idx=i: select_product(idx)
                )
            )

        def select_product(idx):
            nonlocal selected_product_index
            selected_product_index = idx
            for i, control in enumerate(product_list.controls):
                control.bgcolor = ft.Colors.AMBER_800 if i == idx else ft.Colors.GREY_900
            page.update()

        receiver_field = ft.TextField(
            hint_text="رقم المستلم (010xxxxxxxx)",
            width=350,
            bgcolor=ft.Colors.GREY_900,
            border_radius=30,
            prefix_icon=ft.Icons.PHONE,
            color=ft.Colors.WHITE,
        )

        pin_field = ft.TextField(
            hint_text="الرقم السري لفودافون كاش (6 أرقام)",
            width=350,
            bgcolor=ft.Colors.GREY_900,
            border_radius=30,
            prefix_icon=ft.Icons.LOCK,
            password=True,
            can_reveal_password=True,
            color=ft.Colors.WHITE,
        )

        def charge_action(e):
            nonlocal session_user_stars
            if session_user_stars < 1:
                show_snackbar("❌ رصيد نجوم غير كافٍ - تواصل مع الأدمن", True)
                return

            receiver = receiver_field.value.strip()
            pin = pin_field.value.strip()

            if not receiver or len(receiver) != 11:
                show_snackbar("❌ أدخل رقم صحيح 11 رقم", True)
                return
            if not pin or len(pin) != 6:
                show_snackbar("❌ أدخل الرقم السري 6 أرقام", True)
                return

            product = PRODUCTS[selected_product_index]

            page.splash = ft.ProgressBar()
            page.update()

            def charge_thread():
                success = perform_charge(product["id"], product["name"], receiver, pin)
                page.splash = None
                if success:
                    stars_text.value = f"⭐ {session_user_stars} نجمة"
                    receiver_field.value = ""
                    pin_field.value = ""
                page.update()

            threading.Thread(target=charge_thread).start()

        page.add(
            ft.Container(
                expand=True,
                gradient=ft.LinearGradient(
                    begin=ft.alignment.top_center,
                    end=ft.alignment.bottom_center,
                    colors=[ft.Colors.BLACK, ft.Colors.GREY_900]
                ),
                content=ft.Column(
                    scroll=ft.ScrollMode.AUTO,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Container(height=10),
                        ft.Row([
                            ft.Text(f"مرحباً {session_username}", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE, expand=True),
                            ft.IconButton(ft.Icons.LOGOUT, icon_color=ft.Colors.RED, on_click=lambda e: login_screen()),
                        ], width=350),
                        ft.Divider(color=ft.Colors.AMBER),
                        ft.Container(
                            content=stars_text,
                            padding=12,
                            bgcolor=ft.Colors.GREY_900,
                            border_radius=15,
                            width=350,
                            alignment=ft.alignment.center,
                        ),
                        ft.Container(height=20),
                        ft.Text("📦 اختر الكارت:", size=16, color=ft.Colors.GREY_400),
                        ft.Container(product_list, width=350),
                        ft.Container(height=15),
                        ft.Text("📱 رقم المستلم:", size=16, color=ft.Colors.GREY_400),
                        receiver_field,
                        ft.Container(height=15),
                        ft.Text("🔐 الرقم السري:", size=16, color=ft.Colors.GREY_400),
                        pin_field,
                        ft.Container(height=20),
                        ft.ElevatedButton(
                            "🔄 شحن الكرت",
                            width=350,
                            height=50,
                            style=ft.ButtonStyle(
                                bgcolor=ft.Colors.AMBER,
                                color=ft.Colors.BLACK,
                                shape=ft.RoundedRectangleBorder(radius=30),
                            ),
                            on_click=charge_action
                        ),
                        ft.Container(height=20),
                        ft.Row(
                            alignment=ft.MainAxisAlignment.CENTER,
                            controls=[
                                ft.Icon(ft.Icons.SUPPORT_AGENT, size=16, color=ft.Colors.GREY_500),
                                ft.Text(f"📞 للشحن والدعم: {SUPPORT_PHONE}", size=12, color=ft.Colors.GREY_500),
                            ]
                        ),
                        ft.Text(f"المطور: {DEVELOPER_NAME}", size=10, color=ft.Colors.GREY_600),
                        ft.Container(height=20),
                    ]
                )
            )
        )
        select_product(0)
        page.update()

    # لوحة تحكم الأدمن
    def admin_screen():
        page.controls.clear()

        star_price = get_star_price()
        users = get_all_users()
        transactions = get_transactions(30)

        users_list = ft.Column()
        for user in users:
            user_id, username, stars, is_admin = user
            if username != session_username:
                users_list.controls.append(
                    ft.Container(
                        content=ft.Row([
                            ft.Text(f"{username} - ⭐{stars}", expand=True, color=ft.Colors.WHITE),
                            ft.IconButton(ft.Icons.ADD, icon_color=ft.Colors.GREEN,
                                on_click=lambda e, uid=user_id, uname=username: add_stars_dialog(uid, uname)),
                            ft.IconButton(ft.Icons.EDIT, icon_color=ft.Colors.BLUE,
                                on_click=lambda e, uid=user_id: edit_stars_dialog(uid)),
                            ft.IconButton(ft.Icons.DELETE, icon_color=ft.Colors.RED,
                                on_click=lambda e, uid=user_id: delete_user_dialog(uid)),
                        ]),
                        padding=8,
                        border=ft.border.all(1, ft.Colors.GREY_800),
                        border_radius=10,
                        margin=2,
                    )
                )

        trans_list = ft.Column()
        for t in transactions[:20]:
            trans_list.controls.append(ft.Text(f"{t[5][:16]} | {t[1]} | {t[3][:20]} | {t[4]}", size=11, color=ft.Colors.GREY_400))

        def add_stars_dialog(user_id, username):
            stars_field = ft.TextField(hint_text="عدد النجوم", width=200)
            def do_add(e):
                try:
                    stars = int(stars_field.value)
                    if stars < MIN_STARS_PURCHASE:
                        show_snackbar(f"❌ الحد الأدنى {MIN_STARS_PURCHASE} نجمة", True)
                        return
                    amount = stars * star_price
                    add_stars(user_id, stars, amount)
                    show_snackbar(f"✅ تم إضافة {stars} نجمة لـ {username} بقيمة {amount} جنيه")
                    admin_screen()
                except:
                    show_snackbar("❌ أدخل رقماً صحيحاً", True)
            page.dialog = ft.AlertDialog(
                title=ft.Text(f"إضافة نجوم لـ {username}"),
                content=ft.Column([stars_field, ft.Text(f"السعر: {star_price} جنيه - الحد الأدنى {MIN_STARS_PURCHASE}")], height=100),
                actions=[ft.TextButton("إضافة", on_click=do_add), ft.TextButton("إلغاء", on_click=lambda e: close_dialog())],
            )
            page.dialog.open = True
            page.update()

        def edit_stars_dialog(user_id):
            stars_field = ft.TextField(hint_text="الرصيد الجديد", width=200)
            def do_set(e):
                try:
                    new_stars = int(stars_field.value)
                    update_user_stars(user_id, new_stars)
                    show_snackbar(f"✅ تم تعديل الرصيد إلى {new_stars} نجمة")
                    admin_screen()
                except:
                    show_snackbar("❌ أدخل رقماً صحيحاً", True)
            page.dialog = ft.AlertDialog(
                title=ft.Text("تعديل الرصيد"),
                content=ft.Column([stars_field], height=80),
                actions=[ft.TextButton("حفظ", on_click=do_set), ft.TextButton("إلغاء", on_click=lambda e: close_dialog())],
            )
            page.dialog.open = True
            page.update()

        def delete_user_dialog(user_id):
            def do_delete(e):
                delete_user(user_id)
                show_snackbar("✅ تم حذف المستخدم")
                admin_screen()
            page.dialog = ft.AlertDialog(
                title=ft.Text("حذف مستخدم"),
                content=ft.Text("هل أنت متأكد؟"),
                actions=[ft.TextButton("حذف", on_click=do_delete), ft.TextButton("إلغاء", on_click=lambda e: close_dialog())],
            )
            page.dialog.open = True
            page.update()

        def change_price_action(e):
            try:
                new_price = float(price_field.value)
                if new_price <= 0:
                    show_snackbar("❌ السعر يجب أن يكون أكبر من 0", True)
                    return
                set_star_price(new_price)
                show_snackbar(f"✅ تم تغيير سعر النجمة إلى {new_price} جنيه")
                admin_screen()
            except:
                show_snackbar("❌ أدخل رقماً صحيحاً", True)

        def add_user_action(e):
            username = new_user_name.value.strip()
            password = new_user_pass.value
            if not username or not password:
                show_snackbar("❌ أدخل اسم المستخدم والرقم السري", True)
                return
            if add_user(username, password):
                show_snackbar(f"✅ تم إضافة المستخدم {username}")
                admin_screen()
            else:
                show_snackbar("❌ اسم المستخدم موجود مسبقاً", True)

        def close_dialog():
            page.dialog.open = False
            page.update()

        price_field = ft.TextField(hint_text="سعر جديد", width=120, border_radius=20)
        new_user_name = ft.TextField(hint_text="اسم المستخدم", width=120, border_radius=20)
        new_user_pass = ft.TextField(hint_text="الرقم السري", width=120, border_radius=20, password=True)

        page.add(
            ft.Container(
                expand=True,
                gradient=ft.LinearGradient(
                    begin=ft.alignment.top_center,
                    end=ft.alignment.bottom_center,
                    colors=[ft.Colors.BLACK, ft.Colors.GREY_900]
                ),
                content=ft.Column(
                    scroll=ft.ScrollMode.AUTO,
                    controls=[
                        ft.Container(height=10),
                        ft.Row([
                            ft.Text("👑 لوحة التحكم", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.AMBER, expand=True),
                            ft.IconButton(ft.Icons.HOME, icon_color=ft.Colors.AMBER, on_click=lambda e: main_screen()),
                            ft.IconButton(ft.Icons.LOGOUT, icon_color=ft.Colors.RED, on_click=lambda e: login_screen()),
                        ], width=350),
                        ft.Divider(color=ft.Colors.AMBER),
                        ft.Text("⚙️ الإعدادات", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.AMBER),
                        ft.Row([ft.Text(f"سعر النجمة حالياً: {star_price} جنيه"), price_field, ft.ElevatedButton("تغيير", on_click=change_price_action)]),
                        ft.Container(height=10),
                        ft.Text("➕ إضافة مستخدم", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.AMBER),
                        ft.Row([new_user_name, new_user_pass, ft.ElevatedButton("إضافة", on_click=add_user_action)]),
                        ft.Container(height=10),
                        ft.Text("👥 المستخدمين", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.AMBER),
                        ft.Container(users_list, height=200, border=ft.border.all(1, ft.Colors.GREY_800), border_radius=10, padding=8),
                        ft.Container(height=10),
                        ft.Text("📊 آخر العمليات", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.AMBER),
                        ft.Container(trans_list, height=150, border=ft.border.all(1, ft.Colors.GREY_800), border_radius=10, padding=8),
                        ft.Container(height=10),
                        ft.Row(
                            alignment=ft.MainAxisAlignment.CENTER,
                            controls=[
                                ft.Icon(ft.Icons.SUPPORT_AGENT, size=16, color=ft.Colors.GREY_500),
                                ft.Text(f"📞 للشحن والدعم: {SUPPORT_PHONE}", size=12, color=ft.Colors.GREY_500),
                            ]
                        ),
                        ft.Text(f"المطور: {DEVELOPER_NAME}", size=10, color=ft.Colors.GREY_600),
                        ft.Container(height=20),
                    ]
                )
            )
        )
        page.update()

    login_screen()

if __name__ == "__main__":
    ft.app(target=main)