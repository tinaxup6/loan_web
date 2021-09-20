import os
import csv, json
import hashlib
import datetime
import pandas
import sqlite3
# 創造一個用時間 hash 過的值，用作 id
now = datetime.datetime.today()
now_str = now.strftime("%Y%m%d%H%M%S")
time_hash = hashlib.md5(bytes(now_str, encoding = 'utf-8')).hexdigest()

db_name = "loan.db"
table_name = "pred_data"
ori_data = "0916_Grade_Logistic.csv"
mean_value = "mean_value.json"
# 取得 collist
# with open(ori_data, newline = '') as data:
#     rows = csv.DictReader(data)
#     collist = rows.fieldnames
collist = ['id', 'loan_amnt', 'funded_amnt', 'funded_amnt_inv', 'term', 'int_rate', 'installment', 'grade', 'emp_length', 'home_ownership', 'annual_inc', 'verification_status', 'purpose', 'dti', 'delinq_2yrs', 'fico_range_low', 'fico_range_high', 'inq_last_6mths', 'open_acc', 'pub_rec', 'revol_bal', 'revol_util', 'total_acc', 'initial_list_status', 'last_fico_range_high', 'last_fico_range_low', 'collections_12_mths_ex_med', 'acc_now_delinq', 'tot_coll_amt', 'tot_cur_bal', 'open_act_il', 'total_bal_il', 'max_bal_bc', 'all_util', 'total_rev_hi_lim', 'inq_fi', 'total_cu_tl', 'inq_last_12m', 'acc_open_past_24mths', 'avg_cur_bal', 'bc_open_to_buy', 'chargeoff_within_12_mths', 'delinq_amnt', 'mort_acc', 'num_accts_ever_120_pd', 'num_actv_bc_tl', 'num_actv_rev_tl', 'num_bc_sats', 'num_bc_tl', 'num_il_tl', 'num_op_rev_tl', 'num_rev_accts', 'num_rev_tl_bal_gt_0', 'num_sats', 'num_tl_120dpd_2m', 'num_tl_30dpd', 'num_tl_90g_dpd_24m', 'num_tl_op_past_12m', 'pct_tl_nvr_dlq', 'percent_bc_gt_75', 'pub_rec_bankruptcies', 'tax_liens', 'tot_hi_cred_lim', 'total_bal_ex_mort', 'total_bc_limit', 'total_il_high_credit_limit']

# 取得各欄位 mean
def mean_data():
    if os.path.isfile(mean_value):
        pass
    else:
        df = pandas.read_csv(ori_data)
        mean_dict = dict(df.describe().T['mean'])
        with open(mean_value, 'w') as outfile:
            json.dump(mean_dict, outfile)
    with open(mean_value, 'r') as readfile:
        data = json.load(readfile)
        # for col in collist:
        #     print(col, round(data[f'{col}'], 2))


# 將 SQL 寫成文檔，後讀取作為 execute 輸入，並刪掉文檔
def creat_table(create_file = "creat_table.txt"):
    creat_file_w = open(create_file, 'w') # 創造一個文檔
    create_head = f'''CREATE TABLE {table_name} (id text PRIMARY KEY'''
    creat_file_w.write(create_head) # 開始寫入 SQL 語法內容
    with open(mean_value, 'r') as readfile:
        data = json.load(readfile)
    for col in collist:
        if col == 'id': # 因為 create_head 已寫 id 了所以略過
            pass
        else:
            creat_file_w.write(', \n')
            creat_file_w.write(col)
            creat_file_w.write(' float')
            creat_file_w.write(' DEFAULT ')
            creat_file_w.write(str(round(data[f'{col}'], 2)))
    creat_file_w.write(');')
    creat_file_w.close() # 完成寫入，關閉文檔

    creat_file_r = open(create_file, 'r') # 讀取該文檔
    cur.execute(creat_file_r.read()) # 將內容（SQL）視為 execute 輸入
    con.commit() # sqlite3 存檔
    os.remove(create_file) # 刪掉文檔


def query_sqlite3():
    cur.execute(f'''SELECT count(name) FROM sqlite_master WHERE type='table' AND name='{table_name}';''')
    if cur.fetchone()[0] != 1: # 確認 table 是否已存在，0 為無，1 為有，不會有其他數值
        creat_table()
    try:
        cur.execute(f'''INSERT INTO {table_name} (id) VALUES ('{time_hash}')''')
        con.commit()
    except:
        pass
    
    input_dict = {'purpose': 5.0, 'mort_acc': 567.0, 'pub_rec': 345.0, 'tot_coll_amt': 345.0, 'bc_open_to_buy': 3.0, 'num_tl_op_past_12m': 345.0, 'term': 3.0, 'annual_inc': 456.0, 'loan_amnt': 345.0, 'installment': 345.0}
    for item in input_dict:
        update_query = f'''UPDATE pred_data SET {item} = {input_dict[f'{item}']} WHERE id = 'ee';'''
        cur.execute(update_query)
        con.commit()

if __name__ == "__main__":
    mean_data()
    con = sqlite3.connect(f'{db_name}')
    cur = con.cursor()
    query_sqlite3()
    con.close()