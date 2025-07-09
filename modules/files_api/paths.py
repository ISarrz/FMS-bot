import os


def get_project_path(project_dir_name):
    path = os.getcwd().split(project_dir_name)[0]
    path = os.path.join(path, project_dir_name)
    return path


project_name = "FMS-bot"
project_path = get_project_path(project_name)
data_path = os.path.join(project_path, "data")
database_path = os.path.join(data_path, "database.db")
database_dumps_path = os.path.join(data_path, "database_dumps")
database_dump_path = os.path.join(database_dumps_path, "database_dump.db")
config_path = os.path.join(data_path, "config.json")

modules_path = os.path.join(project_path, "modules")
database_updater_path = os.path.join(modules_path, "database_updater")
scripts_path = os.path.join(project_path, "scripts")

downloads_path = os.path.join(database_updater_path, "downloads")
parsed_files_path = os.path.join(database_updater_path, "parsed_files")


images_updater_path = os.path.join(modules_path, "images_updater")
render_path = os.path.join(images_updater_path, "render")
templates_path = os.path.join(render_path, "templates")
fonts_path = os.path.join(images_updater_path, "fonts")

telegram_path = os.path.join(modules_path, "telegram_int")
telegram_messages_path = os.path.join(telegram_path, "messages")
telegram_info_message_path = os.path.join(telegram_messages_path, "info.txt")