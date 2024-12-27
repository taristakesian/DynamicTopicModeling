from telethon import TelegramClient
from telethon.tl.functions.channels import GetFullChannelRequest
from telethon.errors import RPCError
import pandas as pd
import json

from config import API_HASH, API_ID

api_id = API_ID
api_hash = API_HASH

client = TelegramClient('session_name', api_id, api_hash)

async def fetch_channel_data(channel_username):
    try:
        channel = await client.get_entity(channel_username)
        
        # информация о канале
        full_channel = await client(GetFullChannelRequest(channel))
        
        print(f"Канал: {full_channel.chats[0].title}")
        
        data = []  # Хранилище
        
        async for message in client.iter_messages(channel, limit=300):  # Лимит сообщений
            if message.text:  # Пропускаем пустые сообщения
                message_entry = {
                    "title": message.text,
                    "time": message.date.strftime('%Y-%m-%d %H:%M:%S'),
                    "comments": []
                }
                
                if full_channel.full_chat.linked_chat_id:
                    try:
                        async for comment in client.iter_messages(channel, reply_to=message.id):
                            if comment.text:  # Пропускаем пустые
                                comment_entry = {
                                    "comment": comment.text,
                                    "time": comment.date.strftime('%Y-%m-%d %H:%M:%S')
                                }
                                message_entry["comments"].append(comment_entry)
                                
                    except RPCError as e:
                        print(f"Ошибка при получении комментариев: {e}")
                
                data.append(message_entry)
        
        return data
    except RPCError as e:
        print(f"Ошибка при обработке канала: {e}")


# Глобальные темы для сбора
themes = ['politics']

# Список тг каналов
channels = pd.read_csv('data/links_with_com_news.csv')['channel'].to_list()

# Запуск
with client:
    for channel in channels:
        channel_data = client.loop.run_until_complete(fetch_channel_data(channel))  # Укажите username канала

        with open('data_channels/' + channel.split('/')[-1] + '.json', 'w', encoding='utf-8') as f:
            json.dump(channel_data, f, indent=4, ensure_ascii=False)
