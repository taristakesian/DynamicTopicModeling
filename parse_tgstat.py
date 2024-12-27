from bs4 import BeautifulSoup
import pandas as pd


with open('parser/economica.html', 'r', encoding='utf-8') as file:
    html_content = file.read()

soup = BeautifulSoup(html_content, 'html.parser')

form = soup.find('form', id='category-list-form')
data = []

if form:
    container = form.find('div', class_='row justify-content-center lm-list-container')
    
    if container:
        items = container.find_all('div', class_='col-12 col-sm-6 col-md-4')
        
        for item in items:
            card = item.find('div', class_='card card-body peer-item-box py-2 mb-2 mb-sm-3 border border-info-hover position-relative')
            
            if card:
                links = card.find_all('a', href=True)
                
                if len(links) > 1:
                    second_link = links[1]['href'].split('/')[-1]
                    if second_link[0] == '@': # оставляем открытые каналы
                        data.append(second_link)
                else:
                    print("Нет второй ссылки в элементе")
    else:
        print("Контейнер с классом 'lm-list-container' не найден")
else:
    print("Форма с id 'category-list-form' не найдена")

df = pd.DataFrame(data, columns=['link'])
df.to_csv('tg_links_eco.csv', index=False)