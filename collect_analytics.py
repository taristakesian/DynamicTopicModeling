import pandas as pd
from config import API_HASH, API_ID
from telethon.sync import TelegramClient
from telethon.tl.functions.channels import GetFullChannelRequest
from telethon.tl.functions.messages import GetHistoryRequest
from telethon.tl.types import Channel
from datetime import datetime, timedelta
from collections import defaultdict
import asyncio
import time
import pytz

links = pd.read_csv('parser/tg_links.csv')
links['new_link'] = 't.me/' + links['link'].str[1:]

api_id = API_ID
api_hash = API_HASH

client = TelegramClient("session_name", api_id, api_hash)

channels = links['new_link'].tolist()

# Временной диапазон (с 2024-10-01 по 2024-11-30)
start_date = pytz.UTC.localize(datetime(2024, 10, 1))
end_date = pytz.UTC.localize(datetime(2024, 11, 30))

analytics = []

def calculate_average(values):
    return sum(values) / len(values) if values else 0

def get_first_post_date(client, channel_entity):
    first_post_date = None
    try:
        messages = client.iter_messages(channel_entity, reverse=True, limit=1)
        for message in messages:
            first_post_date = message.date
            break
    except Exception as e:
        print(f"Ошибка при получении первого сообщения: {e}")
    return first_post_date

# Запуск
with client:
    for channel_name in channels[191:]:
        try:
            channel_entity = client.get_entity(channel_name)
        
            full_channel = client(GetFullChannelRequest(channel_entity))
            messages = client.iter_messages(channel_entity, limit=1000)

            for i in messages:
                if hasattr(i, 'replies') and i.replies is not None and i.replies.replies == 0:
                    comments_open = 1
                else:
                    comments_open = 0
                    
                break
            # Данные для расчета
            total_views = 0
            total_comments = 0
            total_posts = 0
            total_symbols = 0
            first_post_date = get_first_post_date(client, channel_entity)
            
            daily_posts = defaultdict(int)
            for message in messages:
                if message.date and start_date <= message.date <= end_date:
                    post_date = message.date.date()
                    daily_posts[post_date] += 1

                    # Среднее кол-во просмотров
                    total_views += message.views if message.views else 0

                    # Среднее кол-во комментариев
                    total_comments += message.replies.replies if message.replies else 0

                    # Символы в посте
                    total_symbols += len(message.message) if message.message else 0

                    total_posts += 1

            # Рассчитываем параметры
            average_views_per_day = calculate_average(daily_posts.values())
            average_comments = total_comments / total_posts if total_posts else 0
            average_posts_per_day = len(daily_posts) / ((end_date - start_date).days + 1)  # Количество дней в диапазоне
            average_symbols = total_symbols / total_posts if total_posts else 0

            res = {
                "channel": channel_name,
                "comments_open": comments_open,
                "average_views_per_day": average_views_per_day,
                "average_comments": average_comments,
                "subscribers": full_channel.full_chat.participants_count,
                "average_posts_per_day": average_posts_per_day,
                "first_post_date": first_post_date,
                "average_symbols_per_post": average_symbols,
                "group": 'news'
            }
            # Итоговая аналитика для канала
            analytics.append(res)
            print(res)

        except Exception as e:
            print(f"Ошибка для канала {channel_name}: {e}")
            time.sleep(2)


result = pd.DataFrame(analytics)
result.to_csv('tg_channel_analitics2.csv', index=False)