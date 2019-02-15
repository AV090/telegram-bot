import requests
from telegram import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup

_domain = "https://cricapi.com/api/"

_cricket_api_key = "gWR4ToyufWReDZVkVG0fA6wpzbt1"

_player_id = "35320"

_cric_ops = {
    'search': 'https://cricapi.com/api/playerFinder?apikey=' + _cricket_api_key + '&name=',
    'records': 'https://cricapi.com/api/playerStats?apikey=' + _cricket_api_key + '&pid=',
    'schedules': 'https://cricapi.com/api/matchCalendar?apikey=' + _cricket_api_key,
    'newmatch': "https://cricapi.com/api/matches?apikey=" + _cricket_api_key,
    'match': "https://cricapi.com/api/cricketScore?apikey=" + _cricket_api_key + "&unique_id="
}

labels_dict = {"tests": "Tests", }


def fetch(ops, args=""):
    print(ops, args)
    if ops in _cric_ops:
        action = _cric_ops[ops]
        print(action)
        data = requests.get(action + args).json()

        if ops == 'search':
            data = data.get('data', None)
            return search(data)
        elif ops == 'newmatch':
            print("data => ", data)
            return newmatch(data)
    return None


def search(data):
    if data is not None and len(data) > 1:
        player_list = data

        buttons_menu = []

        for _button in range(0, len(player_list), 2):
            buttons = [InlineKeyboardButton(text=item["fullName"], callback_data="records " + str(item['pid']))
                       for item in
                       player_list[_button:_button + 2]]

            buttons_menu.append(buttons)
        di = dict(text="<b>Please select which player you are looking for</b>", parse_mode='HTML',
                  reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons_menu))
        return di
    elif data is not None and len(data) == 1:
        player = data[0]
        msg = "<em>We found below player</em>"
        keyboard_menu = [
            [InlineKeyboardButton(text=player["fullName"], callback_data="records " + str(player['pid']))]]

        di = dict(text=msg, parse_mode='HTML',
                  reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard_menu))
        return di
    return dict(
        text="<em style='font-color:red;font-size:23'>We cannot find any player. Please modify your search</em>",
        parse_mode='HTML')


def newmatch(data):
    if data is not None:
        matches = data.get('matches', None)
        if matches is not None:
            matches = matches[:10]
            inline_keyboard = []
            win_team = ""
            not_started = ""
            for item in matches:

                if item['matchStarted']:
                    winner_team = item.get('winner_team', None)
                    if winner_team is not None:
                        win_team += "<b>" + item['type'] + " Match: </b>  " + item['team-1'] + " vs " + item[
                            'team-2'] + " \n<i>Won By: </i>" + item['winner_team'] + "\n"
                    else:
                        btn = [InlineKeyboardButton(
                            text="Live - " + item['type'] + " : " + item['team-1'] + " vs " + item['team-2'],
                            callback_data="match " + str(item['unique_id']))]
                        inline_keyboard.append(btn)
                else:
                    not_started += "<b>" + item['type'] + " Match: </b>" + item['team-1'] + " vs " + item[
                        'team-2'] + "\n"

            return [dict(text=win_team, parse_mode='HTML'), dict(text="Live Matches", parse_mode='HTML',
                                                                 reply_markup=InlineKeyboardMarkup(
                                                                     inline_keyboard=inline_keyboard)),
                    dict(text=not_started, parse_mode='HTML')]

    return dict(
        text="<em style='font-color:red;font-size:23'>We cannot find matches.</em>",
        parse_mode='HTML')


def callback_handler_records(pid):
    print("pid is => ", pid)
    try:

        data = requests.get(_cric_ops.get('records') + pid).json()

        if data is not None:
            img = data.get('imageURL', "")
            msg = "<b>Country:" + data['country'] + "</b>" + "\n" + "<i>" + data['profile'] + "</i><b>Teams-> </b>" + \
                  data['majorTeams'] + "\n<b>Stats</b>\n"
            data = data.get('data', None)
            batting = data.get('batting', None)
            if batting is not None:
                msg += "<i>Batting</i>\n" + batting_bowling_data(batting)
            bowling = data.get('bowling', None)
            if bowling is not None:
                msg += "<i>Bowling</i>\n" + batting_bowling_data(bowling)

            msg += "\nProfile Pic:\n" + "<a href='" + img + "'>&nbsp;</a>"

            print(msg, " = msg")
            return dict(text=msg, parse_mode='HTML')
        else:
            raise Exception()
    except Exception as ex:
        print('Exception=> ', ex)
        return dict(text="Cannot process your request now")


def callback_handler_match(match_id):
    print("Match id is =>", match_id)

    try:
        if match_id:
            data = requests.get(_cric_ops['match'] + match_id).json()
            print(data)
            _score = data.get('score',"No Data")
            return dict(text=_score, parse_mode='HTML')
        return dict(text="No details of this match found :(")
    except Exception as ex:
        print('Exceptions is => ', ex)
        return dict(text="Cannot process request now")


def batting_bowling_data(data={}):
    if data != {}:
        p_matches = ('T20Is', 'ODIs', 'tests')
        li = [item for item in data.keys() if item in p_matches]

        if len(li) == 0:
            if 'firstClass' in data:
                li.append('firstClass')
            if 'listA' in data:
                li.append('listA')
        return append_carrer_data(li, data)
    return ""


def append_carrer_data(li=[], di={}):
    if len(li) > 0 and di != {}:
        data = ""
        for item in li:
            data += "<b>" + item + ":</b>\n" + format_dict_str(di[item]) + "\n"
        return data
    return ""


def format_dict_str(di):
    di_str = str(di)
    di_str = di_str.replace("}", "")
    di_str = di_str.replace("{", "")
    temp = ""
    di_str = di_str.split(",")
    for item in range(0, len(di_str), 4):
        temp += " ".join(di_str[item:item + 4]) + "\n"
    return temp