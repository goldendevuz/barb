import logging
from datetime import datetime, timedelta
from aiogram import Router, F
from aiogram.filters import Command
from core.envs import BOT_OWNER_IDS
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    Message,
    CallbackQuery,
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    PreCheckoutQuery,
    LabeledPrice
)
from .api_client import CRMAPIClient

logger = logging.getLogger(__name__)
router = Router()
client = CRMAPIClient()

BOT_OWNER_ID_LIST = [int(x.strip()) for x in BOT_OWNER_IDS.split(",") if x.strip()] or [123456789]

# State definitions for FSM Booking Flow
class BookingStates(StatesGroup):
    searching = State()
    selecting_barbershop = State()
    selecting_service = State()
    selecting_staff = State()
    selecting_time = State()
    confirming = State()


# Helper Keyboards
def get_main_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📅 Yangi Band Qilish"), KeyboardButton(text="📋 Mening Bandliklarim")],
            [KeyboardButton(text="📍 Sartaroshxona Lokatsiyasi"), KeyboardButton(text="🔍 Qidiruv (Filiallar)")],
            [KeyboardButton(text="❌ Bandlikni Bekor Qilish")]
        ],
        resize_keyboard=True
    )


def get_contact_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📱 Telefon raqamni yuborish", request_contact=True)]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )


# ── 1. COMMAND /START & AUTHENTICATION ────────────────────────────────────────

@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    
    # Check deep link start arguments (barber account linking)
    parts = message.text.split(maxsplit=1)
    if len(parts) > 1:
        arg = parts[1].strip()
        if arg.startswith("staff_"):
            try:
                sub_parts = arg.split("_")
                if len(sub_parts) == 3:
                    staff_id = int(sub_parts[1])
                    token = sub_parts[2]
                    
                    await message.answer("🔄 Sartarosh profilingiz bog'lanmoqda...")
                    res = await client.verify_telegram_link(
                        staff_id=staff_id,
                        token=token,
                        telegram_id=message.from_user.id
                    )
                    
                    if res and res.get("success"):
                        await message.answer(
                            f"🎉 Tabriklaymiz, <b>{res.get('staff_name')}</b>!\n\n"
                            f"Sizning Telegram profilingiz CRM tizimiga muvaffaqiyatli bog'landi.\n"
                            f"Endi barcha yangi buyurtmalar va xabarnomalar to'g'ridan-to'g'ri shu yerga keladi! 🪒",
                            parse_mode="HTML",
                            reply_markup=get_main_keyboard()
                        )
                        return
                    else:
                        error_msg = res.get("error") if res else "Ulanish muvaffaqiyatsiz yakunlandi."
                        await message.answer(f"❌ Ulanish xatosi: {error_msg}")
                        return
            except Exception as e:
                logger.error(f"Error handling staff link: {e}")
                await message.answer("❌ Noto'g'ri bog'lanish havolasi.")
                return

    await message.answer(
        "👋 Assalomu alaykum! Barber CRM SaaS tizimiga xush kelibsiz.\n\n"
        "Xizmatlardan foydalanish va uchrashuvlarni band qilish uchun telefon raqamingizni yuboring:",
        reply_markup=get_contact_keyboard()
    )



@router.message(F.contact)
async def process_contact(message: Message):
    contact = message.contact
    telegram_id = message.from_user.id
    first_name = message.from_user.first_name
    
    await message.answer("🔄 Profilingiz tekshirilmoqda...", reply_markup=None)
    
    phone = contact.phone_number
    if not phone.startswith("+"):
        phone = "+" + phone

    customer = await client.get_or_create_customer(
        phone=phone,
        first_name=first_name,
        telegram_id=str(telegram_id)
    )

    if customer:
        await message.answer(
            f"✅ Muvaffaqiyatli bog'landi!\n"
            f"Xush kelibsiz, {customer.get('first_name')}!",
            reply_markup=get_main_keyboard()
        )
    else:
        await message.answer(
            "❌ Tizimga ulanishda xatolik yuz berdi. Iltimos qaytadan urinib ko'ring.",
            reply_markup=get_contact_keyboard()
        )


