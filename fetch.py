import requests, re, copy, json, os, yaml, glob
from itertools import combinations
from bs4 import BeautifulSoup as bs


def parse_html(team_file, type, team):
    """
        # ateam = {}
        # ateam = parse_html('wick.html', 3, ateam)
        # ateam = parse_html('bat.html',  1, ateam)
        # ateam = parse_html('all.html',  4, ateam)
        # ateam = parse_html('ball.html', 2, ateam)
    """
    with open(team_file) as page:
        pg = ''.join(page.readlines())
    bsObj = bs(pg, features='html.parser')
    # print bsObj
    for div in bsObj.findAll('div', {'class': re.compile(r'^js--create-team__team')}):
        # print div
        name = str(div.findAll('div', {'class': re.compile(r'^playerName')})[0].string)
        points = div.findAll('div', {'class': re.compile(r'playerPointsCell')})
        fpoints = float(points[0].string)
        cpoints = float(points[1].string)
        status = div.findAll('div', {'class': re.compile(r'^statusText')})[0].string
        franchise = str(div.findAll('div', {'class': re.compile(r'^squadName')})[0].string)
        if status is not None:
            team[name] = [fpoints, cpoints, type, franchise]
    return team
    # print bsObj.findAll('div')


def dream_fantasy(tid, mid, players):
    dream_points = {}
    for pid in players:
        payload = {"query": "query PlayerProfileQuery( $id: Int = 1 $matchId: Int = 100 $tourId: Int = 10 $site: String = \"cricket\") { player(id: $id, matchId: $matchId, tourId: $tourId, site: $site) { artwork { src } tourStatistics { credits points selectionRate matchId matchName matchDate inDreamTeam creditChange } lineupStatus { status text color } creditChange credits points name type { name } squad { name } playerProfileDisplay profileUrl }}",
                   "variables": {"id": pid, "tourId": tid, "matchId": mid, "teamId": None, "site": "ipl-fantasy"}}
        headers = {'Referer': 'https://fantasy.iplt20.com/ipl-fantasy/create-team/' + str(tid) + '/' + str(mid),
                   'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36',
                   'X-CSRF': '37163426-19ac-7ee8-d222-d0c0cf13d1a9'}
        url = 'https://fantasy.iplt20.com/graphql/query/pwa/player-profile-query'
        r = requests.Session()
        page = r.post(url, json=payload, headers=headers).json()
        matches = page['data']['player']['tourStatistics']
        name = page['data']['player']['name']
        # print page
        for match in matches:
            # print match['matchId'], match['inDreamTeam'], match['points'], match['selectionRate']
            if match['matchId'] == mid:
                actual = match['points']
                dream_points[name] = actual
    return dream_points


def get_actual_points(tid, mid, force_update=False):

    fdir = 'data/dream/'
    if not os.path.isdir(fdir):
        os.makedirs(fdir)
    ff = fdir + str(mid-22442) + '.json'
    if force_update or not os.path.exists(ff):
        payload = {
            "query": "query FantasyScoreCard($site: String!, $tourId: Int!, $matchId: Int!) { site(slug: $site) { fantasyScoreCardHeader { name } tour(id: $tourId) { match(id: $matchId) { status squads { name shortName flag { src } } players(isPlaying: true) { name type { shortName } squad { shortName } pointBreakup { score name } } } } }}",
            "variables": {"tourId": tid, "matchId": mid, "site": "ipl-fantasy"}}
        headers = {'Referer': 'https://fantasy.iplt20.com/ipl-fantasy/fantasy-scorecard/' + str(tid) + '/' + str(mid),
                   'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36',
                   'X-CSRF': '37163426-19ac-7ee8-d222-d0c0cf13d1a9'}
        url = 'https://fantasy.iplt20.com/graphql/query/pwa/fantasy-score-card'
        r = requests.Session()
        page = r.post(url, json=payload, headers=headers).json()
        with open(ff, 'w') as f:
            yaml.safe_dump(page, f)
    else:
        with open(ff, 'r') as f:
            page = yaml.safe_load(f.read())

    status = page['data']['site']['tour']['match']['status']
    if status != 'COMPLETED':
        return []
    dream_team = {}
    players = page['data']['site']['tour']['match']['players']
    for player in players:
        name = player['name']
        total = player['pointBreakup'][0][-1]['score']
        dream_team[str(name)] = total
    # print "Actual points : {}".format(list(sorted(dream_team.items(), key=lambda a: a[1], reverse=True)))
    return dream_team


