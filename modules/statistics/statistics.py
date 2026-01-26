from modules.database.group.group import Group
from modules.config.paths import data_statistics_path
from modules.database.user.user import User
import json


class Statistic:
    @property
    def users_count(self):
        return self.get_field("users_count")

    @users_count.setter
    def users_count(self, value):
        self.set_field("users_count", value)

    @property
    def eleven_grade_count(self):
        return self.get_field("eleven_grade_count")

    @eleven_grade_count.setter
    def eleven_grade_count(self, value):
        self.set_field("eleven_grade_count", value)

    @property
    def ten_grade_count(self):
        return self.get_field("ten_grade_count")

    @ten_grade_count.setter
    def ten_grade_count(self, value):
        self.set_field("ten_grade_count", value)

    @property
    def timetable_count(self):
        return self.get_field("timetable_count")

    @timetable_count.setter
    def timetable_count(self, value: int):
        self.set_field("timetable_count", value)

    @property
    def errors_count(self) -> int:
        return self.get_field("errors_count")

    @errors_count.setter
    def errors_count(self, value: int):
        self.set_field("errors_count", value)

    @staticmethod
    def get_field(field_name: str):
        with open(data_statistics_path) as f:
            response = json.load(f)

        return response[field_name]

    @staticmethod
    def set_field(field_name: str, value):
        data = dict()
        with open(data_statistics_path) as f:
            data = json.load(f)

        data[field_name] = value
        with open(data_statistics_path, "w") as f:
            json.dump(data, f, indent=4)

    def update(self):
        self.users_count = 0
        self.users_with_groups_count = 0
        self.eleven_grade_count = 0
        self.ten_grade_count = 0

        for group in Group(name="10 класс").children + Group(name="11 класс").children:
            if "группа" in group.name:
                continue

            name = group.name

            self.set_field(name, 0)

        for user in User.all():
            self.users_count += 1

            user_groups = user.groups
            if user_groups:
                self.users_with_groups_count += 1

            for group in user_groups:
                if self.contains(group.name) and "группа" not in group.name:
                    count = self.get_field(group.name)
                    self.set_field(group.name, count + 1)

                    if group.parent :
                        if group.parent.name == "10 класс":
                            self.ten_grade_count += 1

                        elif group.parent.name == "11 класс":
                            self.eleven_grade_count += 1

    def reset(self):
        self.timetable_count = 0
        self.errors_count = 0

        self.update()






    @staticmethod
    def contains(value: str):
        data = dict()
        with open(data_statistics_path) as f:
            data = json.load(f)

        if data.__contains__(value):
            return True

        return False

    @staticmethod
    def align(text: str):
        size = 10
        return text.ljust(size, " ")

    def __str__(self):
        text = ""
        text += f"Всего пользователей: {self.users_count}\n"
        text += f"Пользователей с группами: {self.users_with_groups_count}\n"
        text += f"11 класс: {self.eleven_grade_count}\n"
        text += f"10 класс: {self.ten_grade_count}\n"

        groups = Group(name="10 класс").children + Group(name="11 класс").children
        groups = [group for group in groups if "группа" not in group.name]
        for i in range(0, len(groups), 2):
            left = groups[i]
            right = groups[i + 1]
            text += f"`{left.name:<2}: {self.get_field(left.name):<3} {right.name:<2}: {self.get_field(right.name):<3}`\n"

        text += f"Команда timetable: {self.timetable_count}\n"
        text += f"Ошибки: {self.errors_count}\n"

        return text


statistic = Statistic()

if __name__ == "__main__":
    print(statistic)
