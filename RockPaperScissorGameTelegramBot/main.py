import time
import json
import random
from saving import *
def json_read(path):
    with open(path, 'r') as f:
        data=json.load(f)
        return data

def write_json(path, new):
    with open(path, 'w') as f:
        json.dump(new, f, indent=4)


def players(name, game_mode):
    data=json_read('players.json')
    player={'id': len(data)+1, 'name':name, 'game_mode': [game_mode], 'score':0, 'nog':0, 'duration': []}
    for p in data:
        if p['name']==name:
            player=p
            p['game_mode'].append(game_mode)
            data.remove(p)
    write_json('players.json', data)
    return player

def vs_computer(p, options):
    user_choice = int(input('''
Enter your choice:
1.rock
2.paper
3.scissor '''))
    computer_choice = random.randint(1, 3)
    user_option = options[user_choice - 1]
    computer_option = options[computer_choice - 1]
    print(f'''{p['name']}: {user_option}
Computer: {computer_option}''')

    if computer_option == user_option:
        return 'Tie game'
    elif computer_option == 'rock':
        if user_option == 'paper':
            return f'{p['name']} won!'

        else:
            return 'Computer won'
    elif computer_option == 'paper':
        if user_option == 'scissor':
            return f'{p['name']} won!'
        else:
            return 'Computer won'
    elif computer_option == 'scissor':
        if user_option == 'rock':
            return f'{p['name']} won!'
        else:
            return 'Computer won'
    else:
        return 'Computer won'




def vs_user(p, opponent, options):
    player_1 = int(input(f'''
{p['name'].upper()}
Enter your choice:
1.rock
2.paper
3.scissor '''))
    player_2= int(input(f'''
{opponent['name'].upper()}
Enter your choice:
1.rock
2.paper
3.scissor '''))
    player1_option = options[player_1 - 1]
    player2_option = options[player_2 - 1]
    print(f'''{p['name']}: {player1_option}
{opponent['name']}: {player2_option}''')
    if player1_option == player2_option:
        return 'Tie game'
    elif player1_option=='':
        return f'{opponent['name']} won!'
    elif player2_option=='':
        return f'{p['name']} won!'
    elif player1_option == 'rock':
        if player2_option == 'paper':
            return f'{opponent['name']} won!'
        else:
            return f'{p['name']} won!'
    elif player1_option == 'paper':
        if player2_option == 'scissor':
            return f'{opponent['name']} won!'
        else:
            return f'{p['name']} won!'
    elif player1_option == 'scissor':
        if player2_option == 'rock':
            return f'{opponent['name']} won!'
        else:
            return f'{p['name']} won!'










def game(name, mode):
    p=players(name, mode)
    game_options=['rock', 'paper', 'scissor']
    print('Game started. Good Luck!')

    if mode=='computer':
        start_time = time.time()
        result=vs_computer(p, game_options)
        end = time.time()
        print(result)
        print(f'Duration: {round(end-start_time, 2)} seconds')
        if result==f'{p['name']} won!':
            p['score']+=5
        p['duration'].append(end-start_time)
        p['nog']+=1
        data=json_read('players.json')
        data.insert(p['id']-1, p)
        write_json('players.json', data)
        add_user(p['name'], p['score'], p['nog'], p['game_mode'], p['duration'])
    elif mode=='user':
        opponent_name = input('Opponent name: ')
        opponent=players(opponent_name, mode)
        start_time = time.time()
        result=vs_user(p, opponent, game_options)
        end = time.time()
        print(result)
        print(f'Duration: {round(end - start_time, 2)} seconds')
        if result == f'{p['name']} won!':
            p['score'] += 5
        elif result==f'{opponent['name']} won!':
            opponent['score']+=5
        p['duration'].append(end - start_time)
        p['nog'] += 1
        opponent['duration'].append(end - start_time)
        opponent['nog'] += 1
        data = json_read('players.json')
        data.insert(p['id'] - 1, p)
        data.insert(opponent['id'] - 1, opponent)
        write_json('players.json', data)
        add_user(p['name'], p['score'], p['nog'], p['game_mode'], p['duration'])
        add_user(opponent['name'], opponent['score'], opponent['nog'], opponent['game_mode'], opponent['duration'])
    else:
        print('Invalid option')


def main():
    name = input('Enter your name: ').strip()
    mode = input('''
Choose:
VS Computer
VS User: ''').strip().lower()
    no_games=int(input('How many games: '))
    while no_games:
        game(name, mode)
        no_games-=1
main()




