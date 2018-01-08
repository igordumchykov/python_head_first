from flask import Flask, render_template, request, escape, session
from functions import find_vowels
from DBcm import UseDatabase, ConnectionErr
from checker import check_logged_in

app = Flask(__name__)

app.config['dbconfig'] = {'host': '127.0.0.1', 'user': 'root',
                          'password': 'admin', 'database': 'vsearchlogDB', }

app.secret_key = 'some_secret_key'


@app.route('/')
def hello() -> str:
    return 'Hello world from Flask!'


@app.route('/login')
def do_login() -> str:
    session['logged_in'] = True
    return 'You are logged in'


@app.route('/status')
def check_status() -> str:
    if 'logged_in' in session:
        return 'You are currently logged in.'
    return 'You are NOT logged in.'


@app.route('/logout')
def do_logout() -> str:
    session.pop('logged_in')
    return 'You are logged out'


# without decorator
# def check_logged_in() -> bool:
#     if'logged_in' in session:
#         return True
#     return False


@app.route('/search4', methods=['POST'])
def functions() -> str:
    phrase = request.form['phrase']
    letters = request.form['letters']
    results = str(find_vowels(phrase))
    log_request(request, results)
    log_dir_request(request, results)
    log_filter_request(request, results)
    log_db_request(request, results)
    return render_template(
        'results.html',
        the_phrase=phrase,
        the_letters=letters,
        the_title='Here are results: ',
        the_results=results)


@app.route('/entry')
@check_logged_in
def entry_page() -> 'html':
    return render_template('entry.html', the_title='Welcome!')


@app.route('/viewrowlog')
def view_row_log() -> str:
    with open('vsearchlog.log') as log:
        contents = log.read()
    return contents


@app.route('/viewescapelog')
def view_escape_log() -> str:
    with open('vsearchlog.log') as log:
        contents = log.read()
    return escape(contents)


@app.route('/viewfilterlog')
def view_filter_log() -> str:
    contents = []
    with open('vsearchfilterlog.log') as log:
        for line in log:
            contents.append([])
            for item in line.split('|'):
                contents[-1].append(escape(item))
    titles = ('Form Data', 'Remote_addr', 'User_agent', 'Results')
    return render_template('viewlog.html', the_title='View Log',
                           the_row_titles=titles, the_data=contents, )


@app.route('/viewdirlog')
def view_dir_log() -> str:
    with open('vsearchdirlog.log') as log:
        contents = log.read()
    return escape(contents)


@app.route('/viewdblog')
def view_db_log() -> 'html':
    try:
        with UseDatabase(app.config['dbconfig']) as cursor:
            _SQL = """select phrase, letters, ip, browser_string, results from log"""
            cursor.execute(_SQL)
            contents = cursor.fetchall()
        titles = ['Phrase', 'Letters', 'Remote_addr', 'User_agent', 'Results']
        return render_template('viewlog.html', the_title='View Log',
                               the_row_titles=titles, the_data=contents, )
    except ConnectionErr as err:
        print("Exception occurred: ", str(err))


def log_request(req: 'flask_request', res: str) -> None:
    with open('vsearchlog.log', 'a') as log:
        print(req, res, file=log)


def log_filter_request(req: 'flask_request', res: str) -> None:
    with open('vsearchfilterlog.log', 'a') as log:
        print(req.form, res, file=log, end='|')
        print(req.remote_addr, res, file=log, end='|')
        print(req.user_agent, res, file=log, end='|')
        print(res, file=log)


def log_dir_request(req: 'flask_request', res: str) -> None:
    with open('vsearchdirlog.log', 'a') as log:
        print(str(dir(req)), res, file=log)


def log_db_request(req: 'flask_request', res: str) -> None:
    try:
        with UseDatabase(app.config['dbconfig']) as cursor:
            _SQL = """ insert into log
                        (phrase, letters, ip, browser_string, results) values
                        (%s, %s, %s, %s, %s)"""
            cursor.execute(_SQL, (req.form['phrase'], req.form['letters'],
                                  req.remote_addr, req.user_agent.browser, res,))
    except Exception as err:
        print("Exception occurred: ", str(err))


if __name__ == '__main__':
    app.run(debug=True)
