import os
import asyncio
import aiosqlite
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

BOT_TOKEN = os.environ["BOT_TOKEN"]
FSUB_CHANNEL = os.getenv("FSUB_CHANNEL", "")
PUBLIC_CHANNEL = os.getenv("PUBLIC_CHANNEL", "")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

bot = Bot(BOT_TOKEN)
dp = Dispatcher()
DB = "bot.db"

async def db():
    con = await aiosqlite.connect(DB)
    await con.execute("""CREATE TABLE IF NOT EXISTS content(
        code TEXT PRIMARY KEY,
        file_id TEXT NOT NULL,
        caption TEXT
    )""")
    await con.commit()
    return con

async def subscribed(uid: int):
    if not FSUB_CHANNEL:
        return True
    try:
        m = await bot.get_chat_member(FSUB_CHANNEL, uid)
        return m.status in ("member", "administrator", "creator")
    except Exception:
        return False

def join_kb(code):
    u = FSUB_CHANNEL.lstrip("@")
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📢 Join Channel", url=f"https://t.me/{u}")],
        [InlineKeyboardButton(text="✅ Verify", callback_data=f"v:{code}")]
    ])

async def deliver(message, code):
    con = await db()
    cur = await con.execute("SELECT file_id, caption FROM content WHERE code=?", (code,))
    row = await cur.fetchone()
    await con.close()
    if not row:
        await message.answer("❌ Content not found.")
        return
    await message.answer_document(row[0], caption=row[1] or "")

@dp.message(CommandStart())
async def start(message: Message):
    p = message.text.split(maxsplit=1)
    if len(p) == 1:
        await message.answer("👋 Open a valid GET link from the public channel.")
        return
    code = p[1]
    if not await subscribed(message.from_user.id):
        await message.answer("🔒 Join the required channel first.", reply_markup=join_kb(code))
        return
    await deliver(message, code)

@dp.callback_query(F.data.startswith("v:"))
async def verify(c: CallbackQuery):
    code = c.data[2:]
    if not await subscribed(c.from_user.id):
        await c.answer("❌ Please join the channel first.", show_alert=True)
        return
    await c.answer("✅ Verified")
    await deliver(c.message, code)

@dp.message(Command("save"))
async def save_help(message: Message):
    if message.from_user.id != ADMIN_ID:
        return
    await message.answer(
        "Send an authorized file as a document with this caption:\n\n"
        "/save CODE\nTitle / episode"
    )

@dp.message(F.document)
async def save_document(message: Message):
    if message.from_user.id != ADMIN_ID:
        return
    cap = message.caption or ""
    lines = cap.splitlines()
    if not lines or not lines[0].startswith("/save "):
        return
    code = lines[0][6:].strip()
    if not code:
        await message.answer("❌ Missing CODE.")
        return
    title = "\n".join(lines[1:]).strip()
    con = await db()
    await con.execute(
        "INSERT OR REPLACE INTO content(code,file_id,caption) VALUES(?,?,?)",
        (code, message.document.file_id, title)
    )
    await con.commit()
    await con.close()
    me = await bot.get_me()
    link = f"https://t.me/{me.username}?start={code}"
    await message.answer(f"✅ Saved authorized content.\n\n🔗 {link}")

@dp.message(Command("post"))
async def post(message: Message):
    if message.from_user.id != ADMIN_ID:
        return
    if not PUBLIC_CHANNEL:
        await message.answer("Set PUBLIC_CHANNEL first.")
        return
    # Usage: /post CODE\nCaption
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer("Usage: /post CODE")
        return
    code = parts[1].splitlines()[0].strip()
    con = await db()
    cur = await con.execute("SELECT caption FROM content WHERE code=?", (code,))
    row = await cur.fetchone()
    await con.close()
    if not row:
        await message.answer("❌ Save the authorized file first.")
        return
    me = await bot.get_me()
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📥 GET ANIME", url=f"https://t.me/{me.username}?start={code}")]
    ])
    await bot.send_message(
        PUBLIC_CHANNEL,
        f"🎌 {row[0] or 'New Anime'}\n\n👇 Get it here:",
        reply_markup=kb
    )
    await message.answer("✅ Posted to public channel.")

async def main():
    await db()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