# ── 2. NEW BOOKING FLOW WITH DYNAMIC TENANT BRANCHES (FSM) ────────────────────

@router.message(F.text == "📅 Yangi Band Qilish")
async def start_booking(message: Message, state: FSMContext):
    await message.answer("🔄 Sartaroshxona filiallari yuklanmoqda...")
    barbershops = await client.get_barbershops()
    
    if not barbershops:
        # Fallback if no branches registered yet
        await message.answer("😔 Hozircha faol sartaroshxona filiallari topilmadi.")
        return

    buttons = []
    for b in barbershops:
        buttons.append([
            InlineKeyboardButton(
                text=f"🏢 {b['name']} ({b['address']})",
                callback_data=f"branch_{b['id']}"
            )
        ])
        
    markup = InlineKeyboardMarkup(inline_keyboard=buttons)
    await state.set_state(BookingStates.selecting_barbershop)
    await message.answer("📍 Iltimos, o'zingizga qulay sartaroshxona filialini tanlang:", reply_markup=markup)


@router.callback_query(F.data.startswith("branch_"))
async def process_barbershop_selection(callback: CallbackQuery, state: FSMContext):
    barbershop_id = int(callback.data.split("_")[1])
    await state.update_data(barbershop_id=barbershop_id)
    
    await callback.message.edit_text("🔄 Ushbu filial xizmatlari yuklanmoqda...")
    services = await client.get_services()
    
    if not services:
        await callback.message.edit_text("😔 Ushbu filialda hozircha xizmatlar mavjud emas.")
        await state.clear()
        return

    buttons = []
    for s in services:
        buttons.append([
            InlineKeyboardButton(
                text=f"💆‍♂️ {s['name']} - {int(float(s['price'])):,} UZS",
                callback_data=f"service_{s['id']}"
            )
        ])
        
    markup = InlineKeyboardMarkup(inline_keyboard=buttons)
    await state.set_state(BookingStates.selecting_service)
    await callback.message.edit_text("💆‍♂️ Iltimos, xizmat turini tanlang:", reply_markup=markup)


# ── 2.5 TEXT-BASED FUZZY SEARCH (BRANCH/BARBER/LOCATION) ──────────────────────

@router.message(F.text == "🔍 Qidiruv (Filiallar)")
async def start_search(message: Message, state: FSMContext):
    await state.set_state(BookingStates.searching)
    await message.answer(
        "🔍 Qidirmoqchi bo'lgan sartaroshxona nomi, usta ismi yoki manzilni yuboring (Masalan: 'Chilonzor' yoki 'Jasur'):"
    )

@router.message(BookingStates.searching)
async def process_search_query(message: Message, state: FSMContext):
    query = message.text.strip().lower()
    if not query:
        await message.answer("Iltimos, haqiqiy qidiruv so'zini kiriting.")
        return
        
    await message.answer("🔄 Qidirilmoqda...")
    
    barbershops = await client.get_barbershops()
    staff_list = await client.get_staff()
    
    matched_branches = []
    
    # Check branches
    for b in barbershops:
        if query in b["name"].lower() or query in b["address"].lower():
            matched_branches.append(b)
            
    # Check staff
    for s in staff_list:
        full_name = f"{s['first_name']} {s['last_name']}".lower()
        if query in full_name:
            branch_id = s.get("barbershop")
            if branch_id:
                branch = next((b for b in barbershops if b["id"] == branch_id), None)
                if branch and branch not in matched_branches:
                    matched_branches.append(branch)

    if not matched_branches:
        await message.answer(
            "😔 Kechirasiz, mos keluvchi sartaroshxona yoki usta topilmadi. Qayta urinib ko'ring:",
            reply_markup=get_main_keyboard()
        )
        await state.clear()
        return

    await message.answer(f"🎉 {len(matched_branches)} ta filial topildi:")
    for b in matched_branches:
        buttons = [
            [InlineKeyboardButton(text="💆‍♂️ Xizmatlar va Band Qilish", callback_data=f"branch_{b['id']}")]
        ]
        if b.get("latitude") and b.get("longitude"):
            buttons.append([InlineKeyboardButton(text="📍 Xaritada ko'rish", callback_data=f"mappin_{b['id']}")])
            
        markup = InlineKeyboardMarkup(inline_keyboard=buttons)
        
        info_text = (
            f"🏢 <b>{b['name']}</b>\n"
            f"📍 Manzil: {b['address']}\n"
        )
        await message.answer(info_text, reply_markup=markup, parse_mode="HTML")
        
    await state.clear()


