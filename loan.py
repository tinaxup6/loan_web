from flask import Flask, render_template, request, redirect, url_for
from gevent import pywsgi
import joblib
import numpy as np
import sqlite3
import hashlib
import datetime
now = datetime.datetime.today()
now_str = now.strftime("%Y%m%d%H%M%S")
time_hash = hashlib.md5(bytes(now_str, encoding='utf-8')).hexdigest()

app = Flask(__name__)

# model = pickle.load(open('XXX.plk', 'rb'))

# @app.route('/')
# def index():
#     return '<h1>Hello!</h1>'


@app.route('/')
def home():
    return render_template('home.html')

@app.route('/base')
def base():
    return render_template('base.html')

@app.route('/form_result', methods=['GET', 'POST'])
def form_result():
    # print(request.form)
    # purpose = float(request.form.get('purpose',))
    # mort_acc = float(request.form.get('mort_acc',))
    # pub_rec = float(request.form.get('pub_rec',))
    # tot_coll_amt = float(request.form.get('tot_coll_amt',))
    # bc_open_to_buy = float(request.form.get('bc_open_to_buy',))
    # num_tl_op_past_12m = float(request.form.get('num_tl_op_past_12m',))
    # term = float(request.form.get('term',))
    # annual_inc = float(request.form.get('annual_inc',))
    # loan_amnt = float(request.form.get('loan_amnt',))
    # installment = float(request.form.get('installment',))
    print(time_hash)
    # print(annual_inc, type(annual_inc))
    input_col = ["purpose", "mort_acc", "pub_rec", "tot_coll_amt", "bc_open_to_buy", "num_tl_op_past_12m", "term", "annual_inc", "loan_amnt", "installment"]
    input_var = []
    for col in input_col:
        col_var = request.form.get(f'{col}',)
        col_float = float(col_var)
        input_var.append(col_float)
    input_dict = dict(zip(input_col, input_var))

    con = sqlite3.connect('loan.db')
    cur = con.cursor()
    try:
        cur.execute(f'''INSERT INTO pred_data (id) VALUES ('{time_hash}')''')
        con.commit()
    except:
        pass
    # input_dict = {'purpose': 5.0, 'mort_acc': 567.0, 'pub_rec': 345.0, 'tot_coll_amt': 345.0, 'bc_open_to_buy': 3.0, 'num_tl_op_past_12m': 345.0, 'term': 3.0, 'annual_inc': 456.0, 'loan_amnt': 345.0, 'installment': 345.0}
    for item in input_dict:
        update_query = f'''UPDATE pred_data SET {item} = {input_dict[f'{item}']} WHERE id = '{time_hash}';'''
        cur.execute(update_query)
        con.commit()
    
