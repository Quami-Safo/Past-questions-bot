import os
import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
from google.oauth2 import service_account
from googleapiclient.discovery import build

# Load bot token and service account credentials
BOT_TOKEN = os.environ['BOT_TOKEN']
SERVICE_ACCOUNT_INFO = json.loads(os.environ['SERVICE_ACCOUNT_JSON'])

# Google Drive setup
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
creds = service_account.Credentials.from_service_account_info(SERVICE_ACCOUNT_INFO, scopes=SCOPES)
drive_service = build('drive', 'v3', credentials=creds)

# Set your main root folder ID (e.g., UMAT PAST QUESTIONS folder)
ROOT_FOLDER_ID = '1h4iOLT6ZpQvURAoPkYakCjxDZzbp9BVj'

# --- Telegram Bot Logic ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("1ST SEM 2023", callback_data='1ST_SEM_2023')],
    ]
    await update.message.reply_text("Welcome! Please choose a semester:", reply_markup=InlineKeyboardMarkup(keyboard))

async def handle_semester_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    keyboard = [
        [InlineKeyboardButton("Level 100", callback_data='LEVEL_100')],
        [InlineKeyboardButton("Level 200", callback_data='LEVEL_200')],
        [InlineKeyboardButton("Level 300", callback_data='LEVEL_300')],
    ]
    await query.edit_message_text("Choose a level:", reply_markup=InlineKeyboardMarkup(keyboard))

async def handle_level_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    level = query.data.replace("LEVEL_", "")
    folder_name = f"LEVEL {level} 1ST SEM 2023"

    folder_id = get_folder_id_by_name(ROOT_FOLDER_ID, folder_name)
    if not folder_id:
        await query.edit_message_text("Folder not found.")
        return

    files = list_files_in_folder(folder_id)
    if not files:
        await query.edit_message_text("No files found.")
        return

    message = f"📂 Files in {folder_name}:\n\n"
    for file in files:
        message += f"📄 {file['name']}\n🔗 https://drive.google.com/file/d/{file['id']}\n\n"

    await query.edit_message_text(message)

# --- Google Drive Helper Functions ---

def get_folder_id_by_name(parent_id, name):
    query = f"'{parent_id}' in parents and mimeType='application/vnd.google-apps.folder' and name='{name}'"
    results = drive_service.files().list(q=query, fields="files(id, name)").execute()
    folders = results.get('files', [])
    return folders[0]['id'] if folders else None

def list_files_in_folder(folder_id):
    query = f"'{folder_id}' in parents and mimeType!='application/vnd.google-apps.folder'"
    results = drive_service.files().list(q=query, fields="files(id, name)").execute()
    return results.get('files', [])

# --- Bot Entry Point ---
if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_semester_selection, pattern='^1ST_SEM_2023$'))
    app.add_handler(CallbackQueryHandler(handle_level_selection, pattern='^LEVEL_'))

    app.run_polling()