def player_details(tid, mid, pid, force_update=False):
    pdir = 'data/players/'
    if not os.path.isdir(pdir):
        os.makedirs(pdir)
    ff = pdir + str(pid) + '.json'
    if force_update or not os.path.exists(ff):
        payload = {
            "query": "query PlayerProfileQuery( $id: Int = 1 $matchId: Int = 100 $tourId: Int = 10 $site: String = \"cricket\") { player(id: $id, matchId: $matchId, tourId: $tourId, site: $site) { artwork { src } tourStatistics { credits points selectionRate matchId matchName matchDate inDreamTeam creditChange } lineupStatus { status text color } creditChange credits points name type { name } squad { name } playerProfileDisplay profileUrl }}",
            "variables": {"id": pid, "tourId": tid, "matchId": mid, "teamId": None, "site": "ipl-fantasy"}}
        headers = {'Referer': 'https://fantasy.iplt20.com/ipl-fantasy/create-team/' + str(tid) + '/' + str(mid),
                   'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36',
                   'X-CSRF': '37163426-19ac-7ee8-d222-d0c0cf13d1a9'}
        url = 'https://fantasy.iplt20.com/graphql/query/pwa/player-profile-query'
        r = requests.Session()
        page = r.post(url, json=payload, headers=headers).json()
        with open(ff, 'w') as f:
            yaml.safe_dump(page, f)
    else:
        with open(ff, 'r') as f:
            page = yaml.safe_load(f.read())

    matches = page['data']['player']['tourStatistics']
    # print page
    tot = []
    for match in matches:
        # print match
        # print match['matchId'], match['inDreamTeam'], match['points'], match['selectionRate']
        if match['points'] != 0 and match['matchId'] < mid:
            tot.append({match['matchId']: [float(match['points']), match['matchName'], match['matchDate']]})
    # print tot
    tot_points = [k.values()[0][0] for k in tot]
    # print tot_points
    return round(sum(tot_points)/len(tot_points) if sum(tot_points) != 0 else 0, 2)


def match_details(tid, mid, force_update=False):
    # print ("Fetching match details : " + str(mid))
    mdir = 'data/match/'
    if not os.path.isdir(mdir):
        os.makedirs(mdir)
    ff = mdir + str(mid-22442) + '.json'
    team = {}
    if force_update or not os.path.exists(ff):
        payload = {
            "query": "query ShmeCreateTeamQuery( $site: String! $tourId: Int! $teamId: Int = -1 $matchId: Int!) { site(slug: $site) { name showTeamCombination { count siteKey } teamPreviewArtwork { src } teamCriteria { totalCredits maxPlayerPerSquad totalPlayerCount } roles { id artwork { src } color name pointMultiplier shortName } playerTypes { id name minPerTeam maxPerTeam shortName artwork { src } } tour(id: $tourId) { match(id: $matchId) { id guru squads { flag { src } flagWithName { src } id jerseyColor name shortName } startTime status players(teamId: $teamId) { artwork { src } squad { id name jerseyColor shortName } credits id name points type { id maxPerTeam minPerTeam name shortName } lineupStatus { status text color } isSelected role { id artwork { src } color name pointMultiplier shortName } statistics { selectionRate role { id selectionRate } } } tour { id } } } showSelPercent } me { isGuestUser showOnboarding }}",
            "variables": {"tourId": tid, "matchId": mid, "teamId": None, "site": "ipl-fantasy"}}
        headers = {'Referer': 'https://fantasy.iplt20.com/ipl-fantasy/create-team/' + str(tid) + '/' + str(mid),
                   'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36',
                   'X-CSRF': '37163426-19ac-7ee8-d222-d0c0cf13d1a9'}
        url = 'https://fantasy.iplt20.com/graphql/query/pwa/shme-create-team-query'
        r = requests.Session()
        page = r.post(url, json=payload, headers=headers).json()
        with open(ff, 'w') as f:
            yaml.safe_dump(page, f)
    else:
        with open(ff, 'r') as f:
            page = yaml.safe_load(f.read())

    squads = page['data']['site']['tour']['match']['squads']
    status = page['data']['site']['tour']['match']['status']
    startTime = page['data']['site']['tour']['match']['startTime'][:16]
    # print "{} on {}".format(' vs '.join([i['shortName'] for i in squads]),str(startTime))
    players = page['data']['site']['tour']['match']['players']
    for player in players:
        # print player
        srate = player['statistics']['selectionRate']
        name = str(player['name'])
        # print name
        id = player['id']
        credits = player['credits']
        squad = str(player['squad']['name'])
        # print player['type']
        type = player['type']['id'] # 4 = ALL, 3 = WK, 2 = BOWL, 1 = BAT
        if player['lineupStatus'] is not None and player['lineupStatus']['status'] == 'PLAYING':
            fantasy_avg = player_details(tid, mid, id)
            team[name] = [fantasy_avg, credits, type, squad, srate, id]

    return team, {'squad': squad, 'status': status, 'startTime': startTime}


