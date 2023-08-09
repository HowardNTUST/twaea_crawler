import random
import re

import pandas as pd
from joblib import Parallel, delayed

from lib.IR_request import (
    get_candidate_info,
    getdepartment_UST,
    getschool_links,
    getschool_links_UST,
    request_url,
)
from lib.package import dict_write_json, trans_to_csv_UST


# =============================111統測甄選===============================
def department_crawler(year):
    url = f'https://www.com.tw/vtech/university_list{year}.html'
    getschool_soup = request_url(url)
    url_domain = re.findall('.*\\/', url)[0]
    school_links = getschool_links_UST(getschool_soup, url_domain)
    schoolid_to_department_links = []
    # url = 'https://www.com.tw/vtech/university_102_111.html'
    schoolid_to_department_links = Parallel(n_jobs=10)(
        delayed(getdepartment_UST)(url, url_domain) for url in school_links
    )
    return schoolid_to_department_links


# def combine_all_department_links(schoolid_to_department_links,mode,year):
#     all_department_links_df = pd.json_normalize(data=schoolid_to_department_links)
#     return all_department_links_df


def content_crawler(schoolid_to_department_links):
    department_list = []
    for n, school in enumerate(schoolid_to_department_links):
        for value in schoolid_to_department_links[n].values():
            department_list.append(value)

    # 正式
    all_volunteer_data = department_list

    # # 測試
    # all_volunteer_data = random.sample(department_list,10)

    # n=1
    # department_href = department_list[n]
    # url = department_href
    department_data = Parallel(n_jobs=10)(
        delayed(get_candidate_info_UST)(department, n)
        for n, department in enumerate(all_volunteer_data)
    )
    # students = get_candidate_info(department_href,n)

    return len(all_volunteer_data)


def combine_data(department_num, year, mode):
    department_num_list = [i for i in range(department_num)]
    dfs_to_concat = []
    dfs_to_concat = Parallel(n_jobs=10)(
        delayed(trans_to_csv_UST)(file_name, year)
        for n, file_name in enumerate(department_num_list)
    )

    # dfs_to_concat = [trans_to_csv_UST(file_name, year) for n, file_name in enumerate(department_num_list)]

    df_all_data = pd.DataFrame()
    df_all_data = (
        pd.concat(dfs_to_concat, ignore_index=True)
        .drop_duplicates()
        .apply(lambda x: x.str.replace('\r', '') if x.dtype == 'object' else x)
    )
    df_all_data.to_csv(
        f'data/{year}_IR3_{mode}.csv', encoding='utf-8-sig', index=False
    )

    # df_all_data =df_all_data.append(Parallel(n_jobs=10)(
    #                 delayed(trans_to_csv)(file_name,year) for n,file_name in enumerate(department_num_list)
    #             ))
    # df_all_data.to_csv(f'{year}_IR3_UST_new.csv',index='UTF-8-sig')


def main_crawler(mode, year):
    schoolid_to_department_links = department_crawler(year)
    # all_department_links_df = combine_all_department_links(schoolid_to_department_links,mode,year)
    department_num = content_crawler(schoolid_to_department_links)
    combine_data(department_num, year, mode)
