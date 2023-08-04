from lib.IR_U_request import request_url, getschool, getdepartment,get_candidate_info
from lib.package import dict_write_json,trans_to_csv

from joblib import Parallel, delayed
import pandas as pd


#=============================111統測甄選===============================
def main_crawler(year):
    url = f'https://www.com.tw/vtech/'
    getschool_soup = request_url(url)
    school_schoolid_to_name = getschool(getschool_soup)

    # url = 'https://www.com.tw/vtech/university_102_111.html'
    schoolid_to_department_links = Parallel(n_jobs=10)(
                        delayed(getdepartment)(f'https://www.com.tw/vtech/university_{schoolid}_{year}.html',schoolid) for schoolid in school_schoolid_to_name
                    )
    return schoolid_to_department_links

def content_crawler(schoolid_to_department_links):
    
    department_list =[]
    for n,school in enumerate(schoolid_to_department_links):
        for value in schoolid_to_department_links[n].values():
            department_list.append(value)
        
        
    # n=1
    # department_href = department_list[n]
    # url = department_href
    department_data =Parallel(n_jobs=10)(
                    delayed(get_candidate_info)(department,n) for n,department in enumerate(department_list)
                )
    # students = get_candidate_info(department_href,n)

    return len(department_list)

def combine_data(department_num,year):
    department_num_list = [i for i in range(department_num)]
    df_all_data = pd.DataFrame()
    df_all_data =df_all_data.append(Parallel(n_jobs=10)(
                    delayed(trans_to_csv)(file_name,year) for n,file_name in enumerate(department_num_list)
                ))
    df_all_data.to_csv(f'{year}_IR3_UST_new.csv',index='UTF-8-sig')


if __name__=="__main__":
    year = 111
    schoolid_to_department_links = main_crawler(year)
    department_num = content_crawler(schoolid_to_department_links)
    combine_data(department_num,year)
    