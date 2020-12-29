'''server/app.py - main api app declaration'''
import os
import uuid
import time
# import sched
import threading
import shutil
import schedule
# import docker
# import re
# import traceback
# from datetime import datetime
from zipfile import ZipFile, BadZipFile
from flask import Flask, jsonify, send_from_directory, request, abort, session
from flask_cors import CORS
from pymongo import MongoClient
# from flask_pymongo import PyMongo
# from db import database
from bson.objectid import ObjectId
from passlib.hash import sha512_crypt
from leaderboard import Leaderboard
from email_bot import EmailBot
from tournament import TournamentLevel

'''Main wrapper for app creation'''
app = Flask(__name__, static_folder='../build')
app.config["MONGO_URI"] = "mongodb+srv://utmrobotics:1d3erhunted3089@deerhunt.ntpnz.mongodb.net/<dbname>?retryWrites=true&w=majority"
database = MongoClient(app.config["MONGO_URI"])
if PROD_FLAG:
    # app.run(host='0.0.0.0', port=80, threaded=True, ssl_context=(
    #     '/etc/letsencrypt/live/mcss.utmrobotics.com/fullchain.pem', '/etc/letsencrypt/live/mcss.utmrobotics.com/privkey.pem'))
    database = database.deerhunt_prod
else:
    # app.run(host='0.0.0.0', port=8080, threaded=True)
    database = database.deerhunt_db
board = Leaderboard(database.leaderboard)
app.secret_key = b'a*\xfac\xd4\x940 m\xcf[\x90\x7f*P\xac\xcdk{\x9e3)e\xd7q\xd1n/>\xec\xec\xe0'
CORS(app)

# database = None
# dock = docker.from_env()

allowed_emails = ["@mail.utoronto.ca"]
codeGenerator = CodeGenerator(64)
verification_domain = 'https://mcss.utmrobotics.com'


prefix = '/deerhunt'
submissions_folder = f'{prefix}/submissions'
build_folder = f'{prefix}/build'
template_folder = f'{prefix}/template'
server_folder = f'{prefix}/server'

should_display_leaderboards = True
can_submit = True
submitting = {} # dict looks like: {'some team name': }


# Starting second thread for tournament timer.

def job(arr):
    tourny = TournamentLevel(arr)
    x = tourny.run()
    print(x)
# def run_threaded(job_func):
#     job_thread = threading.Thread(target=job_func)
#     job_thread.start()
# def runTournamentThread():
#     schedule.every(1).second.do(run_threaded, job)
#     while 1:
#         schedule.run_pending()
#         time.sleep(1)
# tournament_timer = threading.Thread(target=runTournamentThread)
# tournament_timer.start()
# test = {'alex2': '/deerhunt/submissions/alex2', 'kyrel': '/deerhunt/submissions/kyrel'}
test = ['jasmine', 'kyrel', 'peter', 'jarvis', 'jack', 'raze', 'bufflin', 'dell', 'edmund', 'sova',
        'jasmine2', 'kyrel2', 'peter2', 'jarvis2', 'jack2', 'raze2', 'bufflin2', 'dell2', 'edmund2', 'sova2',
        'jasmine3', 'kyrel3', 'peter3', 'jarvis3', 'jack3', 'raze3', 'bufflin3', 'dell3', 'edmund3', 'sova3',
        'jasmine4', 'kyrel4', 'peter4', 'jarvis4', 'jack4', 'raze4', 'bufflin4', 'dell4', 'edmund4']
        # 'jasmine5', 'kyrel5', 'peter5', 'jarvis5', 'jack5', 'raze5', 'bufflin5', 'dell5', 'edmund5', 'sova5',
        # 'jasmine6', 'kyrel6', 'peter6', 'jarvis6', 'jack6', 'raze6', 'bufflin6', 'dell6', 'edmund6', 'sova6',
        # 'jasmine7', 'kyrel7', 'peter7', 'jarvis7', 'jack7', 'raze7', 'bufflin7', 'dell7', 'edmund7', 'sova7',
        # 'jasmine8', 'kyrel8', 'peter8', 'jarvis8', 'jack8', 'raze8', 'bufflin8', 'dell8', 'edmund8', 'sova8']
job(test)
##
# API routes
##

# TODO: SYNCUPDATE: Complete Reconfiguration of function before prod use.


@app.route('/api/submit', methods=['POST'])
def submit():
    '''
    Instanstly saves a team's submission to /deerhunt/submissions/someTeamname/
    Also removes zip after extracting.
    '''
    print(submitting)
    login_guard()
    if not can_submit:
        abort(403)
    if 'upload' not in request.files:
        abort(400)

    saveSubmission()

    return "Zip submitted! Thanks"

    # try:
    #     position = int(request.form['position']) - 1
    # except Exception:
    #     abort(400)

    # if position < 0 or position > 9:
    #     abort(400)

    # try:
    #     result = run_match(position)
    # except Exception as e:
    #     database.errors.insert_one({'message': str(e), 'trace': traceback.format_exc(),'time': datetime.utcnow()})

    #     if board.is_locked(position):
    #         board.release(position)

    #     abort(500)
    # finally:
    #     submitting[session['username']] = False


