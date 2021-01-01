'''server/app.py - main api app declaration'''
import threading
import schedule
# from datetime import datetime
from zipfile import ZipFile, BadZipFile
from flask import Flask, jsonify, send_from_directory, request, abort, session
from flask_cors import CORS
from pymongo import MongoClient
from bson.objectid import ObjectId
from passlib.hash import sha512_crypt
from leaderboard import Leaderboard
from email_bot import EmailBot
from tournament import TournamentController
from code_generator import CodeGenerator
from teams import TeamController
from global_state import GlobalController
import code_generator
import traceback
import uuid
import docker
import time
import shutil
import os
# import re


'''
Application Run Flags
'''
PROD_FLAG = False

'''Main wrapper for app creation'''
app = Flask(__name__, static_folder='../build')
app.config["MONGO_URI"] = "mongodb+srv://utmrobotics:1d3erhunted3089@deerhunt.ntpnz.mongodb.net/<dbname>?retryWrites=true&w=majority"
client = MongoClient(app.config["MONGO_URI"])
PROD_FLAG = False
if PROD_FLAG:
    # app.run(host='0.0.0.0', port=80, threaded=True, ssl_context=(
    #     '/etc/letsencrypt/live/mcss.utmrobotics.com/fullchain.pem', '/etc/letsencrypt/live/mcss.utmrobotics.com/privkey.pem'))
    database = client.deerhunt_prod
else:
    # app.run(host='0.0.0.0', port=8080, threaded=True)
    database = client.deerhunt_db
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

# tournament_timer = threading.Thread(target=TournamentController.start_scheduler, args=(client, database, 3))
# t1 = TournamentController(client, database)
# t1.daemon = True
# t1.start()
# test = ['jasmine', 'kyrel', 'peter', 'jarvis', 'jack', 'raze', 'bufflin', 'dell', 'edmund', 'sova',
#         'jasmine2', 'kyrel2', 'peter2', 'jarvis2', 'jack2', 'raze2', 'bufflin2', 'dell2', 'edmund2', 'sova2',
#         'jasmine3', 'kyrel3', 'peter3', 'jarvis3', 'jack3', 'raze3', 'bufflin3', 'dell3', 'edmund3', 'sova3',
#         'jasmine4', 'kyrel4', 'peter4', 'jarvis4', 'jack4', 'raze4', 'bufflin4', 'dell4', 'edmund4']
        # 'jasmine5', 'kyrel5', 'peter5', 'jarvis5', 'jack5', 'raze5', 'bufflin5', 'dell5', 'edmund5', 'sova5',
        # 'jasmine6', 'kyrel6', 'peter6', 'jarvis6', 'jack6', 'raze6', 'bufflin6', 'dell6', 'edmund6', 'sova6',
        # 'jasmine7', 'kyrel7', 'peter7', 'jarvis7', 'jack7', 'raze7', 'bufflin7', 'dell7', 'edmund7', 'sova7',
        # 'jasmine8', 'kyrel8', 'peter8', 'jarvis8', 'jack8', 'raze8', 'bufflin8', 'dell8', 'edmund8', 'sova8']

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

    if session['username'] in submitting:
        shutil.rmtree(submitting[session['username']])
    user_file = database.users.find_one({"username": session["username"]})
    team_name = user_file['team']
    team_file = database.teams.find_one({"name": team_name})
    if "last_submit" in team_file:
        # NEED TO CHECK IF 5 MINUTES HAVE PASSED.
        
        
    submit_folder = f'{user_file["team"]}'
    submit_path = f'{submissions_folder}/{submit_folder}'
    
    request.files['upload'].save(f'{submit_path}.zip')
    try:
        with ZipFile(f'{submit_path}.zip', 'r') as z:
            z.extractall(submit_path)
    except BadZipFile:
        abort(400)
    os.remove(f'{submit_path}.zip')
    # NEED TO UPLOAD TO STORAGE HERE.
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



# Teams
# Teams assigning api calls


@app.route('/api/sendinvite', methods=['POST'])
def send_invite():
    '''Sends an invite from a user's current team to a user.'''
    login_guard()
    username = session["username"]
    if not request.is_json:
        abort(400)
    body = request.get_json()
    if not "recipient" in body:
        abort(400)
    recipient_doc = database.users.find_one({'username': body["recipient"]})
    if not recipient_doc:
        abort(400)
    with TeamController(client, database) as team_api:
        status = team_api.send_invite(username, body["recipient"])
    if not status:
        abort(409)
    return "Success"


