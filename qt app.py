from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *
from pandas import read_csv
import pickle
from webbrowser import open as openweb
import sys

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
    for i in sorted(predict, key=lambda x: x[0])[1]:
        info.append(df.loc[i]['Name'])
    return info


class GameInfo(QDialog):
    def __init__(self, info, *args):
        super().__init__(*args)
        self.setWindowTitle(info['Name'])

        self.layout = QVBoxLayout(self)
        self.setLayout(self.layout)

        self.info_label = QLabel(self)
        self.layout.addWidget(self.info_label)
        self.info_label.setText(f"Цена: {info['Price']}$\n"
                                f"Возрастной рейтинг: {info['Required age']}+\n"
                                f"Оценка на Metacritic: {info['Metacritic score']}\n\n"
                                f"https://store.steampowered.com/app/{info['AppID']}")

        self.open_btn = QPushButton('Открыть страницу игры', self)
        self.open_btn.clicked.connect(lambda: openweb(f"https://store.steampowered.com/app/{info['AppID']}"))
        self.layout.addWidget(self.open_btn)


class SteamFinderWindow(QWidget):
    def __init__(self, *args):
        super().__init__(*args)
        self.setWindowTitle('SteamFinder')

        self.layout = QVBoxLayout(self)
        self.setLayout(self.layout)

        self.input_game = QLineEdit(self)
        self.input_game.setPlaceholderText('Название игры')
        self.input_game.textChanged.connect(self.print_games)
        self.layout.addWidget(self.input_game)

        self.info_label = QLabel(self)
        self.layout.addWidget(self.info_label)

        self.game_list = QListWidget(self)
        self.game_list.itemClicked.connect(self.game_info)
        self.layout.addWidget(self.game_list)

    def print_games(self):
        text = self.input_game.text().strip().replace(' ', '').lower()
        self.game_list.clear()
        if len(text) < 3:
            self.info_label.setText('Пожалуйста, введите более 3 букв')
        else:
            rec = recommend_games_by_name(find_closest_matches(text), df)
            if rec is None:
                self.info_label.setText('Ничего не найдено')
            else:
                self.info_label.setText('Результаты поиска по игре ' + rec[0])
                for i in rec[1:11]:
                    self.game_list.addItem(QListWidgetItem(i, self.game_list))

    def game_info(self, name):
        info = df[df['Name'] == name.text()].iloc[0].to_dict()
        wind = GameInfo(info, self)
        wind.exec()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon('SteamFinderLogo.jpg'))
    sf = SteamFinderWindow()
    sf.show()
    sys.exit(app.exec())