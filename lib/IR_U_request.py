#%%
import re

import requests
from bs4 import BeautifulSoup

from lib.package import record_error, save_json


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
    
    headers = {
    'Cookie': 'cf_chl_2=fa3cfae2fac41e6; cf_clearance=XJ1WuPv94x9MvGX5AUnd5JGNipl9p3auGNr1hxiO3fY-1690997272-0-1-4ec4d5cb.32a23e07.19c58a2b-160.0.0; PHPSESSID=sevl7dva6vpdpkgkougnurofr4; _ga=GA1.1.991696743.1690997276; _ga=GA1.1.991696743.1690997276; _gid=GA1.1.1256375975.1690997276; _ga_GB26Y4NW27=GS1.1.1690999531.2.1.1690999532.59.0.0; _gat_gtag_UA_30208828_1=1',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'
    }
    list_req = requests.get(url, headers=headers)
    soup = BeautifulSoup(list_req.text, "html.parser")
    return soup

def getschool_links(soup, url_domain) -> list:
    getschool= soup.select('[id="university_list_row_height"] a')
    school_links  = list(set([url_domain+tag_a['href'] for tag_a in getschool]))
    school_links.sort()
    return school_links

def getdepartment(url, url_domain) -> dict: # url = mode_to_url[mode]['校系查榜網頁'].replace('QUERY_YEAR',year).replace('QUERY_SCHOOLID',schoolid)
    """
    依照校系榜單的連結抓取校系資料連結
    另外將資料打包成這樣是為了檢查是否有抓齊資料，未來可修改資料結構
    Args:
        url (str): https://www.com.tw/cross/university_1101_111.html #依校系榜單查詢
        schoolid (str): 學校代號 e.g.001 (臺大)

    Returns:
        dict: {'學校代號': '001',
                '學系資料': [{'科系': '中國文學系',
                'link': 'https://www.com.tw/cross/check_001012_NO_0_111_0_3.html'},
                {'科系': '外國語文學系',
                'link': 'https://www.com.tw/cross/check_001022_NO_0_111_0_3.html'}...]}
    """
    soup=request_url(url)
    school_department_soup= soup.select('[align="left"] a')
    school_department_to_url = [
        {
            "科系": soup.text,
            "link": url_domain+str(soup['href'])
        }
        for soup in school_department_soup
    ]
    school_department_to_url = {
        "學校代號":re.findall('\\d+',url)[0],
        "學系資料":school_department_to_url
    }
    return school_department_to_url


# 學生編號
def get_students_id(block_soup):
    students_id_block = block_soup.find('td',{'width':'28%'})
    students_id = students_id_block.find('img')['src']
    return students_id

# 考場
def get_venues(block_soup):
    venue_block = block_soup.find('td',{'width':'28%'})
    venue = venue_block.text.replace('\n','').split(':')[1].replace(' ','')
    return venue

def get_choice(wish_block):
    choice =[] 
    if wish_block.find('img',{'src':'images/putdep1.png'})!=None:
        choice = 1
    else:
        choice = 0
    return choice

def get_wish(wish_block):
    wish =[]
    try:
        wish = wish_block.find('td',{'width':'71%'}).text
    except:
        wish = wish_block.find('td',{'width':'75%'}).text
    return wish

def get_admission(wish_block):
    if wish_block.find('div',{'class':re.compile("leftred")})!=None:
        admission = '正取'
    elif wish_block.find('div',{'class':re.compile("leftgreen")})!=None:
        admission = '備取'
    else:
        admission = '無錄取'
    return admission

def get_last_choice(all_wishes):
    last_choice_yn = []
    last_choice_temp='沒有選擇志願'
    for i in range(len(all_wishes)):
        if all_wishes[i][0] == 1:
            last_choice_temp = all_wishes[i][1]
            last_choice_yn.append('Y')
        else:
            last_choice_yn.append('N')
            continue
        
    if last_choice_temp == '':
        last_choice_temp = '沒有選擇學校'
    last_choice = [last_choice_temp for i in range(len(all_wishes))]
    return last_choice,last_choice_yn

def get_choice_wishes(all_wishes):
    choice_wishes = [x[1] for x in all_wishes ] 

    return choice_wishes