@router.callback_query(F.data.startswith("mappin_"))
async def process_mappin_callback(callback: CallbackQuery):
    barbershop_id = int(callback.data.split("_")[1])
    barbershops = await client.get_barbershops()
    branch = next((b for b in barbershops if b["id"] == barbershop_id), None)
    if branch and branch.get("latitude") and branch.get("longitude"):
        await callback.message.reply_location(
            latitude=float(branch["latitude"]),
            longitude=float(branch["longitude"])
        )
        await callback.answer()
    else:
        await callback.answer("😔 Ushbu filial lokatsiyasi kiritilmagan.", show_alert=True)


# ── 2.6 BOT OWNER ADMIN COMMANDS (STATS & ANNOUNCEMENTS) ──────────────────────

@router.message(Command("bot_stats"))
async def cmd_bot_stats(message: Message):
    if message.from_user.id not in BOT_OWNER_ID_LIST:
        await message.answer("❌ Kechirasiz, siz bot egasi emassiz.")
        return
        
    await message.answer("🔄 Tizim statistikasi yuklanmoqda...")
    stats = await client.get_global_stats()
    if not stats:
        await message.answer("❌ Statistikani yuklab bo'lmadi.")
        return
        
    text = (
        "📊 <b>BARBER CRM GLOBAL STATISTIKASI</b>\n\n"
        f"🏢 Filiallar soni: <b>{stats['total_branches']} ta</b>\n"
        f"💇‍♂️ Sartaroshlar soni: <b>{stats['total_barbers']} ta</b>\n"
        f"👥 Ro'yxatdan o'tgan mijozlar: <b>{stats['total_clients']} ta</b>\n"
        f"📅 Jami bandliklar soni: <b>{stats['total_bookings']} ta</b>\n"
        f"💰 Jami tushgan to'lov: <b>{stats['total_revenue']:,} UZS</b>\n"
    )
    await message.answer(text, parse_mode="HTML")


@router.message(Command("broadcast"))
async def cmd_broadcast(message: Message):
    if message.from_user.id not in BOT_OWNER_ID_LIST:
        await message.answer("❌ Kechirasiz, siz bot egasi emassiz.")
        return
        
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer("⚠️ Iltimos xabarni yozing. Masalan:\n<code>/broadcast Yangi yil chegirmalari boshlandi!</code>", parse_mode="HTML")
        return
        
    broadcast_text = parts[1]
    await message.answer("📢 Xabarni barcha mijozlarga yuborish boshlandi...")
    
    clients = await client.get_clients()
    success_count = 0
    fail_count = 0
    
    for c in clients:
        tel_id = c.get("telegram_id")
        if tel_id:
            try:
                await message.bot.send_message(
                    chat_id=int(tel_id),
                    text=f"📢 <b>ADMIN XABARI:</b>\n\n{broadcast_text}",
                    parse_mode="HTML"
                )
                success_count += 1
            except Exception as e:
                fail_count += 1
                
    await message.answer(
        f"✅ <b>E'lon yuborish yakunlandi!</b>\n\n"
        f"🟢 Muvaffaqiyatli: {success_count} ta mijozga\n"
        f"🔴 Muammoli/Bloklangan: {fail_count} ta",
        parse_mode="HTML"
    )



