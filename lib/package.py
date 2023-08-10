import glob
import json
import os
import shutil

import pandas as pd

# import pandas as pd


def open_contrast_url():
    """開啟對照表

    Args:
        None

    Returns:
        dict: 對照表
    """
    with open('data/url_contrast.json', 'r') as f:
        mode_to_url = json.load(f)
    return mode_to_url


# 讀取json
def read_data(folder_path):
    with open(folder_path, "r", encoding='utf-8-sig') as file:
        data = json.load(file)
    return data


def check_data(folder_path):
    if os.path.exists(folder_path):
        return True
    else:
        return False


# 儲存json
def save_json(folder_path, data_json, code_name):
    # 將列表儲存成 JSON 字串
    json_str = json.dumps(data_json)

    # 將json寫道文件中
    with open(
        f"{folder_path}/{code_name}.json", "w", encoding='utf-8-sig'
    ) as file:
        file.write(json_str)


def save_data(department_num, folder_path):
    os.makedirs(folder_path, exist_ok=True)

    for i in range(department_num):
        source_file = f"./data/.cache/{i}.json"
        destination_file = os.path.join(folder_path, f"{i}.json")
        shutil.move(source_file, destination_file)


def check_data(folder_path):
    if os.path.exists(folder_path):
        return True
    else:
        return False


def read_data_num(folder_path):
    json_files = glob.glob(os.path.join(folder_path, "*.json"))
    num_json_files = len(json_files)

    return num_json_files


def record_error(content):
    with open(f"./data/error.txt", "a", encoding='utf-8-sig') as file:
        file.write(content + '\n')


def trans_to_csv(folder_path, file_name, year, mode, choose):
    if check_data(f'{folder_path}/{file_name}.json'):
        data_list = read_data(f'{folder_path}/{file_name}.json')
    else:
        record_error(f'{folder_path}/{file_name}.json')

    match mode:
        case 'U' | 'HS_to_UST':
            student_id_list = [
                data_list[n][0] for n, k in enumerate(data_list)
            ]
            last_school = [data_list[n][2] for n, k in enumerate(data_list)]
            last_choice = [data_list[n][3] for n, k in enumerate(data_list)]
            volunteer = [data_list[n][4] for n, k in enumerate(data_list)]
            admission_status = [
                data_list[n][5] for n, k in enumerate(data_list)
            ]
            volunteer_school = [
                data_list[n][6] for n, k in enumerate(data_list)
            ]
            volunteer_department = [
                data_list[n][7] for n, k in enumerate(data_list)
            ]
        case 'UST':
            student_id_list = [
                data_list[n][0] for n, k in enumerate(data_list)
            ]
            last_school = [data_list[n][1] for n, k in enumerate(data_list)]
            last_choice = [data_list[n][2] for n, k in enumerate(data_list)]
            volunteer = [data_list[n][3] for n, k in enumerate(data_list)]
            admission_status = [
                data_list[n][4] for n, k in enumerate(data_list)
            ]
            volunteer_school = [
                data_list[n][5] for n, k in enumerate(data_list)
            ]
            volunteer_department = [
                data_list[n][6] for n, k in enumerate(data_list)
            ]

    data_all_df = {
        '學年度': year,
        '准考證號碼': student_id_list,
        '最終選擇的志願': last_school,
        '最終志願': last_choice,
        '選擇哪些志願': volunteer,
        '錄取狀況': admission_status,
        '志願序的大學': volunteer_school,
        '志願序的科系': volunteer_department,
    }
    data_all_df = pd.DataFrame(data_all_df)
    return data_all_df


def dict_write_json(dict, file_name):
    """將 dictionary 轉換成 json

    Args:
        dict (dict)
        file_name (str):
    """
    json_str = json.dumps(dict)
    # 將 JSON 字串寫入檔案中
    with open(file_name, "w") as f:
        f.write(json_str)
