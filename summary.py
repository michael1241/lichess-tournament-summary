#!/usr/bin/env python3

import click
import urllib.request
import os
import json
import datetime

@click.command()
@click.option('--code',  prompt='Lichess tournament code')
def getData(code, data=None):
    url = f"https://lichess.org/api/tournament/{code}/games"
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:64.0) Gecko/20100101 Firefox/64.0', 'Accept': 'application/x-ndjson'}
    req = urllib.request.Request(url, data, headers)
    try:
        response = urllib.request.urlopen(req)
        games = response.read().decode('utf-8').split("\n")
        with open('temp', 'w') as file:
            output = {}
            for game in games:
                try:
                    game = json.loads(game)
                except json.decoder.JSONDecodeError:
                    continue
                if output == {}:
                    output['tournamentid'] = code
                    output['date'] = str(datetime.datetime.fromtimestamp(game['createdAt']//1000).date())
                    output['speed'] = game['speed']
                    output['control'] = f"{game['clock']['initial']//60}+{game['clock']['increment']}"
                    output['games'] = {}
                output['games'][game['id']] = {'white':game['players']['white']['user']['id'], 'black':game['players']['black']['user']['id'], 'url':f"https://lichess.org/{game['id']}"}
                try:
                    if game['winner']:
                        output['games'][game['id']]['result'] = "1-0" if game['winner'] == 'white' else "0-1"
                except KeyError:
                    output['games'][game['id']]['result'] = "1/2-1/2"
                stamp = ""
                if not stamp:
                    stamp = f"Lichess_{output['control']}_{output['date']}_{code}.json"
            file.write(json.dumps(output))
        os.rename('temp', stamp)
    except urllib.error.URLError as e:
        if hasattr(e, 'reason'):
            print('Request failed.', file=sys.stderr)
            print('Reason: ', e.reason, file=sys.stderr)
        if hasattr(e, 'code'):
            print('Error code: ', e.code, file=sys.stderr)
            sys.exit(1)
        else:
            raise

getData()
