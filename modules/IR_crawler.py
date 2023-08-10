import re

import pandas as pd
from joblib import Parallel, delayed

from lib.IR_request import (
    add_year_col,
    get_candidate_info,
    get_candidate_info_UST,
    getdepartment,
    getdepartment_UST,
    getschool_links,
    getschool_links_UST,
    request_url,
)
from lib.package import (
    check_data,
    open_contrast_url,
    read_data_num,
    save_data,
    trans_to_csv,
)

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

    schoolid_music_to_department_links = Parallel(n_jobs=10)(
        delayed(getdepartment)(url, url_domain) for schoolid, url in music_dep_links  # type: ignore
    )
    return schoolid_to_department_links, schoolid_music_to_department_links


def department_crawler_UST(mode, year):
    # 網站網址
    mode_to_url = open_contrast_url()

    # according to mode to set url & domain
    url = mode_to_url[mode]['查詢學校網頁'].replace('QUERY_YEAR', year)
    url_domain = re.findall('.*\\/', url)[0]

    # 抓取所有學校連結
    getschool_soup = request_url(url)
    school_links = getschool_links_UST(getschool_soup, url_domain)

    # 抓取所有校系連結
    schoolid_to_department_links = Parallel(n_jobs=10)(
        delayed(getdepartment_UST)(url, url_domain) for url in school_links
    )

    return schoolid_to_department_links


def organize_department_data(
    mode,
    year,
    schoolid_to_department_links,
    schoolid_music_to_department_links,
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
                pd.json_normalize(schoolid_music_to_department_links, '學系資料', ['學校代號']),  # type: ignore
            ]
        )
        .loc[:, ['學校代號', '科系', 'link']]
        .sort_values('學校代號')
        .reset_index()
        .drop('index', axis=1)
    )
    all_department_links_df.to_csv(
        f'data/{year}_IR3_{mode}_check_file_test.csv', encoding='utf-8-sig'
    )
    return all_department_links_df


def organize_department_data_UST(mode, year, schoolid_to_department_links):
    # 合併資料
    all_department_links_df = (
        pd.json_normalize(
            schoolid_to_department_links, '學系資料', ['學校代號']
        )  # type: ignore
        .loc[:, ['學校代號', '科系', 'link']]
        .sort_values('學校代號')
        .reset_index()
        .drop('index', axis=1)
    )
    all_department_links_df.to_csv(
        f'data/{year}_IR3_{mode}_check_file_test.csv', encoding='utf-8-sig'
    )
    return all_department_links_df


def content_crawler(mode, all_department_links_df, choose):
    match choose:
        case '正式':
            # 正式
            all_department_links_df = all_department_links_df
        case '測試':
            # 測試
            all_department_links_df = all_department_links_df.sample(
                n=20, replace=False
            )

    match mode:
        case 'U' | 'HS_to_UST':
            all_volunteer_data = Parallel(n_jobs=30)(
                delayed(get_candidate_info)(url, n)
                for n, url in enumerate(all_department_links_df['link'].values)
            )
        case 'UST':
            all_volunteer_data = Parallel(n_jobs=30)(
                delayed(get_candidate_info_UST)(url, n)
                for n, url in enumerate(all_department_links_df['link'].values)
            )
    return len(all_volunteer_data)


def combine_data(department_num, mode, year, choose, folder_path):
    department_num_list = [i for i in range(department_num)]
    dfs_to_concat = []

    dfs_to_concat = Parallel(n_jobs=10)(
        delayed(trans_to_csv)(folder_path, file_name, year, mode, choose)
        for n, file_name in enumerate(department_num_list)
    )
    # 刪除'\r'讓csv檔案可以正常顯示
    df_all_data = (
        pd.concat(dfs_to_concat, ignore_index=True)
        .drop_duplicates()
        .apply(lambda x: x.str.replace('\r', '') if x.dtype == 'object' else x)
    )

    df_all_data.to_csv(
        f'data/{year}_IR3_{mode}_{choose}.csv',
        encoding='utf-8-sig',
        index=False,
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
    folder_path = f"./data/temp/{year}_IR3_{mode}_{choose}"
    match mode:
        case 'U' | 'HS_to_UST':
            if check_data(folder_path):
                department_num = read_data_num(folder_path)
            else:
                (
                    schoolid_to_department_links,
                    schoolid_music_to_department_links,
                ) = department_crawler(mode, year)
                all_department_links_df = organize_department_data(
                    mode,
                    year,
                    schoolid_to_department_links,
                    schoolid_music_to_department_links,
                )
                department_num = content_crawler(
                    mode, all_department_links_df, choose
                )
                save_data(department_num, folder_path)

            combine_data(department_num, mode, year, choose, folder_path)

        case 'UST':
            if check_data(folder_path):
                department_num = read_data_num(folder_path)
            else:
                schoolid_to_department_links = department_crawler_UST(
                    mode, year
                )
                all_department_links_df = organize_department_data_UST(
                    mode, year, schoolid_to_department_links
                )
                department_num = content_crawler(
                    mode, all_department_links_df, choose
                )
                save_data(department_num, folder_path)

            combine_data(department_num, mode, year, choose, folder_path)