def team_combinations(team, squad, dream_team, avg_out, dream):
    if not dream:
        try:
            avg = round(sum([d[0] for d in team.values()]) / len(team), 2)
        except:
            return
        for k, v in team.items():
            if v[0] == 0.0 and avg_out:
                team[k][0] = avg
                # print avg
            # print k, v
    fteam = []
    filtered = 0
    # print dir(itertools.combinations(team.items(), 11))
    for i in [{j: team[j] for j in i} for i in combinations(team, 11)]:
        fp = cp = rate = 0
        # print i
        cat = {'wick': 0, 'bat': 0, 'bowl': 0, 'all': 0, squad: 0}
        for j, k in i.items():
            fp += k[0]
            cp += k[1]
            if k[2] == 3:
                cat['wick'] += 1
            elif k[2] == 1:
                cat['bat'] += 1
            elif k[2] == 4:
                cat['all'] += 1
            else:
                cat['bowl'] += 1
            if k[3] in cat:
                cat[k[3]] += 1
            else:
                cat[k[3]] = 1
            rate += k[4]

        if cp <= 100 and \
                1 <= cat['wick'] <= 4 and \
                1 <= cat['all'] <= 4 and \
                3 <= cat['bat'] <= 6 and \
                3 <= cat['bowl'] <= 6 and \
                4 <= cat[squad] <= 7:
            fteam.append([i, round(fp, 2), cp, cat, round(rate, 2)])
        else:
            filtered += 1
    # if not dream:
    #     print "Valid Teams : {} || Invalid Teams : {}".format(str(len(fteam)),str(filtered))

    fteam.sort(key=lambda team: team[1], reverse=True)
    if dream:
        print "Dream Team : {}".format(fteam[0])
        return fteam[0]
    team_id = 0
    if len(dream_team) > 0:
        for i in fteam:
            team_id += 1
            count = len([1 for v in i[0].values() if v[-1] in dream_team])
            # if count >= 10:
            #     print team_id, count, i[1:], sorted([{x:y[0]} for x, y in i[0].items()], key=lambda e: e.values(), reverse=True)
            if count == 11:
                print "Predicted Team : {} : {}".format(team_id, [{k: v[0]} for k, v in i[0].items()])
                break
    else:
        for i in fteam[:50]:
            team_id += 1
            # print team_id, i[1:], sorted(i[0].items(), key=lambda e: e[1][0], reverse=True)
            print team_id, i[1:], [a[0] for a in sorted(i[0].items(), key=lambda e: e[1][0], reverse=True)]
    # print dream_team


dream_players = {
    22469: [1343, 9161, 646, 1143, 1886, 9483, 1436, 1519, 1979, 1193, 639],
    22470: [12843, 899,  8793, 9000, 813, 8872, 342, 1091, 1257, 11533, 6867],
    22471: [1517, 298, 36, 736, 2104, 988, 6332, 9164, 974, 10185, 109]
}


