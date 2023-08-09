import json
import os

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
def read_json(code_name):
    with open(f"data/.cache/{code_name}.json", "r",encoding='utf-8-sig') as file:
        data = json.load(file)
    return data

def check_json(code_name):
    if os.path.isfile(f"data/.cache/{code_name}.json"):
        data = read_json(code_name)
    else:
        data = []
    return data
# 儲存json 
def save_json(data_json, code_name):

    # 將列表儲存成 JSON 字串
    json_str = json.dumps(data_json)

    # 將json寫道文件中
    with open(f"data/.cache/{code_name}.json", "w",encoding='utf-8-sig') as file:
        file.write(json_str)



        
def record_error(content):
    with open(f"./data/error.txt", "a",encoding='utf-8-sig') as file:
        file.write(content+'\n')
        
def trans_to_csv(file_name,year):
    data_list =check_json(file_name)
    
    student_id_list = [data_list[n][0] for n,k in enumerate(data_list)]
    last_school = [data_list[n][2] for n,k in enumerate(data_list)]
    last_choice = [data_list[n][3]for n,k in enumerate(data_list)]
    volunteer = [data_list[n][4] for n,k in enumerate(data_list)]
    admission_status = [data_list[n][5] for n,k in enumerate(data_list)]
    volunteer_school = [data_list[n][6] for n,k in enumerate(data_list)]
    volunteer_department = [data_list[n][7] for n,k in enumerate(data_list)]
    
    data_all_df = {
    '學年度':year,
    '准考證號碼':student_id_list,
    '最終選擇的志願':last_school,
    '最終志願':last_choice,
    '選擇哪些志願':volunteer,
    '錄取狀況' :admission_status,
    '志願序的大學':volunteer_school,
    '志願序的科系':volunteer_department
    }
    data_all_df = pd.DataFrame(data_all_df)
    return data_all_df

def trans_to_csv_UST(file_name,year):
    data_list =check_json(file_name)
    
    student_id_list = [data_list[n][0] for n,k in enumerate(data_list)]
    last_school = [data_list[n][1] for n,k in enumerate(data_list)]
    last_choice = [data_list[n][2]for n,k in enumerate(data_list)]
    volunteer = [data_list[n][3] for n,k in enumerate(data_list)]
    admission_status = [data_list[n][4] for n,k in enumerate(data_list)]
    volunteer_school = [data_list[n][5] for n,k in enumerate(data_list)]
    volunteer_department = [data_list[n][6] for n,k in enumerate(data_list)]
    
    data_all_df = {
    '學年度':year,
    '准考證號碼':student_id_list,
    '最終選擇的志願':last_school,
    '最終志願':last_choice,
    '選擇哪些志願':volunteer,
    '錄取狀況' :admission_status,
    '志願序的大學':volunteer_school,
    '志願序的科系':volunteer_department
    }
    data_all_df = pd.DataFrame(data_all_df)
    return data_all_df





def dict_write_json(dict,file_name):
    """將 dictionary 轉換成 json

    Args:
        dict (dict)
        file_name (str):
    """
    json_str = json.dumps(dict)
    # 將 JSON 字串寫入檔案中
    with open(file_name, "w") as f:
        f.write(json_str)
