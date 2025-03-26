from typing import Final
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import cv2
import requests
import imageio
import people_counter
import io

def get_image():
    c = cv2.VideoCapture(0)
    print(type(c))
    c.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    c.set(cv2.CAP_PROP_FRAME_HEIGHT, 360)
    _, img = c.read()
    c.release()

    if img is None:
        print("Error: Failed to capture image from webcam.")
        return None  # Return None if capture failed

    print(type(img))
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    return img  # Return captured image
# CONNECT TO LIVE FEED
#img = get_image()

TOKEN=''
BOT_USERNAME : Final='@freeseats_bot'

with open("token.txt") as tg_token_file:
		TOKEN = tg_token_file.readline()
async def start_command(update:Update,context:ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("freeseats_bot is alive")


async def help_command(update:Update,context:ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("type /seats to get number of available seats\ntype /view if u want to see image")

async def seat_command(update:Update,context:ContextTypes.DEFAULT_TYPE):
    
    img = get_image()
    if img is None:
        await update.message.reply_text("Failed to capture image from webcam.")
        return

    n=people_counter.count_people(img)

    if(10-n==1):
        await update.message.reply_text(f"There are {n} person in view\nout of 10 visible seating area\nthere is atleast one free seat")
    elif(10-n<=0):
        await update.message.reply_text(
            f"There are {n} person in view\nthere are no free seats")
    else:
        await update.message.reply_text(
            f"There are {n} person in view\nout of 10 visible seating area\nthere are atleast {10-n} free seats")
    await update.message.reply_text("type /view if u want to see image")



async def view_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    #url = "http://127.0.0.1:5000/view"  # Flask API route
    
    try:
        # Send the image from the saved path  open(image_path, 'rb')
        img = get_image()
        if img is None:
            await update.message.reply_text("Failed to capture image from webcam.")
            return

        processed_image=people_counter.process_image(img)
        

        if processed_image is not None:
            # Receive and send the processed image back
            _, img_encoded = cv2.imencode('.jpg', processed_image)
            img_bytes = io.BytesIO(img_encoded.tobytes())
            #await update.message.reply_text("Fhey")
            await update.message.reply_photo(img_bytes)
            
        else:
            await update.message.reply_text("Failed to process the image.")

    except Exception as e:
        await update.message.reply_text(f"Error: {e}")




#handle incoming
def handle_response(text:str)->str:
     text=text.lower()
     if 'hello' in text:
         return "Hi"
     if 'seat' in text:
         return "five?"

     return "I don't understand. Type /help for commands."


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_type = update.message.chat.type
    text: str = update.message.text

    print(f'User {update.message.chat.id} in {message_type}: "{text}"')

    if message_type == 'group':
        if BOT_USERNAME in text:
            new_text: str = text.replace(BOT_USERNAME, '').strip()
            response: str = handle_response(new_text)
        else:
            return
    else:
        response: str = handle_response(text)

    print('Bot:', response)
    await update.message.reply_text(response)


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"Update {update} caused error {context.error}")

# Main Function to Run the Bot
def main():
    app = Application.builder().token(TOKEN).build()

    # Adding command handlers
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("seats", seat_command))
    app.add_handler(CommandHandler("view", view_command))

    # Adding message handler
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Error handler
    app.add_error_handler(error_handler)

    # Start the bot
    print("Bot is running...")
    app.run_polling(poll_interval=5)

if __name__ == "__main__":
    main()