def match_det(fixture, mid):
    match_yaml = fixture['Data']['Value'][mid-1]
    match_number = match_yaml['MatchNumber'].split(' ')[1]
    match_date = match_yaml['MatchdateTime'].split(' ')[0]
    match_time = match_yaml['MatchdateTime'].split(' ')[1]
    venue = match_yaml['Venue1'].split(',')[1].strip()
    home_teamcc = match_yaml['HomeTeamCountryCode']
    home_team = match_yaml['HomeTeamName']
    away_teamcc = match_yaml['AwayTeamCountryCode']
    away_team = match_yaml['AwayTeamName']
    result = match_yaml['MatchResult']
    try:
        winning_team = re.findall(r".+(?= beat)", result)[0]
    except:
        winning_team = re.findall(r"(?<=\().+(?= win)", result)[0]
    winning_teamcc = home_teamcc if winning_team == home_team else away_teamcc
    losing_teamcc = home_teamcc if winning_team != home_team else away_teamcc
    tally = re.findall(r"(?<=by ).+", result)[0]
    match_data = [match_number, match_date, match_time, venue, home_teamcc,
                  away_teamcc, winning_teamcc, losing_teamcc, tally]
    match_str = "|".join([str(x) for x in match_data])
    print match_str
    return match_str, home_teamcc, home_team, away_teamcc


def e2e(matchId, fixture):
    match_str, home_teamcc, home_team, away_teamcc = match_det(fixture, matchId)
    matchId += 22442
    tourId = 1552
    est_team22, details = match_details(tourId, matchId)

    if details['status'] == 'COMPLETED':
        act_team = copy.deepcopy(est_team22)

        act_team22 = get_actual_points(tourId, matchId)

        for k in act_team.keys():
            act_team[k][0] = act_team22[k]
        print act_team
        datadir = 'dataset/'
        if not os.path.isdir(datadir):
            os.makedirs(datadir)
        for player, pdata in act_team.items():
            with open(datadir + str(pdata[5]) + '_' + re.sub('\W+', '', player) + '.csv', 'a+') as f:
                pdata[3] = home_teamcc if pdata[3] == home_team else away_teamcc
                f.write(match_str + '|' + "|".join([str(x) for x in pdata[:5]]) + '\n')

        # dream_team = team_combinations(act_team, details['squad'], [], False, True)
        # dream_players = [v[-1] for v in dream_team[0].values()]
    else:
        print details['status']  # NOT_STARTED
        # dream_players = []

    # team_combinations(est_team22, details['squad'], dream_players, False, False)


def get_fixtures(force_update=False):
    if not os.path.isdir('data'):
        os.makedirs('data', exist_ok=True)
    ff = 'data/fixtures.json'
    if force_update or not os.path.exists(ff):
        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Content-Type': 'application/json;charset=utf-8',
            'entity': 'd3tR0!t5m@sh',
            'Referer': 'https://fantasy.iplt20.com/season/league',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 ' +
                          '(KHTML, like Gecko) Chrome/86.0.4240.80 Safari/537.36'
        }
        page = requests.get('https://fantasy.iplt20.com/season/services/feed/fixtures',
                         headers=headers).json()
        with open(ff, 'w') as f:
            yaml.safe_dump(page, f)
    else:
        with open(ff, 'r') as f:
            page = yaml.safe_load(f.read())
    return page


def update_headers():
    # Update Files
    for files in glob.glob('dataset/*csv'):
        with open(files, 'w') as f:
            f.write('MatchNo|Date|Time|Venue|HomeTeam|AwayTeam|'
                    'Winingteam|LosingTeam|Tally|Points|Credits|Type|Team|SelectionRate\n')


fixtures = get_fixtures(force_update=True)
# e2e(51, fixtures)

for match_no in range(1, 51):
    e2e(match_no, fixtures)

from pandas import read_csv
from pandas import set_option
from matplotlib import pyplot

path = r"dataset/1_MSDhoni.csv"

data = read_csv(path, delimiter='|', index_col=0)
set_option('precision', 2)
print(data.head())
print(data.describe())

data.hist()
pyplot.show()