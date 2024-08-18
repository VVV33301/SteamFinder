import discord
from discord import app_commands
from pandas import read_csv
import pickle

from settings import DS_TOKEN

intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

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


@client.event
async def on_ready():
    print('Initialized')
    await tree.sync()


@tree.command(name='help', description='Информация')
async def print_help(interaction):
    await interaction.response.send_message('Введите название игры, а SteamFinder подберет наиболее '
                                            'подходящие по жанрам, категориям и тегам')


@tree.command(name='get', description='Получить похожие игры')
@app_commands.describe(name='Название игры')
async def print_info(interaction, name: str):
    text = name.strip().replace(' ', '').lower()
    if len(text) < 3:
        await interaction.response.send_message('Пожалуйста, введите более 3 букв')
    else:
        rec = recommend_games_by_name(find_closest_matches(text), df)
        if rec is None:
            await interaction.response.send_message('SteamFinder не смог найти игры, похожие на ' + name)
        else:
            await interaction.response.send_message('Список наиболее подходящих игр\n' + '\n'.join(rec[:10]))


@tree.command(name='info', description='Информация об игре')
@app_commands.describe(name='Название игры')
async def print_info(interaction, name: str):
    info = df[df['Name'] == name].iloc[0].to_dict()
    await interaction.response.send_message(f"Название: {info['Name']}\n"
                                            f"Цена: {info['Price']}$\n"
                                            f"Возрастной рейтинг: {info['Required age']}+\n"
                                            f"Оценка на Metacritic: {info['Metacritic score']}\n\n"
                                            f"https://store.steampowered.com/app/{info['AppID']}")


if __name__ == "__main__":
    client.run(DS_TOKEN)
