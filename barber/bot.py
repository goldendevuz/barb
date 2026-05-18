"""
Barbershop Telegram Bot — Aiogram 3.x
O'zbekcha interfeys, inline keyboard, booking, cancel.
"""
import asyncio
import os
import sys
import django
from datetime import date, timedelta, datetime

# Django sozlamalarini yuklash (bot Django modellarini ishlatadi)
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.conf import settings
from asgiref.sync import sync_to_async

from aiogram import Bot, Dispatcher, F, Router
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import (
    Message, CallbackQuery,
    InlineKeyboardMarkup, InlineKeyboardButton,
    ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, Contact,
)

from barber.models import Barber, Service, Client, Booking

# ─── Router ───────────────────────────────────────────────────────────────────
router = Router()


# ─── FSM States ───────────────────────────────────────────────────────────────
class BookingState(StatesGroup):
    waiting_contact = State()
    choosing_service = State()
    choosing_barber = State()
    choosing_date = State()
    choosing_time = State()
    confirming = State()


# ─── Helpers ──────────────────────────────────────────────────────────────────
def main_menu_kb() -> ReplyKeyboardMarkup:
    """Asosiy menyu klaviaturasi."""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📅 Navbat olish")],
            [KeyboardButton(text="📋 Mening navbatlarim"), KeyboardButton(text="❌ Navbatni bekor qilish")],
            [KeyboardButton(text="ℹ️ Ma'lumot")],
        ],
        resize_keyboard=True,
    )


def contact_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="📱 Raqamni yuborish", request_contact=True)]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


@sync_to_async
def get_or_create_client(tg_id: int, name: str) -> Client:
    client, _ = Client.objects.get_or_create(
        telegram_id=tg_id,
        defaults={'name': name, 'phone': ''},
    )
    return client


@sync_to_async
def update_client_phone(tg_id: int, phone: str):
    Client.objects.filter(telegram_id=tg_id).update(phone=phone)


@sync_to_async
def get_active_services():
    return list(Service.objects.filter(active=True))


@sync_to_async
def get_active_barbers():
    return list(Barber.objects.filter(active=True))


@sync_to_async
def get_client_bookings(tg_id: int):
    client = Client.objects.filter(telegram_id=tg_id).first()
    if not client:
        return []
    return list(
        client.bookings
        .select_related('barber', 'service')
        .exclude(status=Booking.STATUS_CANCELLED)
        .order_by('-date', '-time')[:10]
    )


@sync_to_async
def get_pending_bookings(tg_id: int):
    client = Client.objects.filter(telegram_id=tg_id).first()
    if not client:
        return []
    return list(
        client.bookings
        .select_related('barber', 'service')
        .filter(status__in=[Booking.STATUS_PENDING, Booking.STATUS_CONFIRMED])
        .order_by('date', 'time')
    )


@sync_to_async
def cancel_booking(booking_id: int, tg_id: int) -> bool:
    try:
        booking = Booking.objects.get(id=booking_id, client__telegram_id=tg_id)
        booking.status = Booking.STATUS_CANCELLED
        booking.save()
        return True
    except Booking.DoesNotExist:
        return False


@sync_to_async
def create_booking(tg_id: int, service_id: int, barber_id: int,
                   book_date: date, book_time: str, price: float) -> Booking:
    client = Client.objects.get(telegram_id=tg_id)
    barber = Barber.objects.get(id=barber_id)
    service = Service.objects.get(id=service_id)
    h, m = map(int, book_time.split(':'))
    from datetime import time as dtime
    booking = Booking.objects.create(
        client=client,
        barber=barber,
        service=service,
        date=book_date,
        time=dtime(h, m),
        price=price,
        status=Booking.STATUS_PENDING,
    )
    return booking


@sync_to_async
def get_service(service_id: int) -> Service:
    return Service.objects.get(id=service_id)


@sync_to_async
def get_barber(barber_id: int) -> Barber:
    return Barber.objects.get(id=barber_id)


@sync_to_async
def client_has_phone(tg_id: int) -> bool:
    client = Client.objects.filter(telegram_id=tg_id).first()
    return bool(client and client.phone)


