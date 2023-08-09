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


def main_crawler(mode, year):
    """正式用的爬蟲

    Args:
        mode (_type_): _description_
        year (_type_): _description_

    Returns:
        _type_: _description_
    """
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
        f'data/{mode}_{year}_check_file.csv', encoding='utf-8-sig'
    )

    # 正式
    all_volunteer_data = Parallel(
        n_jobs=10
    )(  # url = all_department_links_df['link'].values[0]
        delayed(get_candidate_info)(url, n)
        for n, url in enumerate(all_department_links_df['link'].values)
    )

    # # 測試
    # part_department_links_df = all_department_links_df.sample(
    #     n=10, replace=False
    # )
    # all_volunteer_data = Parallel(n_jobs=10)(
    #     delayed(get_candidate_info)(url, n)
    #     for n, url in enumerate(part_department_links_df['link'].values)
    # )

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
        f'data/{year}_IR3_{mode}_new.csv', encoding='utf-8-sig', index=False
    )

    # volunteer_reorganize_data = list(filter(None, all_volunteer_data))  # type: ignore
    # (
    #     pd.DataFrame(
    #         list(
    #             itertools.chain.from_iterable(all_volunteer_data)
    #         ),  # type: ignore
    #         columns=[
    #             '准考證號碼',
    #             '考區',
    #             '最終選擇的志願',
    #             '最終志願',
    #             '選擇哪些志願',
    #             '錄取狀況',
    #             '志願序的大學',
    #             '志願序的科系',
    #         ],
    #     )
    #     .pipe(add_year_col, year=year)
    #     .loc[
    #         :,
    #         [
    #             '學年度',
    #             '准考證號碼',
    #             '考區',
    #             '最終選擇的志願',
    #             '選擇哪些志願',
    #             '錄取狀況',
    #             '最終志願',
    #             '志願序的大學',
    #             '志願序的科系',
    #         ],
    #     ]
    # .drop_duplicates()
    # # 刪除'\r'讓csv檔案可以正常顯示
    # .apply(lambda x: x.str.replace('\r', '') if x.dtype == 'object' else x)
    # ).to_csv(f'data/{year}_IR3_{mode}.csv', encoding='UTF-8-sig')

    # return volunteer_reorganize_data
