import pandas as pd

from modules.IR_U_crawler import main_crawler
from modules.IR_UST import main_crawler as main_crawler_UST

if __name__ == "__main__":
    for mode in ('U', 'HS_to_UST'):
        year = '112'
        main_crawler(mode, year)

    # main_crawler_UST(mode='UST', year='112')

    year = '112'
    mode = 'UST'
    main_crawler_UST(mode, year)
