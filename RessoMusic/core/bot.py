import uvloop
uvloop.install()

from pyrogram import Client, errors, filters
from pyrogram.enums import ChatMemberStatus, ParseMode
import os
import json
import config
from ..logging import LOGGER

# Cloned bots file
CLONED_BOTS_FILE = "cloned_bots.json"
if not os.path.exists(CLONED_BOTS_FILE):
    with open(CLONED_BOTS_FILE, "w") as f:
        json.dump({}, f)

def load_cloned_bots():
    with open(CLONED_BOTS_FILE, "r") as f:
        return json.load(f)

def save_cloned_bots(data):
    with open(CLONED_BOTS_FILE, "w") as f:
        json.dump(data, f, indent=4)

class AMBOTOP(Client):
    def __init__(self):
        LOGGER(__name__).info(f"Starting Bot...")
        super().__init__(
            name="RessoMusic",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            bot_token=config.BOT_TOKEN,
            in_memory=True,
            parse_mode=ParseMode.HTML,
            max_concurrent_transmissions=7,
        )

    async def start(self):
        await super().start()
        self.id = self.me.id
        self.name = self.me.first_name + " " + (self.me.last_name or "")
        self.username = self.me.username
        self.mention = self.me.mention

        try:
            await self.send_message(
                chat_id=config.LOG_GROUP_ID,
                text=f"<u><b>» {self.mention} ʙᴏᴛ sᴛᴀʀᴛᴇᴅ :</b><u>\n\nɪᴅ : <code>{self.id}</code>\nɴᴀᴍᴇ : {self.name}\nᴜsᴇʀɴᴀᴍᴇ : @{self.username}",
            )
        except (errors.ChannelInvalid, errors.PeerIdInvalid):
            LOGGER(__name__).error("Bot has failed to access the log group/channel. Make sure that you have added your bot to your log group/channel.")
            exit()
        except Exception as ex:
            LOGGER(__name__).error(f"Bot has failed to access the log group/channel.\n  Reason : {type(ex).__name__}.")
            exit()

        a = await self.get_chat_member(config.LOG_GROUP_ID, self.id)
        if a.status != ChatMemberStatus.ADMINISTRATOR:
            LOGGER(__name__).error("Please promote your bot as an admin in your log group/channel.")
            exit()
        LOGGER(__name__).info(f"Music Bot Started as {self.name}")

    async def stop(self):
        await super().stop()

# Clone Bot Feature
@app.on_message(filters.command("clone") & filters.private)
async def clone_bot(client, message):
    args = message.text.split()
    if len(args) != 2:
        return await message.reply("Usage: /clone BOT_TOKEN")

    new_bot_token = args[1]
    cloned_bots = load_cloned_bots()
    if new_bot_token in cloned_bots:
        return await message.reply("This bot is already cloned!")

    try:
        new_bot = Client(f"bot_{len(cloned_bots) + 1}", api_id=config.API_ID, api_hash=config.API_HASH, bot_token=new_bot_token)
        new_bot.start()
        new_bot.stop()
        cloned_bots[new_bot_token] = message.from_user.id
        save_cloned_bots(cloned_bots)
        await message.reply("✅ Bot cloned successfully!")
    except Exception as e:
        await message.reply(f"❌ Failed to clone bot:\n{str(e)}")

@app.on_message(filters.command("rmbot") & filters.private)
async def remove_bot(client, message):
    args = message.text.split()
    if len(args) != 2:
        return await message.reply("Usage: /rmbot BOT_TOKEN")
    
    bot_token = args[1]
    cloned_bots = load_cloned_bots()
    if bot_token not in cloned_bots:
        return await message.reply("❌ This bot was not cloned!")

    del cloned_bots[bot_token]
    save_cloned_bots(cloned_bots)
    await message.reply("✅ Cloned bot removed successfully!")

@app.on_message(filters.command("mybot") & filters.private)
async def my_cloned_bots(client, message):
    cloned_bots = load_cloned_bots()
    user_bots = [token for token, user_id in cloned_bots.items() if user_id == message.from_user.id]
    if not user_bots:
        return await message.reply("❌ You have not cloned any bots.")
    bot_list = "\n".join(user_bots)
    await message.reply(f"✅ Your cloned bots:\n`{bot_list}`")

SUDO_USERS = [123456789]  # Replace with your Telegram user ID(s)

@app.on_message(filters.command("cloned") & filters.private)
async def cloned_count(client, message):
    if message.from_user.id not in SUDO_USERS:
        return await message.reply("❌ You are not authorized to use this command.")
    cloned_bots = load_cloned_bots()
    await message.reply(f"✅ Total cloned bots: `{len(cloned_bots)}`")