@router.callback_query(BookingStates.selecting_service, F.data.startswith("service_"))
async def process_service_selection(callback: CallbackQuery, state: FSMContext):
    service_id = int(callback.data.split("_")[1])
    await state.update_data(service_id=service_id)
    
    await callback.message.edit_text("🔄 Filial sartaroshlari ro'yxati yuklanmoqda...")
    staff_list = await client.get_staff()
    
    data = await state.get_data()
    # Filter staff belonging to this barbershop branch!
    branch_staff = [
        staff for staff in staff_list 
        if not staff.get("barbershop") or staff.get("barbershop") == data["barbershop_id"]
    ]
    
    if not branch_staff:
        # Fallback to all staff if none explicitly restricted to branch
        branch_staff = staff_list

    if not branch_staff:
        await callback.message.edit_text("😔 Ushbu filialda hozircha sartaroshlar topilmadi.")
        await state.clear()
        return

    buttons = []
    for staff in branch_staff:
        buttons.append([
            InlineKeyboardButton(
                text=f"💇‍♂️ {staff['first_name']} {staff['last_name']}".strip(),
                callback_data=f"staff_{staff['id']}"
            )
        ])
        
    markup = InlineKeyboardMarkup(inline_keyboard=buttons)
    await state.set_state(BookingStates.selecting_staff)
    await callback.message.edit_text("✂️ Iltimos, sartaroshingizni tanlang:", reply_markup=markup)


@router.callback_query(BookingStates.selecting_staff, F.data.startswith("staff_"))
async def process_staff_selection(callback: CallbackQuery, state: FSMContext):
    staff_id = int(callback.data.split("_")[1])
    await state.update_data(staff_id=staff_id)
    
    # Generate scheduled/working slots
    slots = []
    now = datetime.now()
    
    # Generate slots for today and tomorrow
    for day_offset in [0, 1]:
        target_date = now + timedelta(days=day_offset)
        for hour in [10, 12, 14, 16, 18]:
            slot_time = target_date.replace(hour=hour, minute=0, second=0, microsecond=0)
            if slot_time > now:
                slots.append(slot_time)

    if not slots:
        await callback.message.edit_text("😔 Afsuski, bugun va ertaga bo'sh vaqtlar qolmadi.")
        await state.clear()
        return

    buttons = []
    for idx, slot in enumerate(slots[:6]):
        day_str = "Bugun" if slot.date() == now.date() else "Ertaga"
        time_str = slot.strftime("%H:%M")
        buttons.append([
            InlineKeyboardButton(
                text=f"📅 {day_str} ({time_str})",
                callback_data=f"time_{idx}_{slot.isoformat()}"
            )
        ])
        
    markup = InlineKeyboardMarkup(inline_keyboard=buttons)
    await state.set_state(BookingStates.selecting_time)
    await callback.message.edit_text("⏰ Qulay uchrashuv vaqtini tanlang:", reply_markup=markup)


@router.callback_query(BookingStates.selecting_time, F.data.startswith("time_"))
async def process_time_selection(callback: CallbackQuery, state: FSMContext):
    data_parts = callback.data.split("_")
    iso_time = data_parts[2]
    await state.update_data(start_time=iso_time)
    
    data = await state.get_data()
    await callback.message.edit_text("🔄 Uchrashuv band qilinmoqda...")
    
    telegram_id = callback.from_user.id
    customer = await client.get_or_create_customer(
        phone="",
        first_name=callback.from_user.first_name,
        telegram_id=str(telegram_id)
    )
    
    if not customer:
        await callback.message.answer("❌ Profilingiz topilmadi, iltimos /start bosing.")
        await state.clear()
        return

    res = await client.create_booking(
        customer_id=customer["id"],
        staff_id=data["staff_id"],
        service_id=data["service_id"],
        start_time=data["start_time"],
        barbershop_id=data["barbershop_id"]
    )
    
    if res:
        appt_time = datetime.fromisoformat(res["start_time"]).strftime("%H:%M (%d-%b)")
        price_uzs = int(float(res.get("service_detail", {}).get("price", 0)))
        
        # Calculate Stars: 1 Star = 200 UZS
        stars_price = int(price_uzs / 200)
        if stars_price < 1:
            stars_price = 1

        # Keep appt_id in state to support Stars Payment
        await state.update_data(appt_id=res["id"], stars_amount=stars_price, service_name=res.get("service_detail", {}).get("name"))

        buttons = [
            [InlineKeyboardButton(text="⭐ Telegram Stars orqali to'lash", callback_data=f"paystars_{res['id']}")],
            [InlineKeyboardButton(text="💵 Keyinroq to'lash", callback_data="paylater")]
        ]
        markup = InlineKeyboardMarkup(inline_keyboard=buttons)

        await callback.message.edit_text(
            f"🎉 Band qilish muvaffaqiyatli yaratildi!\n\n"
            f"🆔 Bandlik ID: #{res['id']}\n"
            f"🏢 Filial: {res.get('barbershop', 'Tanlangan filial')}\n"
            f"💇‍♂️ Usta: {res.get('staff_detail', {}).get('first_name', 'Usta')}\n"
            f"💆‍♂️ Xizmat: {res.get('service_detail', {}).get('name', 'Xizmat')}\n"
            f"⏰ Vaqt: {appt_time}\n"
            f"💵 Narxi: {price_uzs:,} UZS ({stars_price} ⭐ Stars)\n\n"
            f"Sizda hoziroq Telegram Stars orqali to'lovni oldindan amalga oshirish imkoniyati mavjud:",
            reply_markup=markup
        )
    else:
        await callback.message.edit_text(
            "❌ Uchrashuvni band qilishda xatolik yuz berdi. Iltimos qaytadan urinib ko'ring."
        )
        await state.clear()


