from aiogram import Dispatcher, executor, Bot, types
from config import TOKEN, client_id, client_secret, subdomain, redirect_url
from kbs import links_kb
from amocrm.v2 import tokens
from amocrm.v2.entity.lead import Lead
from amocrm.v2.entity.pipeline import Pipeline, Status
from pathlib import Path
import time, os, asyncio

from requests.adapters import HTTPAdapter
from amocrm.v2.interaction import _session
_session.mount("https://", HTTPAdapter(max_retries=5))

#Время, от которого будем высчитывать, обновлять deal_list или нет (раз в  5 мин = 300 сек)
bot = Bot(TOKEN)
dp = Dispatcher(bot)


#Получить словарь из всех сделок
def get_deal_list():
    for i in range(3):
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
                #добавляем запись   -    Название сделки: сделка
                deal_list[deal.name] = deal

            break

        except Exception as e: 
            deal_list = "Произошла ошибка на сервере🫤" + str(e)
            continue
        


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
    #Интервал обновления БД
    update_deal_list_interval = 900

    if len(marker) >= 5:
        second_time = time.time()

        #Если прошло 600 сек с последнего обновления базы
        if (second_time - first_time >= update_deal_list_interval):  
            first_time = second_time

            # Создаем асинхронный поток и запускаем в нем    GET_DEAL_LIST
            loop = asyncio.get_running_loop()
            deal_list = await loop.run_in_executor(None, get_deal_list)
        

        #Находим нужную запись, если не произошло ошибок
        if str(type(deal_list)) != "<class 'str'>":
            deal_status = f"⚠️Неправильно введен маркер товара!\n\nВозможно, вашу запись еще не внесли в базу. \nПопробуйте через {int(update_deal_list_interval - (second_time - first_time))} сек"

            #Ищем сделку в названии которой есть marker
            for key, value in deal_list.items():
                if key.find(marker) != -1:
                    deal_status = "🌍" + (value.status.name).upper()
                    break
        else:
            deal_status = deal_list
    else:
        deal_status = "⚠️Маркер должен быть больше, чем 4 символа!"

    await msg.answer(deal_status)





# Callback кнопки "Местонахождение товара"
@dp.callback_query_handler(text="product_location") #text - То, что отправили с кнопкой
async def product_location(call):
    await tracker_process(call.message)
    await call.answer()  # Обязательно



if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
