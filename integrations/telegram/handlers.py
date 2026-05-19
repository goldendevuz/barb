import logging
from datetime import datetime, timedelta
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    Message,
    CallbackQuery,
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)
from .api_client import CRMAPIClient

logger = logging.getLogger(__name__)
router = Router()
client = CRMAPIClient()

# State definitions for FSM Booking Flow
class BookingStates(StatesGroup):
    selecting_service = State()
    selecting_staff = State()
    selecting_time = State()
    confirming = State()


# Helper Keyboards
def get_main_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📅 Yangi Band Qilish"), KeyboardButton(text="📋 Mening Bandliklarim")],
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
    await message.answer(
        "👋 Assalomu alaykum! Barber CRM tizimiga xush kelibsiz.\n\n"
        "Xizmatlardan foydalanish uchun telefon raqamingizni yuboring:",
        reply_markup=get_contact_keyboard()
    )


@router.message(F.contact)
async def process_contact(message: Message):
    contact = message.contact
    telegram_id = message.from_user.id
    first_name = message.from_user.first_name
    
    await message.answer("🔄 Profilingiz tekshirilmoqda...", reply_markup=None)
    
    # Clean phone number (add + if missing)
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


# ── 2. NEW BOOKING FLOW (FSM) ──────────────────────────────────────────────────

@router.message(F.text == "📅 Yangi Band Qilish")
async def start_booking(message: Message, state: FSMContext):
    await message.answer("🔄 Xizmatlar yuklanmoqda...")
    services = await client.get_services()
    
    if not services:
        await message.answer("😔 Hozirda mavjud xizmatlar topilmadi.")
        return

    # Generate inline options for services
    buttons = []
    for s in services:
        buttons.append([
            InlineKeyboardButton(
                text=f"{s['name']} - {int(float(s['price'])):,} UZS",
                callback_data=f"service_{s['id']}"
            )
        ])
        
    markup = InlineKeyboardMarkup(inline_keyboard=buttons)
    await state.set_state(BookingStates.selecting_service)
    await message.answer("💆‍♂️ Iltimos, xizmat turini tanlang:", reply_markup=markup)


@router.callback_query(BookingStates.selecting_service, F.data.startswith("service_"))
async def process_service_selection(callback: CallbackQuery, state: FSMContext):
    service_id = int(callback.data.split("_")[1])
    await state.update_data(service_id=service_id)
    
    await callback.message.edit_text("🔄 Ustalar ro'yxati yuklanmoqda...")
    staff_list = await client.get_staff()
    
    if not staff_list:
        await callback.message.edit_text("😔 Hozirda ishlayotgan ustalar mavjud emas.")
        await state.clear()
        return

    buttons = []
    for staff in staff_list:
        buttons.append([
            InlineKeyboardButton(
                text=f"💇‍♂️ {staff['first_name']} {staff['last_name']}".strip(),
                callback_data=f"staff_{staff['id']}"
            )
        ])
        
    markup = InlineKeyboardMarkup(inline_keyboard=buttons)
    await state.set_state(BookingStates.selecting_staff)
    await callback.message.edit_text("✂️ Iltimos, ustangizni tanlang:", reply_markup=markup)


@router.callback_query(BookingStates.selecting_staff, F.data.startswith("staff_"))
async def process_staff_selection(callback: CallbackQuery, state: FSMContext):
    staff_id = int(callback.data.split("_")[1])
    await state.update_data(staff_id=staff_id)
    
    # Generate mock available slots for booking simplicity & reliability
    # In a fully granular system, these slots are dynamic based on calendar availability.
    slots = []
    now = datetime.now()
    
    # Generate 4 hour slots for today and tomorrow
    start_hour = 10
    for day_offset in [0, 1]:
        target_date = now + timedelta(days=day_offset)
        # Avoid generating passed slots for today
        for hour in [10, 12, 14, 16, 18]:
            slot_time = target_date.replace(hour=hour, minute=0, second=0, microsecond=0)
            if slot_time > now:
                slots.append(slot_time)

    if not slots:
        await callback.message.edit_text("😔 Afsuski, bugun va ertaga bo'sh vaqtlar qolmadi.")
        await state.clear()
        return

    buttons = []
    # Limit to top 6 slots to keep keyboard clean
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
    await callback.message.edit_text("⏰ Band qilish vaqtini tanlang:", reply_markup=markup)