@app.route('/api/userinvites', methods=['GET'])
def user_invites():
    """Gets the list of team display names and team names that a user 
        has been invited to.
    """
    login_guard()
    with TeamController(client, database) as team_api:
        invites_team_dict = team_api.get_user_invites(session["username"])
    return invites_team_dict

# Teams assigning api calls


@app.route('/api/acceptinvite', methods=['POST'])
def accept_invite():
    '''Accpets an invite on a user's account, if the invite is valid.'''
    login_guard()
    username = session["username"]

    body = request.get_json()
    if not "team" in body:
        abort(400)

    with TeamController(client, database) as team_api:
        status = team_api.accept_invite(username, body["team"])
    if not status:
        abort(409)

    return "Success"


@app.route('/api/createteam', methods=['POST'])
def create_team():
    login_guard()
    if not request.is_json:
        abort(400)
    body = request.get_json()
    if not "team" in body:
        abort(400)

    with TeamController(client, database) as team_api:
        status = team_api.create_team(session["username"], body["team"])
    if not status:
        print("Request failed with error code:" + str(team_api.error))
        abort(409)
    return "Success"


@app.route('/api/leaveteam', methods=['POST'])
def leave_team():
    login_guard()
    with TeamController(client, database) as team_api:
        status = team_api.leave_team(session["username"])
    if not status:
        print("Request failed with error code:" + str(team_api.error))
        abort(409)
    return "Success"


@app.route('/api/getteam', methods=['GET'])
def get_team():
    login_guard()

    with TeamController(client, database) as team_api:
        team = team_api.get_user_team(session["username"])
    if not team:
        return {}
    team_json = {
        "name": team.get("name", ""),
        "display_name": team.get("displayName", ""),
        "invites":  team.get("invites", []),
        "users": team.get("users", [])
    }
    return team_json


@app.route('/api/getteaminvites', methods=['GET'])
def get_team_invites():
    login_guard()
    with TeamController(client, database) as team_api:
        team = team_api.get_user_team(session["username"])
    if not team:
        return {"invited_users": []}
    return {"invited_users": team.get("invites", [])}

# Login and Registstration Routes


@app.route('/api/challenge', methods=['POST'])
def challenge():
    login_guard()
    challenger = session['username']
    defender = request.get_json()
    print(defender)
    with TournamentController(client, database, challenger) as battle:
        can_battle = battle.init_challenge(defender)
        if can_battle:
            result = battle.run_battle()
        

@app.route('/api/login', methods=['POST'])
def login():
    u, p = safe_get_user_and_pass()
    result = database.users.find_one({'username': u})
    if result is None or 'password' not in result:
        abort(403)

    if not sha512_crypt.verify(p, result['password']):
        abort(403)
    if result['verified'] != True:
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


@app.route('/api/register', methods=['POST'])
def register():
    u, p = safe_get_user_and_pass()
    u = u.lower()
    u = u.strip(" ")
    result = database.users.find_one({'username': u})
    if result is not None:
        abort(409)

    if not is_allowed(u):
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

# Admin access and Status


@app.route('/api/isadmin', methods=['GET', 'POST'])
def isadmin():
    return str(is_admin_check())

@app.route('/api/initglobalstate', methods=['POST'])
def initglobalstate():
    admin_guard()
    with GlobalController(client, database) as globals_api:
        if not globals_api.init_state():
            abort(400)
    return str(True)

@app.route('/api/leaderboardtoggle', methods=['GET', 'POST'])
def leaderboardtoggle():
    if request.method == 'GET':
        with GlobalController(client, database) as globals_api:
            if not globals_api.get_leaderboard_state():
                abort(400)
        return str(globals_api.ret_val)
    admin_guard()

    with GlobalController(client, database) as globals_api:
        if not globals_api.leaderboard_toggle():
            abort(400)
    return str(globals_api.ret_val)


@app.route('/api/submittoggle', methods=['GET', 'POST'])
def submittoggle():
    if request.method == 'GET':
        with GlobalController(client, database) as globals_api:
            if not globals_api.get_submit_state():
                abort(400)
        return str(globals_api.ret_val)
    admin_guard()

    with GlobalController(client, database) as globals_api:
        if not globals_api.submit_toggle():
            abort(400)
    return str(globals_api.ret_val)


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
        app.run(host='0.0.0.0', port=8080, threaded=True, debug=True)
        # database = MongoClient(
        #     "mongodb+srv://utmrobotics:1d3erhunted3089@deerhunt.ntpnz.mongodb.net/<dbname>?retryWrites=true&w=majority").deerhunt_db
        # database = mongo.init_app(app)
        # database = database.deerhunt_db
        # print(database)
    # board = Leaderboard(database.leaderboard)