'''
def saveSubmission():
    if session['username'] in submitting:
        shutil.rmtree(submitting[session['username']])
    submit_folder = f'{session["username"]}-{time.time()}'
    submit_path = f'{submissions_folder}/{submit_folder}'
    request.files['upload'].save(f'{submit_path}.zip')
    submitting[session['username']] = submit_path
    try:
        with ZipFile(f'{submit_path}.zip', 'r') as z:
            z.extractall(submit_path)
    except BadZipFile:
        abort(400)
    os.remove(f'{submit_path}.zip')



def run_match(position):
    leader = board.acquire(position)
    leader_path = f'{submissions_folder}/{leader}'

    if leader is None:
        board.replace(position, submit_folder)
        board.save('default')
        return 'Victory by default'

    uid = uuid.uuid4().hex
    build_path = f'{build_folder}/{uid}'

    shutil.copytree(template_folder, f'{build_path}/')
    copy_dir_contents(leader_path, f'{build_path}/p1')
    copy_dir_contents(submit_path, f'{build_path}/p2')
    shutil.copytree(server_folder, f'{build_path}/server')

    img = dock.images.build(path=build_path, tag=uid, rm=True, network_mode=None)
    container = dock.containers.run(uid, detach=True, auto_remove=True, network_mode=None,
                                    cpu_count=1, mem_limit='512m')

    lines = []
    maps = []
    errors = []

    for line in container.logs(stream=True):
        l = line.decode().strip()
        if 'ERROR:' == l[0:6]:
            errors.append(l[6:])
        elif 'MAP:' == l[0:4]:
            maps.append(l[4:])
        else:
            lines.append(l)

    lines = lines[3:]

    if 'Winner: p2' == lines[-1]:
        board.replace(position, submit_folder)
        board.save(uid)

    board.release(position)

    game_id = database.logs.insert_one({'lines': lines,
                                        'maps': maps,
                                        'errors': errors,
                                        'build_id': uid,
                                        'defender': leader,
                                        'challenger': submit_folder,
                                        'submitter': session['username']}).inserted_id

    return jsonify(game_id=str(game_id), message=lines[-1])
'''




@app.route('/api/login', methods=['POST'])
def login():
    u, p = safe_get_user_and_pass()
    result = database.users.find_one({'username': u})
    if result is None or 'password' not in result:
        abort(403)

    if not sha512_crypt.verify(p, result['password']):
        abort(403)
    if result['verified'] == 'False':
        abort(403)

    session['logged_in'] = True
    session['username'] = u
    # submitting[session['username']] = False
    submitting[session['username']] = ''

    return 'Login successful'

# TODO: SYNCUPDATE-Extra work: Proper Variable naming.


@app.route('/api/changepassword', methods=['GET', 'POST'])
def changePassword():
    login_guard()

    cup, nep, cop = safe_get_passwords()
    result = database.users.find_one({'username': session['username']})
    if result is None:
        abort(403)
    if not sha512_crypt.verify(cup, result['password']):
        abort(403)
    if nep != cop:
        abort(400)
    query = {'username': session['username']}
    newvalues = {'$set': {'password': sha512_crypt.encrypt(nep)}}

    database.users.update_one(query, newvalues)

    return 'Change successful'


@app.route('/verify/<code>')
def verify_email(code: str):
    result = database.users.find_one({'code': code})
    if result is None:
        return "Invalid Verification Link."
    reg_time = datetime.strptime(result['time'], '%Y-%m-%d %H:%M:%S.%f')
    curr_time = datetime.now()
    time_delta = curr_time-reg_time
    if time_delta.seconds > 60*30:
        database.users.delete_one({"code": code})
        return "Verification link has expired, Please recreate the account."
    query = {'code': code}
    newvalues = {'$set': {'verified': 'True'}}
    database.users.update_one(query, newvalues)
    return "Account has been verified successfully"


# TODO: SYNCUPDATE: Complete Reconfiguration of function before prod use. Update using upsert
@app.route('/api/register', methods=['POST'])
def register():
    u, p = safe_get_user_and_pass()
    u = u.lower()
    u = u.strip(" ")
    result = database.users.find_one({'username': u})
    if result is not None:
        abort(409)

    if not is_allowed(u):
        print("invalid email")
        abort(409)

    code = codeGenerator.generate()
    query = {'username': u}
    data = {'username': u,
            'password': sha512_crypt.encrypt(p),
            'code': code, 'time': str(datetime.now()),
            'verified': 'False'}
    writeResult = database.users.update_one(
        query,
        {"$setOnInsert": data},
        upsert=True)
    if not writeResult.upserted_id:
        abort(409)
    msg = '\n\nYour account has been successfully created. Please click the link below to verify your account.\n\n{0}\n\nTechnical Team\nUTM Robotics'.format(
        verification_domain+"/verify/"+code)
    email_status = EmailBot.sendmail(u, "Account Verification", msg)
    if not email_status:
        print("Could not send email")
        database.errors.insert_one({"error": "Email could not send, error ",
                                    'time': datetime.utcnow()
                                    })
        return abort(400)
    return 'Register successful'


