import json
import os
import re

import requests
from bs4 import BeautifulSoup


def record_error(content):
    with open(f"error.txt", "a") as file:
        file.write(content+'\n')
# 儲存json 
def save_json(data_json, code_name):

    # 將列表儲存成 JSON 字串
    json_str = json.dumps(data_json)

    # 將json寫道文件中
    with open(f"data/{code_name}.json", "w") as file:
        file.write(json_str)



def check_json(code_name):
    if os.path.isfile(f"{code_name}.json"):
        data = read_json(code_name)
    else:
        data = []
    return data
        
# 請求網站
def request_url(url):
    """
    requests www.com.tw, cookies must be need.
    cookies need update every once in a while.

    Args:
        url (str): 

    Returns:
        bs4.BeautifulSoup: 
    """
    cookie = "IDE=AHWqTUmx271fCxDq4OOG8BHJ7hyGnI6tNhDK5cDYtEC3v-z3MVZx-xOnxuW9_ZVcV2o; DSID=AJ0cbrm4mJMI8G07HLV-qEcV1sOyDZ7RpNaKozEpR603bBAGnkgGNIJx4o4gSIMkX1z5VAc0JJ2ejib-RVDXYsmpkyhisUiXTnyVZfcsrmNcEMmddj48OiuhcRAexYGgPV-zfeYP_83d56bA7W8r2W6ymmdcqGRfolpeE-Cjee9NK1lYS-Xxj8ZQsJ3DweHfuFWFm2SiQQptLTTK22bVn5iaWSsiHTx2B3BA7DY6NGpncVPctTUAftO5Enhwz0HjqTgq74Mz2rQ1mRVxbWBqW1pA8-b5J7RAMBVjUYwew7ejgCB9KpM7ZL0"
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36',
        'cookie': cookie
    }
    list_req = requests.get(url, headers=headers)
    soup = BeautifulSoup(list_req.text, "html.parser")
    return soup

def getschool(soup) -> dict:
    getschool= soup.findAll('div',{'id':'university_list_row_height'})
    school_schoolid_to_name  = {re.search(r'\d+',x.text).group():re.search(r'[^\d\n]+',x.text).group() for x in getschool}
    return school_schoolid_to_name

def getdepartment(url, schoolid=None) -> dict:
    soup=request_url(url)
    school_department_soup= soup.select('[colspan="2"] [align="left"] a')
    school_department_to_url = {soup.text+str(n): 'https://www.com.tw/vtech/'+ str(soup['href']) for n,soup in enumerate(school_department_soup)}
    if schoolid:
        school_department_to_url = school_department_to_url

    return school_department_to_url



# 學生編號
def get_students_id(student_block):
    
    student_id = student_block.find('img')['src']
    return student_id
def get_choice(volunteer_block):
    choice =[] 
    if volunteer_block.find('img',{'src':'images/putdep1.png'})!=None:
        choice = 1
    else:
        choice = 0
    return choice

def get_volunteer(volunteer_block):
    volunteer =[]
    try:
        volunteer = volunteer_block.find('td',{'width':'71%'}).text
    except:
        volunteer = volunteer_block.find('td',{'width':'75%'}).text
    return volunteer

def get_admission(volunteer_block):
    if volunteer_block.find('div',{'class':re.compile("leftred")})!=None:
        admission = '正取'
    elif volunteer_block.find('div',{'class':re.compile("leftgreen")})!=None:
        admission = '備取'
    else:
        admission = '無錄取'
    return admission

def get_last_choice(all_volunteers):
    last_choice_yn = []
    last_choice_temp=''
    for i in range(len(all_volunteers)):
        if all_volunteers[i][0] == 1:
            last_choice_temp = all_volunteers[i][1]
            last_choice_yn.append('Y')
        else:
            last_choice_yn.append('N')
            continue
        
    if last_choice_temp == '':
        last_choice_temp = '沒有選擇學校'
    last_choice = [last_choice_temp for i in range(len(all_volunteers))]

    return last_choice,last_choice_yn

def get_choice_volunteers(all_volunteers):
    choice_volunteers = [x[1] for x in all_volunteers ] 

    return choice_volunteers

def get_volunteer_status(all_volunteers):
    volunteer_status = [x[2] for x in all_volunteers ] 
    return volunteer_status

def get_seperate_volunteers(all_volunteers):
    school = []
    depertment = []
    all_volunteers_school = [x[1] for x in all_volunteers ]
    for  sd in all_volunteers_school:
        sd = all_volunteers_school[0]
        if '大學' in sd:
            array = sd.split('大學')
            school.append(array[0]+'大學')
        elif '學院' in sd:
            array = sd.split('學院')
            school.append(array[0]+'學院')
        else:
            array = sd.split('學校')
            school.append(array[0]+'學校')
        depertment.append(array[1])
    return school,depertment

def get_volunteers(student_block):
    all_volunteers=[]
    organize_all_volunteers = []
    volunteer_blocks = student_block.findAll('tr' ,{'align':'left'}) 
    for volunteer_block in volunteer_blocks:
        # volunteer_block = volunteer_blocks[1]
        # print(volunteer_block)
        if volunteer_block.text.replace(' ','').replace('\n','')!='':
            choice = get_choice(volunteer_block)
            volunteer = get_volunteer(volunteer_block)
            admission = get_admission(volunteer_block)
            all_volunteers.append([choice,volunteer,admission])

    last_choice,last_choice_yn = get_last_choice(all_volunteers)
    choice_volunteers = get_choice_volunteers(all_volunteers)
    volunteer_status = get_volunteer_status(all_volunteers)
    college,depart = get_seperate_volunteers(all_volunteers)

    organize_all_volunteers = [[last_choice[i],last_choice_yn[i],choice_volunteers[i],volunteer_status[i],college[i],depart[i]] for i in range(len(all_volunteers))]
    return organize_all_volunteers

def organize_candidate_info(students_id,organize_all_volunteers):
    students_id_list = []


    for i in range(len(students_id)):
        students_id_list.append(students_id)


    return list(zip(students_id_list,organize_all_volunteers))

# 檢查學生數量是否正確
def check_student_num(page_soup):

    web_students_num = re.findall('\d+(?=人)',str(page_soup.select('table tr [align="right"] [align="center"] ')[0]))[0]
    return web_students_num
    
def get_candidate_info(url,n):
    print(url)
    page_soup=request_url(url)
    students = []
    student_blocks_1 = page_soup.findAll('tr',{'bgcolor':'#DEDEDC'})
    student_blocks_2 = page_soup.findAll('tr',{'bgcolor':'#FFFFFF'})
    student_block_combine = student_blocks_1 + student_blocks_2
    for student_block in student_block_combine:
        # student_block = student_block_combine[0]
        students_id = get_students_id(student_block)
      #   venue = get_venues(student_block)
        organize_all_volunteers = get_volunteers(student_block)
        
        student_info_list = organize_candidate_info (students_id,organize_all_volunteers)
        students.append(student_info_list)
    
    students_num = len(students)
    web_students_num=check_student_num(page_soup)
    if students_num!=web_students_num:
        record_error(f'{url}--true:{web_students_num},scrape:{students_num}')
    
    # save json
    save_json(students, n)
    return students

