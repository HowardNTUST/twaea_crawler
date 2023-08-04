import pandas as pd

from src.IR_U_crawler import main_crawler

if __name__ == "__main__":
    for mode in ('U', 'HS_to_UST'):
        year = '112'
        main_crawler(mode, year)

    # year = '112'
    # mode = 'UST'
    # main_crawler(mode, year)
