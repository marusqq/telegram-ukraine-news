import html
import math
import os
from dotenv import load_dotenv
from google.cloud import translate_v2 as translate
from telethon import TelegramClient, events, types

load_dotenv()

# Get those by registering to telegram
api_id = os.getenv('TELEGRAM_API_ID')
api_hash = os.getenv('TELEGRAM_API_HASH')

# Your phone number or bot token
phone_or_bot_token = os.getenv('PHONE_NUMBER')
password = os.getenv('PASSWORD')
target_channel = os.getenv('MY_CHANNEL_ID')

# Create a Telethon client
client = TelegramClient(phone_or_bot_token, api_id, api_hash)


prorussian_info_channels = {
    -1001700501351: "ASTRA",
    -1001263569229: "Старше Эдды",
    -1001135021433: "WarGonzo",
    -1001260622817: 'Readovka',

}

proukrainian_info_channels = {
    -1001792095607: '✙ Груз 200 ✙',
    -1001747601201: 'Віталій Кім / Миколаївська ОДА',
    -1001731636769: 'Батальон «Монако» 💎',
    -1001722167948: 'Pravda Gerashchenko',
    -1001639691719: '3-тя окрема штурмова бригада',
    -1001595772204: 'БУТУСОВ ПЛЮС',
    -1001576917998: 'WarLife 18+ Россия Украина Война 18+',
    -1001494838117: 'Доброго вечора, ми з Одеси 👋🏻',
    -1001318734754: 'Guildhall',
    -1001315043344: 'ЦАПЛІЄНКО_UKRAINE FIGHTS',
    -1001296487842: 'Оперативний ЗСУ',
    -1001280273449: 'Ukraine NOW',
    -1001242446516: 'Україна 24/7 - новини',
    -1001197363285: 'Украина Сейчас: новости, война, Россия',
    -1001161283843: 'СтратКом ЗСУ / AFU StratCom',
    -1001105313000: 'УНИАН - новости Украины | война с Россией | новини України | '
                    'війна з Росією | УНІАН'
}


async def translate_text(text):
    # Create a client using the key file
    client = translate.Client.from_service_account_json('google-creds.json')

    detected_language = client.detect_language(text)
    source_language = detected_language['language']
    target_language = "en"

    print(f'detected language: {source_language}, confidence: {detected_language["confidence"]}')

    if source_language == target_language or source_language == "und":
        return text

    result = client.translate(text, source_language=source_language, target_language=target_language)

    return result["translatedText"]


def split_caption(caption, max_length):
    parts = []
    num_parts = math.ceil(len(caption) / max_length)
    for i in range(num_parts):
        start = i * max_length
        end = start + max_length
        part = caption[start:end]
        parts.append(part)
    return parts


# Define the event handler to process messages
@client.on(events.NewMessage)
async def handle_message(event):
    chat_id = event.message.chat_id
    chat_name = event.message.chat.title

    if chat_id != target_channel:

        print('--------------------------------------------------')
        print(f'message from {chat_id}: {chat_name}')

        # Check if the message contains media
        if event.message.media:
            # Get the text part of the message
            text_part = event.message.message
        else:
            # If there's no media, use the entire text
            text_part = event.message.text

        # Translate the text part
        translated_text = await translate_text(text_part)
        # Handle strange characters
        translated_text = html.unescape(translated_text)

        # make parts from caption
        max_caption_length = 850  # Set the desired maximum caption length
        caption_parts = split_caption(translated_text, max_caption_length)

        # Construct the translated message with media and text
        if chat_id in list(proukrainian_info_channels.keys()):
            flag = "🇺🇦"
        else:
            flag = "🇷🇺"

        # Send each part of the caption with the media to the target channel
        for count, part in enumerate(caption_parts):

            # start of the message
            if len(caption_parts) > 1:
                message = f"{flag} - {chat_name} ({count+1}/{len(caption_parts)}):\n\n"
            else:
                message = f"{flag} - {chat_name}:\n\n"

            message += part

            if count == 0 and event.message.media:
                print(f'file type {type(event.message.media)}')

                # Check if the media is a web page link
                if isinstance(event.message.media, types.MessageMediaWebPage):
                    # Extract the link from MessageMediaWebPage
                    web_page_url = event.message.media.webpage.url
                    message += f"\n\n🔗 Link: {web_page_url}"
                    await client.send_message(target_channel, message)

                # normal attachments - videos / photos etc
                else:
                    await client.send_message(target_channel, message, file=event.message.media)

            else:
                await client.send_message(target_channel, message)


# Start the client
client.start(phone=phone_or_bot_token, password=password)
print('logged in')

# Run the client to start listening for messages
client.run_until_disconnected()
