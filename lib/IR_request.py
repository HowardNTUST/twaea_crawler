import json
import os
import re

import requests
from bs4 import BeautifulSoup

from lib.package import record_error, save_json


# 請求網站
def request_url(url: str) -> BeautifulSoup:
    """
    requests www.com.tw, cookies must be need.
    cookies need update every once in a while.

    Args:
        url (str):

    Returns:
        bs4.BeautifulSoup:
    """

    headers = {
        'Cookie': 'PHPSESSID=sevl7dva6vpdpkgkougnurofr4; _ga=GA1.1.991696743.1690997276; _ga=GA1.1.991696743.1690997276; cf_chl_2=778bd3bf9e8d1e4; cf_clearance=5MTA6pelb0Tqi._LhmhZHUcLb8YngYVTcnrR57r8.1k-1691386281-0-1-8b914620.dd32dbaa.dc9019c0-160.0.0; _ga_GB26Y4NW27=GS1.1.1691386284.9.0.1691386284.60.0.0; _gid=GA1.1.213420813.1691386285; _gat_gtag_UA_30208828_1=1',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
    }
    list_req = requests.get(url, headers=headers)
    soup = BeautifulSoup(list_req.text, "html.parser")
    return soup


# def getschool(soup) -> dict:
#     getschool= soup.findAll('div',{'id':'university_list_row_height'})
#     school_schoolid_to_name  = {re.search(r'\d+',x.text).group():re.search(r'[^\d\n]+',x.text).group() for x in getschool}
#     return school_schoolid_to_name


def getschool_links_UST(
    getschool_soup: BeautifulSoup, url_domain: str
) -> list:
    getschool = getschool_soup.select('[id="university_list_row_height"] a')
    school_links = list(
        set(
            [
                url_domain + tag_a['href'].replace('m_', '')
                for tag_a in getschool
            ]
        )
    )
    school_links.sort()
    return school_links


def getschool_links(soup: BeautifulSoup, url_domain: str) -> list:
    getschool = soup.select('[id="university_list_row_height"] a')
    school_links = list(
        set([url_domain + tag_a['href'] for tag_a in getschool])
    )
    school_links.sort()
    return school_links


def getdepartment(
    url: str, url_domain: str
) -> (
    dict
):  # url = mode_to_url[mode]['校系查榜網頁'].replace('QUERY_YEAR',year).replace('QUERY_SCHOOLID',schoolid)
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
    soup = request_url(url)
    school_department_soup = soup.select('[align="left"] a')
    school_department_to_url = [
        {"科系": soup.text, "link": url_domain + str(soup['href'])}
        for soup in school_department_soup
    ]
    school_department_to_url = {
        "學校代號": re.findall('\\d+', url)[0],
        "學系資料": school_department_to_url,
    }
    return school_department_to_url


def getdepartment_UST(url: str, schoolid=None) -> dict:
    # url = 'https://www.com.tw/vtech/university_105_112.html'
    soup = request_url(url)
    school_department_soup = soup.select('[colspan="2"] [align="left"] a')
    school_department_to_url = {
        soup.text + str(n): 'https://www.com.tw/vtech/' + str(soup['href'])
        for n, soup in enumerate(school_department_soup)
    }
    if schoolid:
        school_department_to_url = school_department_to_url

    return school_department_to_url


# 學生編號
def get_students_id(student_block: BeautifulSoup) -> str:
    """抓取學生編號的圖片

    Args:
        student_block (soup): 學生資料的block

    Returns:
        image_url: 學生編號的圖片網址
    """
    student_id_block = student_block.find('td', {'width': '28%'})
    student_id = student_id_block.find('img')['src']
    return student_id


# 學生編號
def get_students_id_UST(student_block: BeautifulSoup) -> str:
    """抓取學生編號的圖片find('img')['src']

    Args:
        student_block (soup): 學生資料的block

    Returns:
        image_url: 學生編號的圖片網址
    """
    students_id = student_block.find('img')['src']
    return students_id