''' Safe For Upsert!!!
'''


@app.route('/api/getmatch', methods=['GET', 'POST'])
def getmatch():
    login_guard()

    if not request.is_json:
        abort(400)

    body = request.get_json()

    if 'game_id' not in body:
        abort(400)

    result = database.logs.find_one({'_id': ObjectId(body['game_id'])})

    if result is None:
        abort(400)

    return jsonify(result['maps'])


''' TODO: LEADERBOARD - DISREGARD UNTIL TEAMS COMPLETION
'''


@app.route('/api/leaderboard', methods=['GET', 'POST'])
def leaderboard():
    login_guard()

    if not should_display_leaderboards:
        abort(403)

    lst = []
    for i in range(len(board.board)):
        lst.append({
            'name': board.board[i].split('-')[0],
            'queue': board.queue_count[i]
        })

    return jsonify(lst)


@app.route('/api/isloggedin', methods=['GET', 'POST'])
def isloggedin():
    return str(logged_in())


@app.route('/api/isadmin', methods=['GET', 'POST'])
def isadmin():
    return str(is_admin_check())


'''
 TODO: LEADERBOARD - Use db-based check, check if required at all?
'''


@app.route('/api/leaderboardtoggle', methods=['GET', 'POST'])
def leaderboardtoggle():
    global should_display_leaderboards

    if request.method == 'GET':
        return str(should_display_leaderboards)

    admin_guard()

    should_display_leaderboards = not should_display_leaderboards
    return str(should_display_leaderboards)


''' TODO: LEADERBOARD - Use db-based check, currently not ephemeral-safe.
'''


@app.route('/api/submittoggle', methods=['GET', 'POST'])
def submittoggle():
    global can_submit
    if request.method == 'GET':
        return str(can_submit)

    admin_guard()

    can_submit = not can_submit
    return str(can_submit)


''' TODO: LEADERBOARD - Use db-based check, Submission system will be reconfigured.
'''


@app.route('/api/resetlockout', methods=['GET', 'POST'])
def resetlockout():
    admin_guard()

    if not request.is_json:
        abort(400)

    body = request.get_json()

    if 'username' not in body:
        abort(400)

    if body['username'] in submitting:
        submitting[body['username']] = False

    return 'Success'

##
# View route
##


@app.route('/tutorial')
def tutorial():
    #pylint: disable=unused-argument
    return send_from_directory(app.static_folder, 'tutorial.html')


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def index(path):
    '''Return index.html for all non-api routes'''
    #pylint: disable=unused-argument
    return send_from_directory(app.static_folder, 'index.html')

##
# Helpers
##


def safe_get_user_and_pass():
    if not request.is_json:
        abort(400)

    body = request.get_json()

    return body['username'], body['password']


def safe_get_passwords():
    if not request.is_json:
        abort(400)

    body = request.get_json()

    return body['currentPassword'], body['newPassword'], body['confirmPassword']


def login_guard():
    if 'logged_in' not in session or not session['logged_in']:
        abort(403)


def logged_in():
    return session['logged_in'] if 'logged_in' in session else False


def admin_guard():
    if not is_admin_check():
        abort(403)


def is_admin_check():
    if not logged_in():
        return False

    result = database.users.find_one({'username': session['username']})
    if result is None:
        return False

    if 'admin' not in result or not result['admin']:
        return False
    return True


def is_allowed(email: str) -> bool:
    for allowed_email in allowed_emails:
        if email.endswith(allowed_email):
            return True
    return False


def copy_dir_contents(src, dest):
    for file in os.listdir(src):
        shutil.copy(f'{src}/{file}', dest)


if __name__ == '__main__':
    if PROD_FLAG:
        app.run(host='0.0.0.0', port=80, threaded=True, ssl_context=(
            '/etc/letsencrypt/live/mcss.utmrobotics.com/fullchain.pem', '/etc/letsencrypt/live/mcss.utmrobotics.com/privkey.pem'))
        # database = MongoClient(
        #     "mongodb+srv://utmrobotics:1d3erhunted3089@deerhunt.ntpnz.mongodb.net/<dbname>?retryWrites=true&w=majority").deerhunt_prod
        # database = PyMongo(app)
    else:
<<<<<<< HEAD
        app.run(host='0.0.0.0',port=8080, threaded=True)
=======
        app.run(host='0.0.0.0', port=8080, threaded=True)
        # database = MongoClient(
        #     "mongodb+srv://utmrobotics:1d3erhunted3089@deerhunt.ntpnz.mongodb.net/<dbname>?retryWrites=true&w=majority").deerhunt_db
        # database = mongo.init_app(app)      
        # database = database.deerhunt_db
        # print(database)
    # board = Leaderboard(database.leaderboard)
>>>>>>> dev