# def get_grade():
    logistic_model = 'model/logistic_model.joblib'
    # input_col = ["purpose", "mort_acc", "pub_rec", "tot_coll_amt", "bc_open_to_buy", "num_tl_op_past_12m", "term", "annual_inc", "loan_amnt", "installment"]
    # input_dict = {'purpose': 5.0, 'mort_acc': 567.0, 'pub_rec': 345.0, 'tot_coll_amt': 345.0, 'bc_open_to_buy': 3.0, 'num_tl_op_past_12m': 345.0, 'term': 3.0, 'annual_inc': 456.0, 'loan_amnt': 345.0, 'installment': 345.0}
    input_grade = ["purpose", "mort_acc", "pub_rec", "tot_coll_amt", "bc_open_to_buy", "num_tl_op_past_12m"]
    input_list = []
    for item in input_grade:
        input_list.append(input_dict[f'{item}'])
    x_pred = [input_list]
    model = joblib.load(logistic_model)
    input_dict['grade'] = model.predict(np.array(x_pred))[0]
    print('grade: ', input_dict['grade'])

    con.row_factory = sqlite3.Row
    cur = con.cursor()
    collist = ['id', 'loan_amnt', 'funded_amnt', 'funded_amnt_inv', 'term', 'int_rate', 'installment', 'grade', 'emp_length', 'home_ownership', 'annual_inc', 'verification_status', 'purpose', 'dti', 'delinq_2yrs', 'fico_range_low', 'fico_range_high', 'inq_last_6mths', 'open_acc', 'pub_rec', 'revol_bal', 'revol_util', 'total_acc', 'initial_list_status', 'last_fico_range_high', 'last_fico_range_low', 'collections_12_mths_ex_med', 'acc_now_delinq', 'tot_coll_amt', 'tot_cur_bal', 'open_act_il', 'total_bal_il', 'max_bal_bc', 'all_util', 'total_rev_hi_lim', 'inq_fi', 'total_cu_tl', 'inq_last_12m', 'acc_open_past_24mths', 'avg_cur_bal', 'bc_open_to_buy', 'chargeoff_within_12_mths', 'delinq_amnt', 'mort_acc', 'num_accts_ever_120_pd', 'num_actv_bc_tl', 'num_actv_rev_tl', 'num_bc_sats', 'num_bc_tl', 'num_il_tl', 'num_op_rev_tl', 'num_rev_accts', 'num_rev_tl_bal_gt_0', 'num_sats', 'num_tl_120dpd_2m', 'num_tl_30dpd', 'num_tl_90g_dpd_24m', 'num_tl_op_past_12m', 'pct_tl_nvr_dlq', 'percent_bc_gt_75', 'pub_rec_bankruptcies', 'tax_liens', 'tot_hi_cred_lim', 'total_bal_ex_mort', 'total_bc_limit', 'total_il_high_credit_limit']
    collist.remove('id')
    
# def get_int_rate():
    collist.remove('int_rate')
    cur.execute(f'''SELECT * FROM pred_data WHERE id = '{time_hash}';''')
    fetc = cur.fetchone()
    fetc_dict = dict(zip(fetc.keys(), list(fetc)))

    XGBRegressor_rate = 'model/0920_rate_XGBRegressor.joblib'
    input_list = []
    for item in collist:
        input_list.append(fetc_dict[f'{item}'])
    x_pred = [input_list]
    model = joblib.load(XGBRegressor_rate)
    fetc_dict['int_rate'] = model.predict(np.array(x_pred))[0]
    cur.execute(f'''UPDATE pred_data SET int_rate = {fetc_dict['int_rate']} WHERE id = '{time_hash}';''')
    con.commit()
    print('int_rate: ', fetc_dict['int_rate'])
    collist.append('int_rate')

# def get_funded_amnt():
    collist.remove('funded_amnt')
    cur.execute(f'''SELECT * FROM pred_data WHERE id = '{time_hash}';''')
    fetc = cur.fetchone()
    fetc_dict = dict(zip(fetc.keys(), list(fetc)))
    
    XGBRegressor_fund = 'model/0920_funded_XGBRegressor.joblib'
    input_list = []
    for item in collist:
        input_list.append(fetc_dict[f'{item}'])
    x_pred = [input_list]
    model = joblib.load(XGBRegressor_fund)
    fetc_dict['funded_amnt'] = model.predict(np.array(x_pred))[0]
    cur.execute(f'''UPDATE pred_data SET funded_amnt = {fetc_dict['funded_amnt']} WHERE id = '{time_hash}';''')
    con.commit()
    print('funded_amnt: ', fetc_dict['funded_amnt'])
    collist.append('funded_amnt')

    # check_id = cur.fetchone()
    # if check_id is None:
    #     check_id = 'data error'
    # print('check_id: ', check_id)
    
    prediction1 = fetc_dict['int_rate']
    prediction2 = fetc_dict['funded_amnt']
    return render_template('form_result.html', page_header = 'Prediction', prediction1 = prediction1, prediction2 = prediction2)

if __name__=="__main__":
    app.run(debug=True)