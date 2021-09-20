from flask import Flask, render_template, request, redirect, url_for
# from gevent import pywsgi
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
    logistic_model = 'Gua/model/logistic_model.joblib'
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

# def get_int_rate():
    XGBRegressor = 'Gua/model/fund_XGBRegressor.joblib'
    x_pred = [[input_dict['grade'], input_dict['term']]]
    model = joblib.load(XGBRegressor)
    input_dict['int_rate'] = model.predict(np.array(x_pred))[0]
    print('int_rate: ', input_dict['int_rate'])

# def get_funded_amnt():
    XGBRegressor = 'Gua/model/fund_XGBRegressor.joblib'
    x_pred = [[input_dict['grade'], input_dict['loan_amnt']]]
    model = joblib.load(XGBRegressor)
    input_dict['funded_amnt'] = model.predict(np.array(x_pred))[0]
    print('funded_amnt: ', input_dict['funded_amnt'])

    # check_id = cur.fetchone()
    # if check_id is None:
    #     check_id = 'data error'
    # print('check_id: ', check_id)

    cur.execute(f"""UPDATE pred_data SET \
                    grade = {input_dict['grade']}, \
                    int_rate = {input_dict['int_rate']}, \
                    funded_amnt = {input_dict['funded_amnt']} \
                    WHERE id = '{time_hash}';""")
    con.commit()
    return render_template('form_result.html', page_header = 'Prediction', prediction1 = input_dict['int_rate'], prediction2 = input_dict['funded_amnt'])


if __name__=="__main__":
    app.run(debug=True)