# 考場
def get_venues(student_block: BeautifulSoup) -> str:
    """
    抓取考場只有U跟UST可以抓取到，但是後續不會用到
    .find('td',{'width':'28%'})

    Args:
        student_block (soup): 學生資料的block

    Returns:
        venue(str): 考場

    """
    venue_block = student_block.find('td', {'width': '28%'})
    venue = venue_block.text.replace('\n', '').split(':')[1].replace(' ', '')
    return venue


def get_choice(wish_block: BeautifulSoup) -> bool:
    """是否選擇志願學校
    在get_wishes使用

    Args:
        wish_block (soup): 志願資料的block

    Returns:
        choice: bool
    """
    choice = []
    if wish_block.find('img', {'src': 'images/putdep1.png'}) != None:
        choice = 1
    else:
        choice = 0
    return choice


def get_wish(wish_block: BeautifulSoup) -> str:
    """抓取志願學校

    Args:
        wish_block (soup): 志願資料的block

    Returns:
        wish(str): 志願學校
    """
    wish = []
    try:
        wish = wish_block.find('td', {'width': '71%'}).text
    except:
        wish = wish_block.find('td', {'width': '75%'}).text
    return wish


def get_admission(wish_block: BeautifulSoup) -> str:
    """抓取錄取狀態(正取、備取、無錄取)

    Args:
        wish_block (soup): 志願資料的block

    Returns:
        admission(str): 錄取狀態
    """
    if wish_block.find('div', {'class': re.compile("leftred")}) != None:
        admission = '正取'
    elif wish_block.find('div', {'class': re.compile("leftgreen")}) != None:
        admission = '備取'
    else:
        admission = '無錄取'
    return admission


def get_last_choice(all_wishes: list) -> (list, list):
    """從志願中抓取最終選擇學校，最終選擇學校每個志願都一樣

    Args:
        all_wishes (list): _description_

    Returns:
        last_choice (list): 每個志願最終選擇學校都相同
        last_choice_yn (list): 最終選擇學校y or n
    """
    last_choice_yn = ['Y' if wish[0] == 1 else 'N' for wish in all_wishes]
    last_choice_temp = next(
        (wish[1] for wish in all_wishes if wish[0] == 1), ''
    )
    last_choice_temp = '沒有選擇學校' if last_choice_temp == '' else last_choice_temp
    last_choice = [last_choice_temp] * len(all_wishes)
    return last_choice, last_choice_yn


def get_seperate_wishes(all_wishes: list) -> (list, list):
    """把大學跟科系分開

    Args:
        all_wishes (list): 志願資料

    Returns:
        school(list): 學校
        depertment(list): 科系
    """
    school = []
    depertment = []
    all_wishes_school = [x[1] for x in all_wishes]
    for sd in all_wishes_school:
        if '大學' in sd:
            array = sd.split('大學')
            school.append(array[0] + '大學')
        elif '學院' in sd:
            array = sd.split('學院')
            school.append(array[0] + '學院')
        else:
            array = sd.split('學校')
            school.append(array[0] + '學校')
        depertment.append(array[1].strip())
    return school, depertment


# 在這裡檢查申請數量
def get_wishes(student_block, url):
    all_wishes = []
    wish_blocks = student_block.findAll('tr', {'align': 'left'})
    check_num = re.findall('check_\\d{5,7}', str(wish_blocks))
    for wish_block in wish_blocks:  # wish_block = wish_blocks[]
        if wish_block.text.replace(' ', '').replace('\n', '') != '':
            choice = get_choice(wish_block)
            wish = get_wish(wish_block)
            admission = get_admission(wish_block)
            all_wishes.append([choice, wish, admission])

    last_choice, last_choice_yn = get_last_choice(all_wishes)
    choice_wishes = [x[1] for x in all_wishes]
    wish_status = [x[2] for x in all_wishes]
    college, depart = get_seperate_wishes(all_wishes)
    organize_all_wishes = [
        [
            last_choice[i],
            last_choice_yn[i],
            choice_wishes[i],
            wish_status[i],
            college[i].strip(),
            depart[i].strip(),
        ]
        for i in range(len(all_wishes))
    ]
    if len(check_num) == len(organize_all_wishes):
        return organize_all_wishes
    else:
        raise ValueError(f"{url}{organize_all_wishes} wish num error")


