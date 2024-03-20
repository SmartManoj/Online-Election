from pyrogram import Client, StopPropagation, filters
from pyrogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove


from config2 import API_ID, API_HASH, BOT_TOKEN
app = Client("votingBot", bot_token=BOT_TOKEN, api_id=API_ID, api_hash=API_HASH)

import sqlite3
conn = sqlite3.connect('voting.db')

c = conn.cursor()
# Create table
if 0:
    c.execute('''CREATE TABLE IF NOT EXISTS votes
                (id INTEGER PRIMARY KEY, username text, mobile text, aadhaar text, vote text)''')

    # Insert a row of data
    conn.commit();exit()
voting_data = {}
@app.on_message(filters.command(["start"]))
async def start(bot, message):
    name = message.from_user.first_name
    msg = f"Hey {name}, Welcome to The Smart Poll. Please share your mobile number:"
    # reply markup asks the user to share their phone number
    reply_markup=ReplyKeyboardMarkup(
                [
                    [KeyboardButton("Click to share your mobile number", request_contact=True)],
                ],
                resize_keyboard=True,
            )
    await message.reply_text(
        msg, reply_markup=reply_markup
    )
    raise StopPropagation

    

@app.on_message(filters.contact)
async def receive_mobile(bot, message):
    user_id = message.from_user.id
    voting_data[user_id] = {"mobile": message.contact.phone_number}
    await message.reply_text(
        "Thank you. Now, please enter your Aadhaar number:",
        reply_markup = ReplyKeyboardRemove()    
    )
    raise StopPropagation


@app.on_message(filters.regex(r'^[123]$'))
async def receive_vote(bot, message):
    user_id = message.from_user.id
    if user_id in voting_data and "aadhaar" in voting_data[user_id]:
        vote_map = { "1": "I.N.D.I.A.", "2": "NDA", "3": "Others" }
        voting_data[user_id]["vote"] = vote_map[message.text]
        try:
            c = conn.cursor()
            c.execute("INSERT INTO votes (id, username, mobile, aadhaar, vote) VALUES (?, ?, ?, ?, ?)", (user_id, message.from_user.username, voting_data[user_id]["mobile"], voting_data[user_id]["aadhaar"], voting_data[user_id]["vote"]))
            conn.commit()
        except sqlite3.IntegrityError:
            c.close()

        await message.reply_text(
            "Thank you for your vote. Your input has been recorded. Check out the Anonymous poll too https://t.me/SmartManojChannel/1757"
        )
        # Here you can implement storing the vote to a persistent storage
        raise StopPropagation
    
@app.on_message()
async def receive_aadhaar(bot, message):
    user_id = message.from_user.id
    msg = message.text.replace(" ", "")
    if len(msg) != 12 or not msg.isdigit():
        await message.reply_text(
            "Invalid Aadhaar number. Please enter a valid 12-digit Aadhaar number."
        )
        return

    if user_id in voting_data:
        voting_data[user_id]["aadhaar"] = message.text
        await message.reply_text(
            "Received Aadhaar number. Now, vote by choosing a number:\n1. I.N.D.I.A.\n2. NDA\n3. Others"
        )

if __name__ == "__main__":
    print("Starting the bot")
    app.run()
