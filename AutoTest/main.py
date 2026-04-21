import random
import json
from PIL import Image
from saving import *

def json_read(path):
    with open(path, encoding='utf-8') as f:
        data=json.load(f)
        return data

def user_checker(surname, name):
    line=None
    data=json_read('users.json')
    for l in data:
        if l['surname']==surname and l['name']==name:
            line=l
    return line



def user(new_user, content):
    right = 0
    wrong = 0
    skip = 0
    incorrect = []
    random.shuffle(content)
    for i in range(int(new_user['number_of_questions'])):


        if content[i]['id'] not in new_user['questions_history']:
            new_user['questions_history'].append(content[i]['id'])
            question(content[i], new_user['language'])
            user_answer=input("Enter number of the option you chose: ")
            if user_answer:
                u_answer=answer(user_answer, content[i], new_user['language'])
                print(u_answer)
                if u_answer in ['Правильно', 'Тугри', "To'g'ri"]:
                    new_user['points']+=1
                    new_user['right_answers']+=1
                    right+=1
                elif u_answer in ['Неправильно', 'Нотугри', "Noto'g'ri"]:
                    incorrect.append(content[i]['question'])
                    new_user['points']-=0.25
                    wrong+=1
                else:
                    skip+=1
            else:
                continue
    percent=round((100*right)/new_user['number_of_questions'], 2)
    new_user['percent']=percent
    if percent>60:
        new_user['status']="Pass"
    else:
        new_user['status']="Fail"
    return {"user":new_user, "right": right, "wrong": wrong, "skip": skip, "incorrect": incorrect}

def existing_user(user, content, no_q):
    right = 0
    wrong = 0
    skip = 0
    incorrect = []
    random.shuffle(content)
    for i in range(no_q):
        if content[i]['id'] not in user['questions_history']:
            user['questions_history'].append(content[i]['id'])
            question(content[i], user['language'])
            user_answer = input("Enter number of the option you chose: ")
            if user_answer:
                u_answer = answer(user_answer, content[i], user['language'])
                print(u_answer)
                if u_answer in ['Правильно', 'Тугри', "To'g'ri"]:
                    user["points"]+=1
                    user['right_answers'] += 1
                    right+=1
                elif  u_answer in ['Неправильно', 'Нотугри', "Noto'g'ri"]:
                    incorrect.append(content[i]['question'])
                    user['points'] -= 0.25
                    wrong+=1
                else:
                    skip+=1
            else:
                continue
    percent = round((100 * user['right_answers']) / user['number_of_questions'], 2)
    user['number_of_questions']+=no_q
    user['percent']=percent
    if percent > 60:
        user['status'] = "Pass"
    else:
        user['status'] = "Fail"
    return {"user": user, "right": right, "wrong": wrong, "skip": skip, "incorrect": incorrect}




def question(data, l):
    if data['media']['exist']:
        image_name = data['media']['name']
        img = Image.open(f"Autotest/{image_name}.png")
        img.show()
    print(f'Q {data["id"]}: {data["question"]}')
    if l=="кирилл" or l=="рус":
        for index, option in enumerate(data["choises"], 1):
            print(f"{index}: {option["text"]}")
    else:
        for index, option in enumerate(data["choices"], 1):
            print(f"{index}: {option["text"]}")

def answer(user_answer, data, l):
    found_correct_answer=None
    try:
        answer=int(user_answer)

        if l=='рус':
            if data["choises"][answer - 1]["answer"]:
                found_correct_answer='Правильно'
            else:
                found_correct_answer = 'Неправильно'
        elif l=='кирилл':
            if data["choises"][answer - 1]["answer"]:
                found_correct_answer='Тугри'
            else:
                found_correct_answer = 'Нотугри'
        elif l=='lotin':
            if data["choices"][answer - 1]["answer"]:
                found_correct_answer="To'g'ri"
            else:
                found_correct_answer = "Noto'g'ri"
    except ValueError:
        print("Has to be number")
    return found_correct_answer

