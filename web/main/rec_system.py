import logging
import warnings
import time
from datetime import datetime

warnings.filterwarnings("ignore")
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

import numpy as np
import pandas as pd
import catboost as cb
import os

from sklearn.preprocessing import LabelEncoder, OneHotEncoder
from .tools.word2vec_predict import Analyzer


class Utils:
    edu_levels = {
        'ООО': ['Биология', 'Французский язык', 'Информатика', 'Основы безопасности жизнедеятельности',
                'Английский язык', 'Русский язык', 'История', 'Изобразительное искусство', 'Литература',
                'Геометрия', 'Алгебра', 'Химия', 'География', 'Технология', 'Всеобщая история',
                'История России', 'Музыка', 'Испанский язык', 'Немецкий язык', 'Мир историй',
                'Китайский язык',
                'История Отечества', 'Физика', 'Природоведение', 'Чтение (Литературное чтение)',
                'Основы социальной жизни'],
        'НОО': ['Русский язык', 'Основы православной культуры', 'Математика', 'Основы буддийской культуры',
                'Основы иудейской культуры', 'Основы мировых религиозных культур',
                'Основы исламской культуры',
                'Основы светской этики', 'Французский язык', 'Английский язык', 'Окружающий мир',
                'Литературное чтение', 'Музыка', 'Испанский язык', 'Немецкий язык', 'Физическая культура',
                'Технология', 'Окружающий мир (Человек, природа, общество)', 'Обучение грамоте',
                'Ознакомление с окружающим миром', 'Мир природы и человека', 'Чтение',
                'Чтение (Литературное чтение)'],
        'СОО': ['Всеобщая история', 'Английский язык', 'Обществознание', 'География', 'Физика', 'Экология',
                'Французский язык', 'История России', 'Испанский язык', 'Русский язык', 'Геометрия',
                'Алгебра',
                'Немецкий язык', 'Право', 'Экономика', 'Естествознание', 'Физическая культура', 'Химия',
                'Литература', 'Информатика', 'История', 'Алгебра и начала математического анализа',
                'Математика', 'Администрирование сетей', 'Литературное чтение']
    }

    def __init__(self):
        self.le = LabelEncoder()
        self.model = cb.CatBoostClassifier()
        self.text_analyzer = Analyzer()

        self.materials = pd.read_csv(os.path.join('main', 'data', 'materials.csv'), dtype={'material_id': int})
        users_info = pd.read_csv(os.path.join('main', 'data', 'users.csv'), dtype={'teacher_id': int})
        self.text_analyzer.load_model(os.path.join('main', 'tools', 'word2vec.model'))
        self.model.load_model(os.path.join('main', 'tools', 'model.cbm'), format='cbm')

        # TEST
        # self.materials = pd.read_csv('../input/materials.csv', dtype={'material_id': int}).drop(['Unnamed: 0'], axis=1)
        # users_info = pd.read_csv('../input/users.csv', dtype={'teacher_id': int})
        # self.model.load_model('../input/model.cbm', format='cbm')
        # self.text_analyzer.load_model('../input/word2vec.model')

        #       FIXME Часть пользователей могла бесследно исчезнуть
        #         users_info = users_info[users_info['name'].isin(self.materials['name'].unique().tolist())]
        self.materials = self.materials.rename(index=str, columns={column: column + '_watching' for column in
                                                                   self.materials.columns})
        self.users = {}
        for user in users_info['teacher_id'].unique():
            self.users[user] = users_info[users_info['teacher_id'] == user].sort_values(by='sort_time')

        self.education_dict = {'ООО': 'education_level_watching_0', 'СОО': 'education_level_watching_1',
                               'НОО': 'education_level_watching_2'}
        self.colors = [
            "#FEA47F", "#25CCF7", "#EAB543", "#55E6C1", "#CAD3C8", "#F97F51", "#1B9CFC", "#F8EFBA", "#58B19F",
            "#2C3A47",
            "#B33771", "#3B3B98", "#FD7272", "#9AECDB", "#D6A2E8", "#6D214F", "#182C61", "#FC427B", "#BDC581",
            "#82589F",
            "#ef5777", "#575fcf", "#4bcffa", "#34e7e4", "#0be881", "#f53b57", "#3c40c6", "#0fbcf9", "#00d8d6",
            "#05c46b",
            "#ffc048", "#ffdd59", "#ff5e57", "#d2dae2", "#485460", "#ffa801", "#ffd32a", "#ff3f34", "#808e9b",
            "#1e272e",
            "#fc5c65", "#fd9644", "#fed330", "#26de81", "#2bcbba", "#eb3b5a", "#fa8231", "#f7b731", "#20bf6b",
            "#0fb9b1",
            "#45aaf2", "#4b7bec", "#a55eea", "#d1d8e0", "#778ca3", "#2d98da", "#3867d6", "#8854d0", "#a5b1c2", "#4b6584"
        ]

        logger.info('Initialization completed')

    # def get_materials(self, education, subject):
    #     """
    #     :type education: str
    #     :type subject: str
    #     :param education: level of education
    #     :param subject: school subject from list
    #     :return: dict of materials for subject with structure {material name: uploading_data}
    #     """
    #     assert education in self.education, f"Education level must be in list: {', '.join(self.education)}."
    #     assert subject in self.subjects, f"Subject must be in list: {', '.join(self.subjects)}."
    #     return pd.read_csv(f"{education}/{subject}.csv", sep=";").columns.tolist()

    def _preprocessor(self, data):
        label_columns = [
            "year",
            "subject",
            "creation_year",
            "material_type",
            "year_watching",
            "education_level",
            "subject_watching",
            "material_type_watching",
            "education_level_watching",
            "creation_year_watching"
        ]

        onehot_columns = [
            "year",
            "material_type",
            "creation_year",
            "year_watching",
            "education_level",
            "material_type_watching",
            "creation_year_watching",
            "education_level_watching",
        ]

        for column in label_columns:
            data[column] = self.le.fit_transform(data[column])

        for column in onehot_columns:
            one_hot = pd.get_dummies(data[column], prefix=column)
            data = pd.concat([data, one_hot], axis=1)

        columns = ['action_info', 'average_rating', 'average_rating_watching', 'cos_sec', 'cos_sec_watching',
                   'creation_day', 'creation_day_watching', 'creation_month', 'creation_month_watching',
                   'creation_year_0', 'creation_year_1', 'creation_year_2', 'creation_year_3',
                   'creation_year_watching_0', 'creation_year_watching_1', 'creation_year_watching_2',
                   'creation_year_watching_3', 'day', 'day_watching', 'distance', 'education_level_0',
                   'education_level_1', 'education_level_2', 'education_level_watching_0', 'education_level_watching_1',
                   'education_level_watching_2', 'material_id', 'material_id_watching', 'material_type_0',
                   'material_type_1', 'material_type_2', 'material_type_3', 'material_type_4', 'material_type_5',
                   'material_type_watching_0', 'material_type_watching_1', 'material_type_watching_2',
                   'material_type_watching_3', 'material_type_watching_4', 'material_type_watching_5', 'month',
                   'month_watching', 'school_id', 'school_id_watching', 'sin_sec', 'sin_sec_watching', 'subject',
                   'subject_watching', 'teacher_id', 'week_days', 'week_days_watching', 'year_0', 'year_1', 'year_2',
                   'year_3', 'year_watching_0', 'year_watching_1', 'year_watching_2', 'year_watching_3']
        unique_columns = set(columns) - set(data.columns.tolist())
        for unique in unique_columns:
            data[unique] = 0

        data = data.drop(onehot_columns, axis=1)
        data = data[sorted(data.columns.tolist())]
        return data

    def make_recommendations(self, user_id, education, subject):
        """
        :type user_id: int
        :type education: str
        :type subject: str
        :type n: int

        :param user_id: id of user in DataFrames
        :param education: education level of materials
        :param subject: school subject of materials
        :param n: number of materials for recommendations

        :return: dict of recommendations with probability for n materials
        """

        # # FIXME Тяжелый модуль для фильтрации просмотренных материлов по возможности что-нибудь сделать
        # mini_materials = self.materials[(self.materials["subject_watching"] == subject) & (self.materials["education_level_watching"] == education)]
        # unique_materials = zip(mini_materials["material_id_watching"], mini_materials["material_type_watching"])
        # materials_users = zip(self.users["user"]["material_id_watching"], self.users["user"]["material_type_watching"])
        # unique_materials = list(set(unique_materials) ^ set(materials_users))
        # materials_id = []
        # materials_type = []
        # for _id, _type in unique_materials:
        #     materials_id.append(_id)
        #     materials_type.append(_type)
        # materials = mini_materials[(mini_materials["material_id_watching"].isin(materials_id)) & (mini_materials["material_type_watching"].isin(materials_type))]

        materials = self.materials[
            (self.materials["subject_watching"] == subject) & (self.materials["education_level_watching"] == education)]
        last = self.users[user_id].iloc[-1]
        last = last.drop([key for key in last.keys() if "_watching" in key])

        for key in last.keys():
            materials[key] = last[key]

        dt = datetime.now()
        materials["teacher_id"] = user_id
        materials["week_days_watching"] = dt.weekday()
        materials["year_watching"] = dt.year
        materials["month_watching"] = dt.month
        materials["day_watching"] = dt.day

        seconds = dt.hour * 3600 + dt.minute * 60 + dt.second
        materials["cos_sec_watching"] = round(self.make_cyclic(seconds, True, 86400), 4)
        materials["sin_sec_watching"] = round(self.make_cyclic(seconds, False, 86400), 4)
        materials["distance"] = materials.apply(
            lambda row: self.text_analyzer.predict(row['name'], row['name_watching']), axis=1)

        names = materials["name_watching"]
        years = materials["creation_year_watching"]
        materials = materials.drop(['name_watching', 'name'], axis=1)
        materials = self._preprocessor(materials)

        materials["prediction"] = self.model.predict_proba(materials)[:, 1]
        materials["subject"] = self.le.inverse_transform(materials["subject"])
        materials["name"] = names
        materials["creation_year_watching"] = years
        #         materials = materials[(materials["subject_watching"] == subject) & (materials[self.education_dict[education]] == 1)]
        materials = materials.drop_duplicates(
            ['name', 'material_id', 'creation_year_watching', 'creation_month_watching', 'creation_day_watching'])
        materials = materials.sort_values(by="prediction", ascending=False)
        return materials

    def get_recommendations(self, user_id, education, subject, n):
        data = self.make_recommendations(user_id, education, subject)
        result = []
        for i in range(n):
            #             result[data.iloc[i]["name"]] = [
            #                 int(data.iloc[i]["creation_year_watching"]),
            #                 int(data.iloc[i]["creation_month_watching"]),
            #                 int(data.iloc[i]["creation_day_watching"])
            #             ]
            result.append([
                data.iloc[i]["name"],
                int(data.iloc[i]["material_id_watching"]),
                int(data.iloc[i]["creation_year_watching"]),
                int(data.iloc[i]["creation_month_watching"]),
                int(data.iloc[i]["creation_day_watching"])
            ])
        return result

    @staticmethod
    def make_cyclic(value, cos, period):
        value *= 2 * np.pi / period
        if cos:
            return np.cos(value)
        return np.sin(value)


    def draw_marks(self, user_id):
        user = self.users[user_id]
        subjects = user["subject"].unique()
        marks = [5, 4, 3, 2, 1]
        content = {"categories": subjects.tolist(), "series": []}
        for mark in marks:
            content["series"].append({"name": str(mark), "data": []})
            for subject in subjects:
                amount = user[(user["subject"] == subject) & (user["action_info"] == mark)]["action_info"].shape[0]
                content["series"][-1]["data"].append(amount)
        return content

    def draw_subjects(self, user_id):
        subjects = self.users[user_id]['subject'].value_counts()
        content = []
        print(subjects.sum())
        total = subjects.sum()
        for subject in subjects.keys():
            if subjects[subject] == subjects.max():
                content.append({"name": subject.capitalize(),
                                "y": round(subjects[subject] / total * 100, 2),
                                "sliced": True})
            else:
                content.append({"name": subject.capitalize(),
                                "y": round(subjects[subject] / total * 100, 2)})
        return content

    def write_themes(self):
        with open("themes.txt", "w", encoding="utf8") as file:
            for theme in self.materials["name_watching"].unique():
                file.write(theme + "\n")

# u = Utils()
# u.write_themes()
# u.get_recommendations(444531, "ООО", "Биология", 10)