# ── 3. TELEGRAM STARS PAYMENT INTEGRATION ─────────────────────────────────────

@router.callback_query(F.data.startswith("paystars_"))
async def process_stars_invoice(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    appt_id = int(callback.data.split("_")[1])
    stars_amount = data.get("stars_amount", 50)
    service_name = data.get("service_name", "Barber Xizmati")
    
    await callback.message.answer("💸 To'lov hisob-fakturasi tayyorlanmoqda...")
    
    # Send Invoice using Telegram Stars (Currency code: XTR)
    await callback.bot.send_invoice(
        chat_id=callback.message.chat.id,
        title=f"💇‍♂️ {service_name}",
        description=f"#{appt_id} sonli uchrashuv to'lovi uchun Telegram Stars invoices",
        payload=f"appt_payment_{appt_id}",
        provider_token="", # Empty for Telegram Stars payments
        currency="XTR",
        prices=[LabeledPrice(label="Telegram Stars", amount=stars_amount)],
        start_parameter="pay_stars"
    )
    await callback.answer()
    await state.clear()


@router.callback_query(F.data == "paylater")
async def process_pay_later(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(
        "👍 Qabul qilindi! To'lovni sartaroshxonada joyida amalga oshirishingiz mumkin. Kutib qolamiz!",
        reply_markup=get_main_keyboard()
    )
    await state.clear()


# Pre-checkout query handler to auto-approve payments
@router.pre_checkout_query()
async def process_pre_checkout(pre_checkout_query: PreCheckoutQuery):
    await pre_checkout_query.answer(ok=True)


# Successful payment handler
@router.message(F.successful_payment)
async def process_successful_payment(message: Message):
    payload = message.successful_payment.invoice_payload
    appt_id = int(payload.split("_")[2])
    
    # Confirm booking in the CRM
    res = await client.transition_booking(appt_id, "confirmed")
    
    stars_charged = message.successful_payment.total_amount
    uzs_equivalent = stars_charged * 200

    await message.answer(
        f"⭐ <b>To'lov muvaffaqiyatli qabul qilindi!</b>\n\n"
        f"💳 To'langan: {stars_charged} Stars (~{uzs_equivalent:,} UZS)\n"
        f"📅 Buyurtma #{appt_id} holati avtomatik ravishda <b>TASDIQLANDI</b>.\n"
        f"Ishonchingiz uchun rahmat! Sartaroshxonada sizni kutamiz.",
        parse_mode="HTML",
        reply_markup=get_main_keyboard()
    )


# ── 4. LOCATION BASED BRANCHES LIST ───────────────────────────────────────────

@router.message(F.text == "📍 Sartaroshxona Lokatsiyasi")
async def cmd_location(message: Message):
    barbershops = await client.get_barbershops()
    if not barbershops:
        await message.answer("😔 Hozircha faol filiallar lokatsiyalari mavjud emas.")
        return

    buttons = []
    for b in barbershops:
        buttons.append([
            InlineKeyboardButton(
                text=f"📍 {b['name']}",
                callback_data=f"loc_{b['id']}"
            )
        ])
    markup = InlineKeyboardMarkup(inline_keyboard=buttons)
    await message.answer("Qaysi filialning xaritadagi joylashuvini ko'rishni xohlaysiz?", reply_markup=markup)


@router.callback_query(F.data.startswith("loc_"))
async def process_location_query(callback: CallbackQuery):
    branch_id = int(callback.data.split("_")[1])
    barbershops = await client.get_barbershops()
    
    branch = next((b for b in barbershops if b["id"] == branch_id), None)
    if not branch:
        await callback.message.edit_text("❌ Filial topilmadi.")
        return

    # If coords are not filled, use standard center city values
    lat = float(branch.get("latitude")) if branch.get("latitude") else 41.311081
    lng = float(branch.get("longitude")) if branch.get("longitude") else 69.240562

    await callback.message.delete()
    
    # Send active location coordinates directly!
    await callback.message.answer_location(
        latitude=lat,
        longitude=lng
    )
    await callback.message.answer(
        f"🏢 <b>{branch['name']}</b>\n"
        f"📍 Manzil: {branch['address']}\n"
        f"Tashrifingizni kutamiz!",
        parse_mode="HTML",
        reply_markup=get_main_keyboard()
    )


# ── 5. LIST AND CANCEL BOOKINGS ───────────────────────────────────────────────

@router.message(F.text == "📋 Mening Bandliklarim")
async def show_bookings(message: Message):
    telegram_id = message.from_user.id
    bookings = await client.get_upcoming_bookings(str(telegram_id))
    
    if not bookings:
        await message.answer("🤷‍♂️ Sizda hozircha yaqin orada faol bandliklar yo'q.")
        return
        
    text = "📋 <b>Sizning yaqin oradagi bandliklaringiz:</b>\n\n"
    for b in bookings:
        appt_time = datetime.fromisoformat(b["start_time"]).strftime("%d-%b, %H:%M")
        text += (
            f"📌 <b>ID: #{b['id']}</b>\n"
            f"🏢 Filial: {b.get('barbershop', {}).get('name') if isinstance(b.get('barbershop'), dict) else 'Filial'}\n"
            f"💆‍♂️ Xizmat: {b.get('service_detail', {}).get('name')}\n"
            f"💇‍♂️ Usta: {b.get('staff_detail', {}).get('first_name')}\n"
            f"⏰ Vaqt: {appt_time}\n"
            f"📈 Holati: {b['status'].upper()}\n\n"
        )
        
    await message.answer(text, parse_mode="HTML")


@router.message(F.text == "❌ Bandlikni Bekor Qilish")
async def cancel_booking_list(message: Message):
    telegram_id = message.from_user.id
    bookings = await client.get_upcoming_bookings(str(telegram_id))
    
    if not bookings:
        await message.answer("🤷‍♂️ Bekor qilish uchun faol bandliklar topilmadi.")
        return
        
    buttons = []
    for b in bookings:
        appt_time = datetime.fromisoformat(b["start_time"]).strftime("%d-%b %H:%M")
        buttons.append([
            InlineKeyboardButton(
                text=f"❌ ID: #{b['id']} ({appt_time})",
                callback_data=f"cancel_{b['id']}"
            )
        ])
        
    markup = InlineKeyboardMarkup(inline_keyboard=buttons)
    await message.answer("Bekor qilmoqchi bo'lgan bandligingizni tanlang:", reply_markup=markup)


@router.callback_query(F.data.startswith("cancel_"))
async def process_booking_cancellation(callback: CallbackQuery):
    booking_id = int(callback.data.split("_")[1])
    res = await client.transition_booking(booking_id, "cancelled")
    
    if res:
        await callback.message.edit_text(
            f"✅ Bandlik #{booking_id} muvaffaqiyatli bekor qilindi.\n"
            f"Qayta band qilish uchun xohlagan vaqtingizda murojaat qiling!"
        )
    else:
        await callback.message.edit_text("❌ Bandlikni bekor qilish imkoni bo'lmadi. Iltimos administrator bilan bog'laning.")
