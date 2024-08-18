from flask import Flask, request
from pandas import read_csv
import pickle

app = Flask(__name__)

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


@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        input_data = request.form['input_data']
        rec = recommend_games_by_name(find_closest_matches(input_data), df)
        links = []
        for name in rec[1:]:
            links.append(f'<a href="/app/{name}">{name}</a>')
        return f'''
        <html>
        <head>
            <title>SteamFinder</title>
        </head>
        <body>
            <h2>Введите данные для предсказания:</h2>
            <form method="post">
                <input type="text" name="input_data" placeholder="Введите данные через запятую" required>
                <button type="submit">Предсказать</button>
            </form>
            <h3>Результаты предсказаний</h3>
            {'<br>'.join(links)}
        </body>
        </html>
        '''
    return f'''
            <html>
            <head>
                <title>SteamFinder</title>
            </head>
            <body>
                <h2>Введите данные для предсказания:</h2>
                <form method="post">
                    <input type="text" name="input_data" placeholder="Введите данные через запятую" required>
                    <button type="submit">Предсказать</button>
                </form>
            </body>
            </html>
            '''


@app.route('/app/<string:name>')
def print_info(name):
    info = df[df['Name'] == name].iloc[0].to_dict()
    return f'''
            <html>
            <head>
                <title>{name} - SteamFinder</title>
            </head>
            <body>
                <h2>{name}</h2>
                <p>Название: {info['Name']}</p>
                <p>Цена: {info['Price']}$</p>
                <p>Возрастной рейтинг: {info['Required age']}+</p>
                <p>Оценка на Metacritic: {info['Metacritic score']}</p>
                <a href="https://store.steampowered.com/app/{info['AppID']}"></a>
            </body>
            </html>
            '''


if __name__ == "__main__":
    app.run()
