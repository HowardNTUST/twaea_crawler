import pandas as pd
from modules.IR_crawler import main_crawler

if __name__ == "__main__":
    for mode in ('U', 'HS_to_UST', 'UST'):
        year = '112'
        choose = '正式'
        main_crawler(mode, year, choose)
