from aiogram import Bot, Dispatcher, F
from aiogram.types import *
from aiogram.filters import Command
import asyncio
from pandas import read_csv
import pickle

from settings import TG_TOKEN

bot = Bot(TG_TOKEN)
dp = Dispatcher()

df = read_csv('dataset/games_knn.csv', index_col=0)
model = pickle.load(open('knn.model', 'rb'))

list2check = df['Name Cleaned'].values.tolist()


def find_closest_matches(test_str):
    scores = {}
    for ii in list2check:
        cnt = 0
        min_len = min(len(test_str), len(ii))
        for jj in range(min_len):
            cnt += 1 if test_str[jj] == ii[jj] else 0
        scores[ii] = cnt
    sorted_score = sorted(scores.items(), key=lambda x: x[1], reverse=True)[0]
    closest_match = sorted_score[0]
    return closest_match


def recommend_games_by_name(game_name, df):
    if game_name not in list2check:
        return None
    info = []
    pred, ind = model.kneighbors([eval(df.loc[df[df['Name Cleaned'] == game_name].index[0]]['Feat'])])
    predict = (pred[0].tolist(), ind[0].tolist())
    for i in sorted(predict, key=lambda x: x[0])[1][1:]:
        info.append(df.loc[i]['Name'])
    return info


@dp.message(Command('start'))
async def start(message: Message):
    await message.answer('SteamFinder поможет Вам подобрать игры. Просто введите игру, а бот подскажет, какие игры нужны таким как Вы')


@dp.message(Command('help'))
async def print_help(message: Message):
    await message.answer('Введите название игры, а SteamFinder подберет наиболее подходящие по жанрам, категориям и тегам')


@dp.message(F.text)
async def predict_games(message: Message):
    text = message.text.strip().replace(' ', '').lower()
    if len(text) < 3:
        await message.answer('Пожалуйста, введите более 3 букв')
    else:
        rec = recommend_games_by_name(find_closest_matches(text), df)
        if rec is None:
            await message.answer('SteamFinder не смог найти игры, похожие на ' + message.text)
        else:
            variants = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text=i, callback_data=i)] for i in rec[:10]])
            await message.answer('Список наиболее подходящих игр', reply_markup=variants)


@dp.callback_query(F.data)
async def print_info(call: CallbackQuery):
    info = df[df['Name'] == call.data].iloc[0].to_dict()
    await call.message.answer(f"Название: {info['Name']}\n"
                              f"Цена: {info['Price']}$\n"
                              f"Возрастной рейтинг: {info['Required age']}+\n"
                              f"Оценка на Metacritic: {info['Metacritic score']}\n\n"
                              f"https://store.steampowered.com/app/{info['AppID']}")
    await call.answer()


async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    print('Initialized')
    asyncio.run(main())