# ─── Keyboards ────────────────────────────────────────────────────────────────
def services_kb(services: list) -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(
            text=f"✂️ {s.name} — {s.price:,.0f} so'm ({s.duration} daq.)",
            callback_data=f"service:{s.id}:{s.price}"
        )]
        for s in services
    ]
    buttons.append([InlineKeyboardButton(text="🔙 Orqaga", callback_data="back:main")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def barbers_kb(barbers: list) -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text=f"💈 {b.name}", callback_data=f"barber:{b.id}")]
        for b in barbers
    ]
    buttons.append([InlineKeyboardButton(text="🔙 Orqaga", callback_data="back:service")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def dates_kb() -> InlineKeyboardMarkup:
    """Keyingi 7 kunni ko'rsatish."""
    today = date.today()
    days_uz = ['Du', 'Se', 'Ch', 'Pa', 'Ju', 'Sh', 'Ya']
    months_uz = [
        '', 'Yan', 'Fev', 'Mar', 'Apr', 'May', 'Iyn',
        'Iyl', 'Avg', 'Sen', 'Okt', 'Noy', 'Dek'
    ]
    buttons = []
    for i in range(7):
        d = today + timedelta(days=i)
        label = f"{'Bugun' if i == 0 else 'Ertaga' if i == 1 else days_uz[d.weekday()]} {d.day} {months_uz[d.month]}"
        buttons.append([InlineKeyboardButton(
            text=label,
            callback_data=f"date:{d.isoformat()}"
        )])
    buttons.append([InlineKeyboardButton(text="🔙 Orqaga", callback_data="back:barber")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def times_kb(chosen_date: str) -> InlineKeyboardMarkup:
    """09:00 dan 18:00 gacha har 30 daqiqada."""
    slots = []
    for h in range(9, 19):
        for m in (0, 30):
            slots.append(f"{h:02d}:{m:02d}")
    rows = []
    for i in range(0, len(slots), 4):
        row = [
            InlineKeyboardButton(text=t, callback_data=f"time:{t}")
            for t in slots[i:i + 4]
        ]
        rows.append(row)
    rows.append([InlineKeyboardButton(text="🔙 Orqaga", callback_data="back:date")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def confirm_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Tasdiqlash", callback_data="confirm:yes"),
            InlineKeyboardButton(text="❌ Bekor", callback_data="confirm:no"),
        ]
    ])


def cancel_bookings_kb(bookings: list) -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(
            text=f"❌ {b.date} {b.time.strftime('%H:%M')} — {b.service.name}",
            callback_data=f"cancel:{b.id}"
        )]
        for b in bookings
    ]
    buttons.append([InlineKeyboardButton(text="🔙 Orqaga", callback_data="back:main")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


# ─── Handlers ─────────────────────────────────────────────────────────────────

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    name = message.from_user.full_name
    tg_id = message.from_user.id
    await get_or_create_client(tg_id, name)

    text = (
        f"🪒 <b>Sartaroshxona botiga xush kelibsiz, {name}!</b>\n\n"
        "Quyidagi menyudan xizmat tanlang:"
    )
    await message.answer(text, reply_markup=main_menu_kb(), parse_mode=ParseMode.HTML)


@router.message(F.text == "ℹ️ Ma'lumot")
async def info_handler(message: Message):
    text = (
        "🪒 <b>Sartaroshxona haqida</b>\n\n"
        "📍 Manzil: Toshkent shahar, Chilonzor tumani\n"
        "📞 Telefon: +998 71 123-45-67\n"
        "🕒 Ish vaqti: 09:00 – 19:00 (Dushanba–Shanba)\n\n"
        "Navbat olish uchun: 📅 <b>Navbat olish</b> tugmasini bosing."
    )
    await message.answer(text, parse_mode=ParseMode.HTML, reply_markup=main_menu_kb())


# ─── Booking Flow ─────────────────────────────────────────────────────────────

@router.message(F.text == "📅 Navbat olish")
async def start_booking(message: Message, state: FSMContext):
    tg_id = message.from_user.id
    has_phone = await client_has_phone(tg_id)

    if not has_phone:
        await state.set_state(BookingState.waiting_contact)
        await message.answer(
            "📱 Iltimos, telefon raqamingizni yuboring:",
            reply_markup=contact_kb(),
        )
        return

    services = await get_active_services()
    if not services:
        await message.answer("⚠️ Hozircha xizmatlar mavjud emas.")
        return

    await state.set_state(BookingState.choosing_service)
    await message.answer(
        "✂️ <b>Xizmat tanlang:</b>",
        reply_markup=services_kb(services),
        parse_mode=ParseMode.HTML,
    )


@router.message(BookingState.waiting_contact, F.contact)
async def handle_contact(message: Message, state: FSMContext):
    phone = message.contact.phone_number
    tg_id = message.from_user.id
    await update_client_phone(tg_id, phone)

    services = await get_active_services()
    if not services:
        await state.clear()
        await message.answer("⚠️ Xizmatlar mavjud emas.", reply_markup=main_menu_kb())
        return

    await state.set_state(BookingState.choosing_service)
    await message.answer(
        f"✅ Raqam saqlandi: <code>{phone}</code>\n\n✂️ <b>Xizmat tanlang:</b>",
        reply_markup=services_kb(services),
        parse_mode=ParseMode.HTML,
    )


@router.message(BookingState.waiting_contact)
async def handle_contact_text(message: Message):
    await message.answer("📱 Iltimos, tugmani bosib raqam yuboring:", reply_markup=contact_kb())


@router.callback_query(F.data.startswith("service:"))
async def choose_service(callback: CallbackQuery, state: FSMContext):
    _, service_id, price = callback.data.split(":")
    await state.update_data(service_id=int(service_id), price=float(price))

    barbers = await get_active_barbers()
    if not barbers:
        await callback.answer("⚠️ Sartaroshlar mavjud emas!", show_alert=True)
        return

    await state.set_state(BookingState.choosing_barber)
    await callback.message.edit_text(
        "💈 <b>Sartarosh tanlang:</b>",
        reply_markup=barbers_kb(barbers),
        parse_mode=ParseMode.HTML,
    )


@router.callback_query(F.data.startswith("barber:"))
async def choose_barber(callback: CallbackQuery, state: FSMContext):
    barber_id = int(callback.data.split(":")[1])
    await state.update_data(barber_id=barber_id)
    await state.set_state(BookingState.choosing_date)
    await callback.message.edit_text(
        "📅 <b>Sanani tanlang:</b>",
        reply_markup=dates_kb(),
        parse_mode=ParseMode.HTML,
    )


@router.callback_query(F.data.startswith("date:"))
async def choose_date(callback: CallbackQuery, state: FSMContext):
    chosen_date = callback.data.split(":")[1]
    await state.update_data(date=chosen_date)
    await state.set_state(BookingState.choosing_time)
    await callback.message.edit_text(
        f"🕐 <b>{chosen_date} uchun vaqt tanlang:</b>",
        reply_markup=times_kb(chosen_date),
        parse_mode=ParseMode.HTML,
    )


@router.callback_query(F.data.startswith("time:"))
async def choose_time(callback: CallbackQuery, state: FSMContext):
    chosen_time = callback.data.split(":")[1] + ":" + callback.data.split(":")[2]
    await state.update_data(time=chosen_time)

    data = await state.get_data()
    service = await get_service(data['service_id'])
    barber = await get_barber(data['barber_id'])

    text = (
        "📋 <b>Buyurtma ma'lumotlari:</b>\n\n"
        f"✂️ Xizmat: <b>{service.name}</b>\n"
        f"💈 Sartarosh: <b>{barber.name}</b>\n"
        f"📅 Sana: <b>{data['date']}</b>\n"
        f"🕐 Vaqt: <b>{chosen_time}</b>\n"
        f"💰 Narx: <b>{service.price:,.0f} so'm</b>\n\n"
        "Tasdiqlaysizmi?"
    )
    await state.set_state(BookingState.confirming)
    await callback.message.edit_text(text, reply_markup=confirm_kb(), parse_mode=ParseMode.HTML)


@router.callback_query(F.data == "confirm:yes")
async def confirm_booking(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    tg_id = callback.from_user.id

    book_date = date.fromisoformat(data['date'])
    booking = await create_booking(
        tg_id=tg_id,
        service_id=data['service_id'],
        barber_id=data['barber_id'],
        book_date=book_date,
        book_time=data['time'],
        price=data['price'],
    )

    await state.clear()
    await callback.message.edit_text(
        f"✅ <b>Navbat muvaffaqiyatli olindi!</b>\n\n"
        f"📋 Buyurtma #{booking.id}\n"
        f"📅 {booking.date} soat {booking.time.strftime('%H:%M')}\n\n"
        "Sartaroshxonaga xush kelibsiz! 🪒",
        parse_mode=ParseMode.HTML,
    )
    await callback.message.answer("Asosiy menyu:", reply_markup=main_menu_kb())


@router.callback_query(F.data == "confirm:no")
async def cancel_confirm(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("❌ Buyurtma bekor qilindi.")
    await callback.message.answer("Asosiy menyu:", reply_markup=main_menu_kb())


# ─── Back Navigation ──────────────────────────────────────────────────────────

@router.callback_query(F.data.startswith("back:"))
async def back_handler(callback: CallbackQuery, state: FSMContext):
    destination = callback.data.split(":")[1]

    if destination == "main":
        await state.clear()
        await callback.message.delete()
        await callback.message.answer("Asosiy menyu:", reply_markup=main_menu_kb())

    elif destination == "service":
        services = await get_active_services()
        await state.set_state(BookingState.choosing_service)
        await callback.message.edit_text(
            "✂️ <b>Xizmat tanlang:</b>",
            reply_markup=services_kb(services),
            parse_mode=ParseMode.HTML,
        )

    elif destination == "barber":
        barbers = await get_active_barbers()
        await state.set_state(BookingState.choosing_barber)
        await callback.message.edit_text(
            "💈 <b>Sartarosh tanlang:</b>",
            reply_markup=barbers_kb(barbers),
            parse_mode=ParseMode.HTML,
        )

    elif destination == "date":
        await state.set_state(BookingState.choosing_date)
        await callback.message.edit_text(
            "📅 <b>Sanani tanlang:</b>",
            reply_markup=dates_kb(),
            parse_mode=ParseMode.HTML,
        )


# ─── My Bookings ──────────────────────────────────────────────────────────────

@router.message(F.text == "📋 Mening navbatlarim")
async def my_bookings(message: Message):
    bookings = await get_client_bookings(message.from_user.id)
    if not bookings:
        await message.answer("📭 Sizda hali buyurtmalar yo'q.", reply_markup=main_menu_kb())
        return

    lines = ["📋 <b>Buyurtmalaringiz:</b>\n"]
    status_icons = {
        Booking.STATUS_PENDING: "⏳",
        Booking.STATUS_CONFIRMED: "✅",
        Booking.STATUS_CANCELLED: "❌",
        Booking.STATUS_DONE: "✔️",
    }
    for b in bookings:
        icon = status_icons.get(b.status, "•")
        lines.append(
            f"{icon} #{b.id} | {b.date} {b.time.strftime('%H:%M')}\n"
            f"   ✂️ {b.service.name} — 💈 {b.barber.name}\n"
            f"   💰 {b.price:,.0f} so'm\n"
        )

    await message.answer("\n".join(lines), parse_mode=ParseMode.HTML, reply_markup=main_menu_kb())


# ─── Cancel Booking ───────────────────────────────────────────────────────────

@router.message(F.text == "❌ Navbatni bekor qilish")
async def cancel_booking_start(message: Message):
    bookings = await get_pending_bookings(message.from_user.id)
    if not bookings:
        await message.answer(
            "📭 Bekor qilish mumkin bo'lgan navbatlar yo'q.",
            reply_markup=main_menu_kb(),
        )
        return

    await message.answer(
        "❌ <b>Qaysi navbatni bekor qilmoqchisiz?</b>",
        reply_markup=cancel_bookings_kb(bookings),
        parse_mode=ParseMode.HTML,
    )


@router.callback_query(F.data.startswith("cancel:"))
async def do_cancel_booking(callback: CallbackQuery):
    booking_id = int(callback.data.split(":")[1])
    success = await cancel_booking(booking_id, callback.from_user.id)

    if success:
        await callback.message.edit_text(f"✅ Navbat #{booking_id} bekor qilindi.")
    else:
        await callback.answer("⚠️ Navbat topilmadi!", show_alert=True)

    await callback.message.answer("Asosiy menyu:", reply_markup=main_menu_kb())


# ─── Main ─────────────────────────────────────────────────────────────────────

async def main():
    token = settings.TELEGRAM_BOT_TOKEN
    if not token:
        print("❌ TELEGRAM_BOT_TOKEN .env faylida topilmadi!")
        return

    bot = Bot(token=token)
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(router)

    print("🤖 Bot ishga tushdi...")
    await dp.start_polling(bot, allowed_updates=["message", "callback_query"])


if __name__ == "__main__":
    asyncio.run(main())
