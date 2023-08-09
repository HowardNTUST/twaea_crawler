import itertools
import re

import pandas as pd
from joblib import Parallel, delayed

from lib.IR_request import (
    add_year_col,
    get_candidate_info,
    getdepartment,
    getschool_links,
    request_url,
)
from lib.package import open_contrast_url, trans_to_csv

"""
U: 大學查榜->大學個人申請
HS_to_UST: 大學查榜->科大四技申請
UST: 統測分發->依校系查榜
TODO:
產出前把空格去掉
"""


def department_crawler(mode, year):
    # 網站網址
    mode_to_url = open_contrast_url()

    # according to mode to set url & domain
    url = mode_to_url[mode]['查詢學校網頁'].replace('QUERY_YEAR', year)
    url_domain = re.findall('.*\\/', url)[0]

    # 抓取所有學校連結
    getschool_soup = request_url(url)
    school_links = getschool_links(getschool_soup, url_domain)

    # 抓取所有校系連結
    schoolid_to_department_links = Parallel(n_jobs=10)(
        delayed(getdepartment)(url, url_domain) for url in school_links
    )

    # 處理音樂系額外連結
    music_dep_links = (
        pd.json_normalize(schoolid_to_department_links, '學系資料', ['學校代號'])  # type: ignore
        .query("link.str.contains('music_dep')")
        .loc[:, ['學校代號', 'link']]
        .to_numpy()
    )

    volunteer_data = Parallel(n_jobs=10)(
        delayed(getdepartment)(url, url_domain) for schoolid, url in music_dep_links  # type: ignore
    )
    return schoolid_to_department_links, volunteer_data


def organize_department_data(
    mode, year, schoolid_to_department_links, volunteer_data
):
    # 合併資料
    all_department_links_df = (
        pd.concat(
            [
                pd.json_normalize(
                    schoolid_to_department_links, '學系資料', ['學校代號']
                ).query(
                    "~link.str.contains('music_dep')"
                ),  # type: ignore
                pd.json_normalize(volunteer_data, '學系資料', ['學校代號']),  # type: ignore
            ]
        )
        .loc[:, ['學校代號', '科系', 'link']]
        .sort_values('學校代號')
        .reset_index()
        .drop('index', axis=1)
    )
    all_department_links_df.to_csv(
        f'data/{mode}_{year}_check_file_test.csv', encoding='utf-8-sig'
    )
    return all_department_links_df


def content_crawler(all_department_links_df, choose):
    match choose:
        case '正式':
            # 正式
            all_volunteer_data = Parallel(
                n_jobs=30
            )(  # url = all_department_links_df['link'].values[0]
                delayed(get_candidate_info)(url, n)
                for n, url in enumerate(all_department_links_df['link'].values)
            )
        case '測試':
            # 測試
            part_department_links_df = all_department_links_df.sample(
                n=10, replace=False
            )
            all_volunteer_data = Parallel(n_jobs=10)(
                delayed(get_candidate_info)(url, n)
                for n, url in enumerate(
                    part_department_links_df['link'].values
                )
            )
    return all_volunteer_data


def combine_data(mode, year, all_volunteer_data):
    department_num_list = [i for i in range(len(all_volunteer_data))]
    dfs_to_concat = []
    dfs_to_concat = Parallel(n_jobs=10)(
        delayed(trans_to_csv)(file_name, year)
        for n, file_name in enumerate(department_num_list)
    )
    # 刪除'\r'讓csv檔案可以正常顯示
    df_all_data = (
        pd.concat(dfs_to_concat, ignore_index=True)
        .drop_duplicates()
        .apply(lambda x: x.str.replace('\r', '') if x.dtype == 'object' else x)
    )

    df_all_data.to_csv(
        f'data/{year}_IR3_{mode}_test.csv', encoding='utf-8-sig', index=False
    )


def main_crawler(mode, year, choose):
    """正式用的爬蟲

    Args:
        mode (_type_): _description_
        year (_type_): _description_
        choose(str) : '正式' or '測試'

    Returns:
        _type_: _description_
    """
    schoolid_to_department_links, volunteer_data = department_crawler(
        mode, year
    )
    all_department_links_df = organize_department_data(
        mode, year, schoolid_to_department_links, volunteer_data
    )
    all_volunteer_data = content_crawler(all_department_links_df, choose)
    combine_data(mode, year, all_volunteer_data)
