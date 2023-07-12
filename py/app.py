from tinydb import TinyDB, Query
from flask import Flask, make_response, jsonify, request
from datetime import datetime
from flask_cors import CORS
import logging
import json

app = Flask(__name__)
CORS(app, methods=["GET", "POST"])

db_dir = '/app/db/'
dpm_db = db_dir + "department.json"
dpm_table = "Department"
product_db = db_dir + "product.json"
product_table = "Product"

sale_table = "Sale"

log = logging.getLogger('flask_app')
log.setLevel(logging.INFO)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
log.addHandler(console_handler)


def ok(msg='OK', data=None):
    response_data = {
        'message': msg,
        'data': data
    }
    response = make_response(jsonify(response_data))
    response.headers['Content-Type'] = 'application/json'
    response.status_code = 200
    return response


def error(code=500, msg=''):
    response_data = {
        'message': msg
    }
    response = make_response(jsonify(response_data))
    response.headers['Content-Type'] = 'application/json'
    response.status_code = code
    return response


@app.route('/', methods=['GET'])
def holle():
    return datetime.now().strftime("%Y%m%d")


@app.route('/add/dpm', methods=['POST'])
def add_dpm():
    try:
        names = request.json
        if names is None or len(names) == 0:
            return error(400, "请填写数据")

        dups = check_duplicate_dpm(names)
        if len(dups) > 0:
            return error(409, json.dumps(dups) + "已经存在")

        add_departments(names)
        return ok()
    except Exception as e:
        log.error(e)
        return error(500, "服务器出错")


@app.route('/rm/dpm/<name>', methods=['POST'])
def rm_dpm(name):
    try:
        if is_name_null(name):
            return error(400, "请填写数据")

        # dups = check_duplicate_dpm(names)
        # if len(dups) == 0:
        #     return error(409, json.dumps(dups) + "不存在")

        del_department(name)
        return ok('[{}] 已删除'.format(name))
    except Exception as e:
        log.error(e)
        return error(500, "服务器出错")


@app.route('/list/dpm', methods=['GET'])
def list_dpm():
    try:
        return ok(data=get_department())
    except Exception as e:
        return error(500, "服务器出错")


def check_duplicate_dpm(names):
    dpms = get_department()
    return [name for name in names if name in dpms]


@app.route('/add/product', methods=['POST'])
def add_prod():
    try:
        p = request.json
        if p is None or is_name_null(p['name']) or p['price'] is None:
            return error(400, "请填写数据")

        for pp in get_product():
            if pp['name'] == p['name']:
                return error(409, "[{}] 已存在".format(p['name']))

        add_products([p])
        return ok()
    except Exception as e:
        log.error(e)
        return error(500, "服务器出错")


@app.route('/update/product', methods=['POST'])
def update_prod():
    try:
        p = request.json
        if p is None or is_name_null(p['name']) or p['price'] is None:
            return error(400, "请填写数据")
        update_product(p)
        return ok()
    except Exception as e:
        log.error(e)
        return error(500, "服务器出错")


@app.route('/rm/product/<name>', methods=['POST'])
def rm_prod(name):
    try:
        if is_name_null(name):
            return error(400, "请填写数据")
        del_product(name)
        return ok('[{}] 已删除'.format(name))
    except Exception as e:
        log.error(e)
        return error(500, "服务器出错")


@app.route('/list/product', methods=['GET'])
def list_pd():
    try:
        return ok(data=get_product())
    except Exception as e:
        return error(500, "服务器出错")


@app.route('/add/sale/<date>', methods=['POST'])
def add_sale(date):
    try:
        sales = request.json
        if date == '' or sales is None or len(sales) == 0:
            return error(400, "请填写数据")

        sales = [s for s in sales if s['num'] > 0]
        clear_sales(date, sales[0]['dpm'])
        add_sales(date, sales)
        return ok()
    except Exception as e:
        log.error(e)
        return error(500, "服务器出错")


@app.route('/rm/sale/<date>', methods=['POST'])
def rm_sale(date):
    try:
        dpms = request.json
        if date == '':
            return error(400, "请填写日期")

        if dpms is None or len(dpms) == 0:
            dpms = ['']
        for dpm in dpms:
            clear_sales(date, dpm)
        return ok()
    except Exception as e:
        log.error(e)
        return error(500, "服务器出错")