class Wish:
    def __init__(self, student_block, url):
        self.student_block = student_block
        self.url = url

    def _get_choice(wish_block: BeautifulSoup) -> bool:
        """是否選擇志願學校
        在get_wishes使用

        Args:
            wish_block (soup): 志願資料的block

        Returns:
            choice: bool
        """
        choice = []
        if wish_block.find('img', {'src': 'images/putdep1.png'}) != None:
            choice = 1
        else:
            choice = 0
        return choice

    def _get_wish(wish_block: BeautifulSoup) -> str:
        """抓取志願學校

        Args:
            wish_block (soup): 志願資料的block

        Returns:
            wish(str): 志願學校
        """
        wish = []
        try:
            wish = wish_block.find('td', {'width': '71%'}).text
        except:
            wish = wish_block.find('td', {'width': '75%'}).text
        return wish

    def _get_admission(wish_block: BeautifulSoup) -> str:
        """抓取錄取狀態(正取、備取、無錄取)

        Args:
            wish_block (soup): 志願資料的block

        Returns:
            admission(str): 錄取狀態
        """
        if wish_block.find('div', {'class': re.compile("leftred")}) != None:
            admission = '正取'
        elif (
            wish_block.find('div', {'class': re.compile("leftgreen")}) != None
        ):
            admission = '備取'
        else:
            admission = '無錄取'
        return admission

    def _get_last_choice(all_wishes: list) -> (list, list):
        """從志願中抓取最終選擇學校，最終選擇學校每個志願都一樣

        Args:
            all_wishes (list): _description_

        Returns:
            last_choice (list): 每個志願最終選擇學校都相同
            last_choice_yn (list): 最終選擇學校y or n
        """
        last_choice_yn = ['Y' if wish[0] == 1 else 'N' for wish in all_wishes]
        last_choice_temp = next(
            (wish[1] for wish in all_wishes if wish[0] == 1), ''
        )
        last_choice_temp = (
            '沒有選擇學校' if last_choice_temp == '' else last_choice_temp
        )
        last_choice = [last_choice_temp] * len(all_wishes)
        return last_choice, last_choice_yn

    def _get_seperate_wishes(all_wishes: list) -> (list, list):
        """把大學跟科系分開

        Args:
            all_wishes (list): 志願資料

        Returns:
            school(list): 學校
            depertment(list): 科系
        """
        school = []
        depertment = []
        all_wishes_school = [x[1] for x in all_wishes]
        for sd in all_wishes_school:
            if '大學' in sd:
                array = sd.split('大學')
                school.append(array[0] + '大學')
            elif '學院' in sd:
                array = sd.split('學院')
                school.append(array[0] + '學院')
            else:
                array = sd.split('學校')
                school.append(array[0] + '學校')
            depertment.append(array[1].strip())
        return school, depertment

    def get_wishes(self):
        all_wishes = []
        wish_blocks = self.student_block.findAll('tr', {'align': 'left'})
        check_num = re.findall('check_\\d{5,7}', str(wish_blocks))
        for wish_block in wish_blocks:  # wish_block = wish_blocks[]
            if wish_block.text.replace(' ', '').replace('\n', '') != '':
                choice = get_choice(wish_block)
                wish = get_wish(wish_block)
                admission = get_admission(wish_block)
                all_wishes.append([choice, wish, admission])

        last_choice, last_choice_yn = get_last_choice(all_wishes)
        choice_wishes = [x[1] for x in all_wishes]
        wish_status = [x[2] for x in all_wishes]
        college, depart = get_seperate_wishes(all_wishes)
        organize_all_wishes = [
            [
                last_choice[i],
                last_choice_yn[i],
                choice_wishes[i],
                wish_status[i],
                college[i].strip(),
                depart[i].strip(),
            ]
            for i in range(len(all_wishes))
        ]
        if len(check_num) == len(organize_all_wishes):
            return organize_all_wishes
        else:
            raise ValueError(f"{self.url}{organize_all_wishes} wish num error")


