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

modules_path = os.path.join(project_path, "modules")
scripts_path = os.path.join(project_path, "scripts")