def get_wish_status(all_wishes):
    wish_status = [x[2] for x in all_wishes ] 
    return wish_status

def get_seperate_wishes(all_wishes):
    school = []
    depertment = []
    all_wishes_school = [x[1] for x in all_wishes ]
    for  sd in all_wishes_school:
        if '大學' in sd:
            array = sd.split('大學')
            school.append(array[0]+'大學')
        elif '學院' in sd:
            array = sd.split('學院')
            school.append(array[0]+'學院')
        else:
            array = sd.split('學校')
            school.append(array[0]+'學校')
        depertment.append(array[1].strip())
    return school, depertment

# def get_wishes(student_block):
#     all_wishes=[]
#     wish_blocks = student_block.select('tr[align="left"]')
#     final_wish = '無錄取'
#     for wish_block in wish_blocks:
#         # wish_block = wish_blocks[0]
#         if len(wish_block.select('[align="left"] a:-soup-contains(" ")'))==0:# there is a block without data
#             continue
#         last_choice = 'Y' if len(wish_block.select('[title="分發錄取"]'))>0 else 'N' 
#         wish = wish_block.select('[align="left"] a:-soup-contains(" ")')[0].text
#         college = wish.split(' ')[0] 
#         depart = wish.split(' ')[0]
#         wish = wish.replace(' ','')
#         if last_choice =='Y':
#             final_wish = wish
#         admission = get_admission(wish_block)
#         all_wishes.append([last_choice, wish, admission, college, depart])
#     for single_with in all_wishes:
#         single_with = single_with.insert(0, final_wish)
#     return all_wishes

def get_wishes(student_block, url):
    all_wishes=[]
    wish_blocks = student_block.findAll('tr' ,{'align':'left'}) 
    check_num = re.findall('check_\\d{5,7}',str(wish_blocks))
    for wish_block in wish_blocks: # wish_block = wish_blocks[]
        if wish_block.text.replace(' ','').replace('\n','')!='':
            choice = get_choice(wish_block)
            wish = get_wish(wish_block)
            admission = get_admission(wish_block)
            all_wishes.append([choice,wish,admission])

    last_choice,last_choice_yn = get_last_choice(all_wishes)
    choice_wishes = get_choice_wishes(all_wishes)
    wish_status = get_wish_status(all_wishes)
    college,depart = get_seperate_wishes(all_wishes)
    organize_all_wishes = [[last_choice[i],last_choice_yn[i],choice_wishes[i],wish_status[i],college[i].strip(),depart[i].strip()] for i in range(len(all_wishes))]
    if len(check_num) == len(organize_all_wishes):
        return organize_all_wishes
    else:
        raise ValueError(f"{url}{organize_all_wishes} wish num error")

# 檢查學生數量是否正確
def check_student_num(page_soup):

    web_students_num = re.findall('\d+(?=人)',str(page_soup.select('table tr [align="right"] [align="center"] ')[0]))[0]
    return web_students_num


def get_candidate_info(url,n): # url = "https://www.com.tw/cross/check_002292_NO_1_108_0_3.html"
    print(url)
    page_soup = request_url(url)
    count_person = re.findall('\\d+(?=人)',page_soup.select('[align="center"] td[colspan="8"] div[align="center"]')[0].text)[0]
    if count_person == '0':
        return
    students = []
    student_blocks_1 = page_soup.findAll('tr',{'bgcolor':'#DEDEDC'})
    student_blocks_2 = page_soup.findAll('tr',{'bgcolor':'#FFFFFF'})
    student_block_combine = student_blocks_1 + student_blocks_2
    for student_block in student_block_combine:
        # student_block = student_block_combine[0]
        students_id = get_students_id(student_block)
        venue = get_venues(student_block)
        organize_all_wishes = get_wishes(student_block, url)
        student_info_list = [[students_id, venue]+sublist for sublist in organize_all_wishes]
        students.extend(student_info_list)
    students_num = len(students)
    web_students_num=check_student_num(page_soup)
    if students_num!=web_students_num:
        record_error(f'{url}--true:{web_students_num},scrape:{students_num}')
    
    # save json
    save_json(students, n)
    return students



def add_year_col(df, year):
    df['學年度'] = str(year)
    return df
# %%