# 檢查學生數量是否正確
def check_student_num(page_soup):
    """獲取志願學生數量

    Args:
        page_soup (soup):

    Returns:
        web_students_num(int): 人數
    """
    web_students_num = int(
        re.findall(
            '\d+(?=人)',
            str(
                page_soup.select('table tr [align="right"] [align="center"] ')[
                    0
                ]
            ),
        )[0]
    )
    return web_students_num


def get_candidate_info(url, n):
    """抓取所有學生的資料

    Args:
        url (str): 學系資料連結
        n (int): 學系資料連結的index

    Returns:
        students (list): 學生資料
    """
    # url = "https://www.com.tw/vtech/check_101001_NO_1_112_1_3.html"
    print(url)
    page_soup = request_url(url)
    count_person = re.findall(
        '\\d+(?=人)',
        page_soup.select(
            '[align="center"] td[colspan="8"] div[align="center"]'
        )[0].text,
    )[0]
    if count_person == '0':
        return []
    students = []
    students_num = 0
    student_blocks_1 = page_soup.findAll('tr', {'bgcolor': '#DEDEDC'})
    student_blocks_2 = page_soup.findAll('tr', {'bgcolor': '#FFFFFF'})
    student_block_combine = student_blocks_1 + student_blocks_2
    for student_block in student_block_combine:
        # student_block = student_block_combine[0]
        students_id = get_students_id(student_block)
        venue = get_venues(student_block)
        organize_all_wishes = Wish(student_block, url).get_wishes()
        student_info_list = [
            [students_id, venue] + sublist for sublist in organize_all_wishes
        ]
        students.extend(student_info_list)
        students_num += 1
    web_students_num = check_student_num(page_soup)
    if students_num != web_students_num:
        record_error(f'{url}--true:{web_students_num},scrape:{students_num}')

    # save json
    save_json(students, n)
    return students


def get_candidate_info_UST(url, n):
    # url ='https://www.com.tw/vtech/check_101001_NO_1_112_1_3.html'
    print(url)
    page_soup = request_url(url)
    count_person = re.findall(
        '\\d+(?=人)',
        page_soup.select(
            '[align="center"] td[colspan="8"] div[align="center"]'
        )[0].text,
    )[0]
    if count_person == '0':
        return []
    students = []
    students_num = 0
    student_blocks_1 = page_soup.findAll('tr', {'bgcolor': '#DEDEDC'})
    student_blocks_2 = page_soup.findAll('tr', {'bgcolor': '#FFFFFF'})
    student_block_combine = student_blocks_1 + student_blocks_2
    for student_block in student_block_combine:
        # student_block = student_block_combine[0]
        students_id = get_students_id_UST(student_block)
        #   venue = get_venues(student_block)
        organize_all_wishes = Wish(student_block, url).get_wishes()

        student_info_list = [
            [students_id] + sublist for sublist in organize_all_wishes
        ]
        students.extend(student_info_list)
        students_num += 1
    web_students_num = check_student_num(page_soup)
    if students_num != web_students_num:
        record_error(f'{url}--true:{web_students_num},scrape:{students_num}')

    # save json
    save_json(students, n)
    return students


def add_year_col(df, year):
    df['學年度'] = str(year)
    return df


# %%