def main():
    global questions_no, username, name, surname, content
    users = []
    data=json_read('users.json')
    for d in data:
        users.append(d)
    new_user={"user_id": 0, "language": '', "surname": '', "name": '', "username": '',
          "number_of_questions": 0, "questions_history": [], "points": 0, "right_answers": 0,
          "status": "Failed", "percent": 0}

    print("""Привет! Добро пожаловать в Авто тест бот 
Salom! Auto test botiga xush kelibsiz
Салом! Авто тест ботига хуш келибсиз""")

    language = input('''Какой язык вы предпочитаете?
Qaysi til sizga ma'qul?
Кайси тил сизга ма'кул?
(рус, кирилл, lotin): ''').strip().lower()
    if language=='кирилл':
        surname=input('Илтимос, фамилиянгизни киритинг: ').strip().lower()
        name=input('Илтимос, исмингизни киритинг: ').strip().lower()
        username=input('Илтимос, никнеймингизни киритинг: ').strip().lower()
        while True:
            no_questions=input('Нечта саволга жавоб беришни хохлайсиз? (ракам киритинг): ')
            try:
                questions_no=int(no_questions)
                break
            except ValueError:
                print('Ракам киритинг')
        content = json_read("Autotest/uzkiril.json")
    elif language=='рус':
        surname = input('Пожалуйста, введите вашу фамилию: ').strip().lower()
        name = input('Пожалуйста, введите вашу имю: ').strip().lower()
        username = input('Пожалуйста, введите вашу никнейм: ').strip().lower()
        while True:
            no_questions = input('Сколько вопросов вы хотите решить? (введите число): ')
            try:
                questions_no = int(no_questions)
                break
            except ValueError:
                print('Ошибка! Пожалуйста, введите число')
        content = json_read("Autotest/rus.json")
    elif language=='lotin':
        surname = input('Iltimos, familyangizni kiriting: ').strip().lower()
        name = input('Iltimos, ismingizni kiriting: ').strip().lower()
        username = input('Iltimos, nikneymingizni kiriting: ').strip().lower()
        while True:
            no_questions = input('Nechta savolga javob berishni xohlaysiz? (raqam kiriting): ')
            try:
                questions_no = int(no_questions)
                break
            except ValueError:
                print('Raqam kiriting')
        content = json_read("Autotest/uzlotin.json")
    else:
        print('''Неверный
                 Noto'g'ri
                 Нотугри''')
    id = len(users) + 1
    if user_checker(surname, name):
        l=user_checker(surname, name)

        index=users.index(l)
        users.pop(index)
        edited=existing_user(l, content, questions_no)
        users.insert(index, edited['user'])
        modify_user(edited['user']['user_id'], edited['user']['language'], edited['user']['surname'], edited['user']['name'], edited['user']['username'], edited['user']['number_of_questions'], edited['user']['points'], edited['user']['right_answers'], edited['user']['questions_history'], edited['user']['status'], edited['user']['percent'])
        print(f"Number of right answers: {edited['right']}")
        print(f"Number of wrong answers: {edited['wrong']}")
        print(f"Number of skipped questions: {edited['skip']}")
        print()
        if len(edited['incorrect']) > 0:
            print("Wrong answered questions: ")
            for i in edited['incorrect']:
                print(i)
    else:
        new_user['user_id']=id
        new_user['language']=language
        new_user['surname']=surname
        new_user['name']=name
        new_user['username']=username
        new_user['number_of_questions']=questions_no
        new=user(new_user, content)
        users.append(new['user'])
        print(new)
        add_user(id, language, surname, name, username, questions_no, new['user']['points'], new['user']['right_answers'], new['user']['questions_history'], new['user']['status'], new["user"]['percent'])
        print(f"Number of right answers: {new['right']}")
        print(f"Number of wrong answers: {new['wrong']}")
        print(f"Number of skipped questions: {new['skip']}")
        print()
        if len(new['incorrect'])>0:
            print("Wrong answered questions: ")
            for i in new['incorrect']:
                print(i)

    with open('users.json', 'w') as f:
        json_ready_list = [u.__dict__ if hasattr(u, '__dict__') else u for u in users]
        json.dump(json_ready_list, f, indent=4)

main()
