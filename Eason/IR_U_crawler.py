from lib.IR_U_request import request_url, getschool, getdepartment
from lib.package import dict_write_json

from joblib import Parallel, delayed

def main_crawler(year):
    url = f'https://www.com.tw/cross/university_list{year}.html'
    getschool_soup = request_url(url)
    school_schoolid_to_name = getschool(getschool_soup)

    schoolid_to_department_links = Parallel(n_jobs=10)(
                        delayed(getdepartment)(f'https://www.com.tw/cross/university_{schoolid}_{year}.html',schoolid) for schoolid in school_schoolid_to_name
                    )
    return schoolid_to_department_links
    # for school_data in schoolid_to_department_links:# school_data = schoolid_to_department_links[0] 
    #     for department, url in list(school_data.values())[0]: # list(school_data.values())[0]
    #         if 'music_dep' in url:
    #             schoolid_to_department_links[0][next(iter(school_data))].pop()

if __name__=="__main_":
    year = 111
    schoolid_to_department_links = main_crawler(year)
