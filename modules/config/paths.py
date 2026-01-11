import os


def get_project_path(project_dir_name):
    path = os.getcwd().split(project_dir_name)[0]
    path = os.path.join(path, project_dir_name)
    return path


project_name = "FMS-bot"
project_path = get_project_path(project_name)
data_path = os.path.join(project_path, "data")
os.makedirs(data_path, exist_ok=True)
database_path = os.path.join(data_path, "database.db")
config_path = os.path.join(data_path, "config.json")

modules_path = os.path.join(project_path, "modules")
scripts_path = os.path.join(project_path, "scripts")

statistics_path = os.path.join(modules_path, "statistics")
data_statistics_path = os.path.join(statistics_path, "data_statistics.json")

downloaded_files_path = os.path.join(data_path, "downloaded_files")
os.makedirs(downloaded_files_path, exist_ok=True)
parsed_files_path = os.path.join(data_path, "parsed_files")
os.makedirs(parsed_files_path, exist_ok=True)

data_updater_path = os.path.join(modules_path, "data_updater")
painter_path = os.path.join(data_updater_path, "painter")
fonts_path = os.path.join(painter_path, "fonts")

images_updater_path = os.path.join(modules_path, "images_updater")
render_path = os.path.join(images_updater_path, "render")
templates_path = os.path.join(render_path, "templates")

telegram_path = os.path.join(modules_path, "telegram_int")
telegram_data_path = os.path.join(modules_path, "data.json")
telegram_messages_path = os.path.join(telegram_path, "messages")
telegram_info_message_path = os.path.join(telegram_messages_path, "info.txt")
