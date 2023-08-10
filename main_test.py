import pandas as pd
from modules.IR_crawler import main_crawler
import time

if __name__ == "__main__":
    # 開始測量
    start = time.time()
    for mode in ('U', 'HS_to_UST', 'UST'):
        year = '112'
        choose = '測試'
        main_crawler(mode, year, choose)
    
    # 結束測量
    end = time.time()

    # 輸出結果
    print("執行時間：%f 秒" % (end - start))
