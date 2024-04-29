import os

from flask import Flask, render_template, redirect, request
import requests

app = Flask(__name__)

current_user = ''
current_bitcoin_buy = '0'
current_bitcoin_in_wallet = '0'
current_eth_buy = '0'
current_eth_in_wallet = '0'
current_ltc_buy = '0'
current_ltc_in_wallet = '0'

contents = os.listdir("users")

users = {}
for i in contents:
    users[i] = {}
    for j in os.listdir(f'users/{i}'):
        with open(f'users/{i}/{j}') as f:
            f = f.readline()
            users[i][j] = f

message_to_log = 'None'
message_to_reg = 'None'


@app.route('/', methods=['GET', 'POST'])
@app.route('/main_page', methods=['GET', 'POST'])
def main():
    return render_template('main_page.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    global message_to_log

    return render_template('login.html', message=message_to_log)


@app.route('/register', methods=['GET', 'POST'])
def register():
    global message_to_reg

    return render_template('register.html', message=message_to_reg)


@app.route('/register_user', methods=['GET', 'POST'])
def register_user():
    global message_to_reg, message_to_log

    user = request.form['user']
    password = request.form['password']

    if user not in users:
        os.mkdir(f'users/{user}')
        hp = f'users/{user}'

        with open(os.path.join(hp, f'password.txt'), 'w') as f:
            f.write(password)

        for i in ['bit', 'eth', 'ltc']:
            fp = os.path.join(hp, i)

            with open(fp, 'w') as f:
                f.write('0 0')

    else:
        message_to_reg = 'already registered'
        return redirect('register')

    message_to_log = 'success'
    return redirect('login')


@app.route('/check_user', methods=['GET', 'POST'])
def check_user():
    global message_to_log, current_user, current_bitcoin_in_wallet, current_eth_in_wallet, current_ltc_in_wallet
    global current_bitcoin_buy, current_eth_buy, current_ltc_buy

    username_on_check = request.form['uc']
    password_on_check = request.form['pc']

    if username_on_check in users:
        current_user = username_on_check

        if users[username_on_check]['password.txt'] == password_on_check:
            with open(f'users/{current_user}/bit', 'r') as f:
                current_bitcoin_in_wallet = int(f.readline().split()[1])
                current_bitcoin_buy = users[current_user]['bit'].split()[0]

            with open(f'users/{current_user}/eth', 'r') as f:
                current_eth_in_wallet = int(f.readline().split()[1])
                current_eth_buy = users[current_user]['eth'].split()[0]

            with open(f'users/{current_user}/ltc', 'r') as f:
                current_ltc_in_wallet = float(f.readline().split()[1])
                current_ltc_buy = users[current_user]['ltc'].split()[0]

            return redirect('trading_page')

        else:
            message_to_log = "Wrong password"
            return redirect('login')

    message_to_log = 'Did not registered'
    return redirect('login')


@app.route('/trading_page', methods=['GET', 'POST'])
def trading_page():
    global current_eth_in_wallet, current_eth_buy, current_bitcoin_buy, current_bitcoin_in_wallet, current_ltc_buy
    global current_ltc_in_wallet

    url = 'https://api.binance.com/api/v1/ticker/24hr'

    params1 = {'symbol': 'BTCUSDT'}
    params2 = {'symbol': 'ETHUSDT'}
    params3 = {'symbol': 'LTCUSDT'}

    response1 = requests.get(url, params=params1)
    response2 = requests.get(url, params=params2)
    response3 = requests.get(url, params=params3)

    data1 = response1.json()['lastPrice'][0:7]
    data2 = response2.json()['lastPrice'][0:7]
    data3 = response3.json()['lastPrice'][0:7]

    profit = str((float(data1) - float(current_bitcoin_buy)) * int(current_bitcoin_in_wallet))[0:6]
    profit_eth = str((float(data2) - float(current_eth_buy)) * int(current_eth_in_wallet))[0:6]
    profit_ltc = str((float(data3) - float(current_ltc_buy)) * int(current_ltc_in_wallet))[0:6]

    return render_template('trade_page.html', q1=data1, q2=data2, q3=data3, bp=current_bitcoin_buy, ep=current_eth_buy,
                           lp=current_eth_buy, wallet_bit=current_bitcoin_in_wallet, wallet_eth=current_eth_in_wallet,
                           wallet_ltc=current_ltc_in_wallet, profit_bit=profit, profit_eth=profit_eth,
                           profit_ltc=profit_ltc)


@app.route('/trade_bitcoin', methods=['GET', 'POST'])
def but_bitcoin():
    global current_user, current_bitcoin_buy, current_bitcoin_in_wallet

    plus = request.form['buy_bitcoin']
    minus = request.form['sell_bitcoin']

    itog = int(plus) + -int(minus)

    url = f'https://api.binance.com/api/v1/ticker/24hr'
    params1 = {'symbol': 'BTCUSDT'}
    response1 = requests.get(url, params=params1)

    current_bitcoin_buy = response1.json()['lastPrice'][0:7]

    with open(f'users/{current_user}/bit', 'r') as f:
        it = int(f.readline().split()[1])

    with open(f'users/{current_user}/bit', 'w') as f:
        f.write('')
        f.write(f'{response1.json()["lastPrice"][0:7]} {itog + it}')
        current_bitcoin_in_wallet = it + itog

    return redirect('trading_page')


@app.route('/trade_ethe', methods=['POST', 'GET'])
def trade_ethe():
    global current_user, current_eth_buy, current_eth_in_wallet

    plus = request.form['buy_ethe']
    minus = request.form['sell_ethe']
    itog = int(plus) + -int(minus)

    url = 'https://api.binance.com/api/v1/ticker/24hr'

    params1 = {'symbol': 'ETHUSDT'}
    response1 = requests.get(url, params=params1)
    current_eth_buy = response1.json()['lastPrice'][0:7]

    with open(f'users/{current_user}/eth', 'r') as f:
        it = int(f.readline().split()[1])

    with open(f'users/{current_user}/eth', 'w') as f:
        f.write('')
        f.write(f'{response1.json()['lastPrice'][0:7]} {itog + it}')
        current_eth_in_wallet = str(it + itog)

    return redirect('trading_page')


@app.route('/trade_litcoin', methods=['POST', 'GET'])
def trade_litcoin():
    global current_user, current_ltc_buy, current_ltc_in_wallet

    plus = request.form['buy_litcoin']
    minus = request.form['sell_litcoin']
    itog = int(plus) + -int(minus)

    url = 'https://api.binance.com/api/v1/ticker/24hr'

    params1 = {'symbol': 'LTCUSDT'}
    response1 = requests.get(url, params=params1)
    current_ltc_buy = response1.json()['lastPrice'][0:7]

    with open(f'users/{current_user}/ltc', 'r') as f:
        it = int(f.readline().split()[1])

    with open(f'users/{current_user}/ltc', 'w') as f:
        f.write('')
        f.write(f'{response1.json()['lastPrice'][0:7]} {itog + it}')
        current_ltc_in_wallet = it + itog

    return redirect('trading_page')


@app.route('/profile', methods=['POST', 'GET'])
def profile():
    global current_user, current_bitcoin_in_wallet, current_eth_in_wallet, current_ltc_in_wallet

    return render_template('profile.html', username=current_user, wallet_bit=current_bitcoin_in_wallet,
                           wallet_eth=current_eth_in_wallet, wallet_lit=current_ltc_in_wallet)


@app.route('/exit_from_account', methods=['POST', 'GET'])
def exit_from_account():
    global current_user

    current_user = 'None'
    return redirect('login')


@app.route('/about', methods=['POST', 'GET'])
def about():
    return render_template('about.html')


if __name__ == '__main__':
    app.run(debug=True)