@router.callback_query(BookingStates.selecting_time, F.data.startswith("time_"))
async def process_time_selection(callback: CallbackQuery, state: FSMContext):
    data_parts = callback.data.split("_")
    iso_time = data_parts[2]
    await state.update_data(start_time=iso_time)
    
    # Read all collected state details
    data = await state.get_data()
    
    await callback.message.edit_text("🔄 Bandlik tasdiqlanmoqda...")
    
    # Fetch customer
    telegram_id = callback.from_user.id
    customer = await client.get_or_create_customer(
        phone="", # Fetch already linked
        first_name=callback.from_user.first_name,
        telegram_id=str(telegram_id)
    )
    
    if not customer:
        await callback.message.answer("❌ Profilingiz topilmadi, iltimos /start bosing.")
        await state.clear()
        return

    # Call backend booking creation
    res = await client.create_booking(
        customer_id=customer["id"],
        staff_id=data["staff_id"],
        service_id=data["service_id"],
        start_time=data["start_time"]
    )
    
    if res:
        appt_time = datetime.fromisoformat(res["start_time"]).strftime("%H:%M (%d-%b)")
        await callback.message.edit_text(
            f"🎉 Muvaffaqiyatli band qilindi!\n\n"
            f"🆔 Bandlik ID: #{res['id']}\n"
            f"💇‍♂️ Usta: {res.get('staff_detail', {}).get('first_name', 'Tanlangan usta')}\n"
            f"💆‍♂️ Xizmat: {res.get('service_detail', {}).get('name', 'Tanlangan xizmat')}\n"
            f"⏰ Vaqt: {appt_time}\n"
            f"💵 Narxi: {int(float(res.get('service_detail', {}).get('price', 0))):,} UZS\n\n"
            f"Sizni kutib qolamiz!"
        )
    else:
        await callback.message.edit_text(
            "❌ Band qilish jarayonida xatolik yuz berdi. Iltimos keyinroq qaytadan urinib ko'ring."
        )
        
    await state.clear()


# ── 3. LIST BOOKINGS ───────────────────────────────────────────────────────────

@router.message(F.text == "📋 Mening Bandliklarim")
async def show_bookings(message: Message):
    telegram_id = message.from_user.id
    bookings = await client.get_upcoming_bookings(str(telegram_id))
    
    if not bookings:
        await message.answer("🤷‍♂️ Sizda hozircha yaqin orada hech qanday faol bandliklar yo'q.")
        return
        
    text = "📋 <b>Sizning yaqin oradagi bandliklaringiz:</b>\n\n"
    for b in bookings:
        appt_time = datetime.fromisoformat(b["start_time"]).strftime("%d-%b, %H:%M")
        text += (
            f"📌 <b>ID: #{b['id']}</b>\n"
            f"💆‍♂️ Xizmat: {b.get('service_detail', {}).get('name')}\n"
            f"💇‍♂️ Usta: {b.get('staff_detail', {}).get('first_name')}\n"
            f"⏰ Vaqt: {appt_time}\n"
            f"📈 Holati: {b['status'].upper()}\n\n"
        )
        
    await message.answer(text, parse_mode="HTML")


# ── 4. CANCEL BOOKING FLOW ─────────────────────────────────────────────────────

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
    
    # Attempt cancellation via state machine transition to 'cancelled'
    res = await client.transition_booking(booking_id, "cancelled")
    
    if res:
        await callback.message.edit_text(
            f"✅ Bandlik #{booking_id} muvaffaqiyatli bekor qilindi.\n"
            f"Pul qaytarish yoki boshqa ma'lumotlar uchun operatorimiz bilan bog'laning."
        )
    else:
        await callback.message.edit_text("❌ Bandlikni bekor qilish imkoni bo'lmadi. Iltimos administrator bilan bog'laning.")