@app.route('/check/sale/<date>/<dpm>', methods=['GET'])
def check_sale(date, dpm):
    try:
        if date == '':
            return error(400, "请填写日期")

        data = generate_table(date, dpm)
        return ok(data=data)
    except Exception as e:
        log.error(e)
        return error(500, "服务器出错")


def generate_table(date, dpm=None):
    data = get_sales(date, dpm)
    rows = []
    if is_name_null(dpm):
        dpms, products = get_dpm_and_products_from_sales(data)
        price_count = 0
        row1 = [''] + [d for d in dpms] + ['数量', '价格', '总计']
        rows.append(row1)

        for p in products:
            row = [p]
            for i in range(1, len(row1) - 3):
                row.append(count_sale_with_dpm(p, row1[i], sales))
            row.append(products[p]['num'])
            row.append(products[p]['price'])
            pc = products[p]['num'] * products[p]['price']
            row.append(pc)
            price_count += pc
            rows.append(row)

        row_end = ['总计']
        for i in range(1, len(row1) - 3):
            row_end.append(dpms[row1[i]]['sales'])
        row_end.append('')
        row_end.append('')
        row_end.append(price_count)
        rows.append(row_end)

    else:
        row1 = ['app', '下载', '备注', '价格', '总计']
        rows.append(row1)
        count = 0
        price_count = 0
        for sale in data:
            price = sale['num'] * sale['price']
            row = [sale['name'], sale['num'], sale['comment'], sale['price'], price]
            rows.append(row)
            count += sale['num']
            price_count += price
        row_end = ['总计', count, '', '', price_count]
        rows.append(row_end)
    return rows


def count_sale_with_dpm(pname, dpm, sales):
    count = 0
    for s in sales:
        if s['name'] == pname and s['dpm'] == dpm:
            count += 1
    if count == 0:
        return ''
    return str(count)


def get_dpm_and_products_from_sales(sales):
    dpms = {}
    products = {}
    for s in sales:
        if dpms[s['dpm']] is None:
            dpms[s['dpm']] = {'sales': 1}
        else:
            dpms[s['dpm']]['sales'] += 1

        if products[s['name']] is None:
            products[s['name']] = {'price': s['price'], 'num': s['num']}
        else:
            products[s['name']]['num'] += s['num']
    return dpms, products


def get_department():
    table = TinyDB(dpm_db).table(dpm_table)
    return [item['name'] for item in table.all()]


def get_product():
    table = TinyDB(product_db).table(product_table)
    return table.all()


def add_departments(names):
    db = TinyDB(dpm_db)
    table = db.table(dpm_table)
    for name in names:
        table.insert({"name": name})
    db.close()


def add_products(products):
    db = TinyDB(product_db)
    table = db.table(product_table)
    for p in products:
        # table.insert({"name": p['name'], "price": p['price']})
        table.insert(p)
    db.close()


def del_department(name):
    db = TinyDB(dpm_db)
    table = db.table(dpm_table)
    Dpm = Query()
    table.remove(Dpm.name == name)
    db.close()


def del_product(name):
    db = TinyDB(product_db)
    table = db.table(product_table)
    Product = Query()
    table.remove(Product.name == name)
    db.close()


def update_product(p):
    db = TinyDB(product_db)
    table = db.table(product_table)
    Product = Query()
    table.update({"price": p['price']}, Product.name == p['name'])
    db.close()


def clear_sales(date, dpm=None):
    db = TinyDB(sale_db(date))
    table = db.table(sale_table)
    if is_name_null(dpm):
        table.truncate()
    else:
        Sale = Query()
        table.remove(Sale.dpm == dpm)
    db.close()


def add_sales(date, sales):
    db = TinyDB(sale_db(date))
    table = db.table(sale_table)
    table.insert_multiple(sales)
    db.close()


def get_sales(date, dpm=None):
    db = TinyDB(sale_db(date))
    table = db.table(sale_table)
    if is_name_null(dpm):
        data = table.all()
    else:
        Sale = Query()
        data = table.search(Sale.dpm == dpm)
    db.close()
    return data


def is_name_null(name):
    if name is None or name == '' or name == 'NA':
        return True
    return False


def sale_db(date):
    return '{}sale{}.json'.format(db_dir, date)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6060)
