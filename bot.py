from aiogram import Dispatcher, executor, Bot, types
from config import TOKEN, client_id, client_secret, subdomain, redirect_url
from kbs import links_kb
from amocrm.v2 import tokens
from amocrm.v2.entity.lead import Lead
from pathlib import Path
import time
import os


#Время, от которого будем высчитывать, обновлять deal_list или нет (раз в  5 мин = 300 сек)
bot = Bot(TOKEN)
dp = Dispatcher(bot)


#Получить словарь из всех сделок
def get_deal_list():
    try:
        #Get Auth code
        with open(r"tokens/refresh_token.txt") as f:
            auth_code = f.readline()

        #Auth
        tokens.default_token_manager(
            client_id=client_id,
            client_secret=client_secret,
            subdomain=subdomain,
            redirect_url=redirect_url,
            storage=tokens.FileTokensStorage(directory_path=os.path.join(str(Path.cwd()), "tokens")),  # by default FileTokensStorage
        )
        tokens.default_token_manager.init(code=auth_code, skip_error=True)


        #Get Deal List
        deal_list = {}
        for deal in Lead.objects.all():
            deal_list[deal.name] = deal.price
    except: 
        deal_list = "Произошла ошибка на сервере🫤"


    return deal_list



first_time = time.time() 
deal_list = get_deal_list()



# /start
@dp.message_handler(commands=["start", "help"])
async def start_process(msg):
    text = "У нашего бота вы можете узнать местонахождение вашего товара! 🌍 \n\nВыберите действие 🔽"
    await msg.answer(text, reply_markup=links_kb)


# /tracker
@dp.message_handler(commands=["tracker"])
async def tracker_process(msg):
    text = "ВВЕДИТЕ МАРКЕР ТОВАРА 📦"
    await msg.answer(text)




# Обработчик маркера
@dp.message_handler(content_types=["text"])
async def get_marker_process(msg):
    global deal_list, first_time

    marker = msg.text
    second_time = time.time()


    #Если прошло 180 сек с последнего обновления базы
    if (second_time - first_time >= 180):  
        first_time = second_time
        deal_list = get_deal_list() #dict
    

    #Находим нужную запись, если не произошло ошибок
    if str(type(deal_list)) != "<class 'str'>":
        deal_price = deal_list.get(marker, "⚠️ Неправильно введен маркер товара! ⚠️")
    else:
        deal_price = "Произошла ошибка на сервере🫤"

    await msg.answer(deal_price)





# Callback кнопки "Местонахождение товара"
@dp.callback_query_handler(text="product_location") #text - То, что отправили с кнопкой
async def product_location(call):
    await tracker_process(call.message)
    await call.answer()  # Обязательно



if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)