import json
from datetime import date

from unicodedata import category


def json_read(path):
    with open(path, 'r') as f:
        data=json.load(f)
        return data

def write_json(path, new):
    with open(path, 'w') as f:
        json.dump(new, f, indent=4)


def view_products(path):
    data=json_read(path)
    for i in data['products']:
        print(f'{i['name']:<15} {i['price']:<10} {i['stock']:<10} {i['category']:<10}')

def add_to_cart(product):
    data = json_read('store_data.json')
    cart = json_read('../assignment 3/cart.json')

    product = product.lower()
    found_in_store = False
    found_in_cart = False

    for item in data:
        if item['name'].lower() == product:
            found_in_store = True

            for c in cart:
                if c['name'].lower() == product:
                    c['quantity'] += 1
                    found_in_cart = True
                    break

            if not found_in_cart:
                cart.append({
                    'name': product,
                    'price': item['price'],
                    'quantity': 1
                })

            print("Product added to cart.")
            break

    if not found_in_store:
        print("Product not found.")

    with open('../assignment 3/cart.json', 'w') as f:
        json.dump(cart, f, indent=4)

# add_to_cart('headphones')
def see_cart(username, password):
    data = json_read('../assignment 3/users.json')
    print(f"{'Product':<15} {'Price':<10} {'Quantity':<10}")
    for i in data:
        if i['username']==username and i['password']==password:
            for j in i['cart']:
                print(f"{j['product']:<15} {j['price']:<10} {j['quantity']:<10}")

def remove(username, password):
    data = json_read('../assignment 3/cart.json')
    choice = int(input('''What do you want?
                    1: Clear cart;
                    2: Remove product one by one;
                    3: Remove all one kind of product at once;  '''))
    for i in data:
        if i['username']==username and i['password']==password:
                    if choice==2:
                        product = input('Enter product name: ')
                        for j in i['cart']:
                            if j['product'].lower()==product.lower():
                                j['quantity']-=1
                                j['total_price']-=j['total_product']
                                break
                    elif choice==3:
                        product = input('Enter product name: ')
                        for j in i['cart']:
                            if j['product'].lower()==product.lower():
                                data.remove(j)
                    elif choice==1:
                        i['cart'].clear()
                    else:
                        print('Invalid choice')
                    with open('../assignment 3/cart.json', 'w') as f:
                        json.dump(data, f, indent=4)
# remove(1,'Headphones')



def sign_up(username, password, is_admin=False):
    data=json_read('../assignment 3/users.json')
    id=len(data)+1
    d_info={'id': id, 'username': username, 'password': password, 'is_admin':is_admin, 'cart': {}, 'purchase': {}}
    for i in data:
        if username == i["username"] and password == i["password"]:
            print('User already exists')
            break
    else:
        data.append(d_info)
        with open('../assignment 3/users.json', 'w') as file:
            json.dump(data, file, indent=4)


def login(username, password):
    data=json_read('../assignment 3/users.json')
    for i in data:
        if i['username']==username and i['password']==password:
            print(f'Welcome back {username}!')
            break
    else:
        print('No user found')

def edit_product(id, new_product, price, stock, category):
    data=json_read('store_data.json')
    for i in data:
        if i['id']==id:
            i['name']=new_product
            i['price']=price
            i['stock']=stock
            i['category']=category
            break
    else:
        print('No item found')

    write_json('store_data.json', data)
def remove_product(name):
    data=json_read('store_data.json')
    for i in data:
        if i['name'].lower()==name.lower():
            data.remove(i)
            break
    else:
        print('Product not found')
    write_json('store_data.json', data)

def add_product():
    data=json_read('store_data.json')
    id=len(data)+1
    name=input('Enter the product name: ')
    price=float(input('Enter the price: '))
    stock=int(input('Stock: '))
    category=input('Which category: ')
    info={'id': id, 'name': name, 'price': price, 'stock': stock, 'category': category}
    data.append(info)
    write_json('store_data.json', data)


def see_all_products():
    data=json_read('store_data.json')
    print(f'{'id':<5}  {'name':<10} {'price':<10} {'stock':<10} {'category':<10}')
    for i in data:
        print(f'{i['id']:<5}  {i['name']:<10} {i['price']:<10} {i['stock']:<10} {i['category']:<10}')
def see_all_users():
    data=json_read('../assignment 3/users.json')
    print(f'{'id':<5} {'username':<10} {'password':<10} {'is_admin':<10}')
    for i in data:
        print(f'{i['id']:<5} {i['username']:<10} {i['password']:<10} {i['is_admin']:<10}')

def set_user_admin():
    id=int(input('Enter id: '))

    data=json_read('store_data.json')
    for i in data:
        if i['id']==id:
            i['is_admin']=True
            break
    else:
        print('No user found')

    write_json('store_data.json', data)
def remove_user():
    data=json_read('../assignment 3/users.json')
    name=input('Enter name: ')
    for i in data:
        if i['username'].lower()==name.lower():
            data.remove(i)
            break
    else:
        print('User not found')
    write_json('../assignment 3/users.json', data)

def add_user():
    data=json_read('../assignment 3/users.json')
    id=len(data)+1
    username=input('Enter username: ')
    password=input('Enter the password: ')
    is_admin=input('Is admin?: ').strip().lower()
    if is_admin=='true':
        is_admin=True
        data1=json_read('../assignment 3/admins.json')
        info = {'id': id, 'username': username, 'password': password, 'is_admin': is_admin}
        data1.append(info)
        write_json('../assignment 3/admins.json', data1)
    else:
        is_admin=False
    info={'id': id, 'username': username, 'password': password, 'is_admin':is_admin}
    data.append(info)
    write_json('../assignment 3/users.json', data)
# add_user()
def see_all_admins():
    data=json_read('../assignment 3/admins.json')
    print(f'{'id':<5} {'username':<10} {'password':<10} {'is_admin':<10}')
    for i in data:
        print(f'{i['id']:<5} {i['username']:<10} {i['password']:<10} {i['is_admin']:<10}')

def user_edit(choice):
    if choice==1:
        see_all_users()
    elif choice==2:
        set_user_admin()
    elif choice==3:
        add_user()
    elif choice==4:
        remove_user()
    else:
        print('Invalid choice')

def product_edit(choice):
    if choice==1:
        see_all_products()
    elif choice==2:
        id=int(input('Enter product id you want to change: '))
        new_product=input('Enter new product name: ')
        price=float(input('Enter the price of the product: '))
        stock=int(input('Stock:  '))
        category=input("Category of product: ")
        edit_product(id, new_product, price, stock, category)
    elif choice==3:
        add_product()
    elif choice==4:
        name=input('Enter the name of product you want to delete: ')
        remove_product(name)
    else:
        print('Invalid choice')




def admin_login(username, password):
    data=json_read('../assignment 3/admins.json')
    for i in data:
        if i['username']==username and i['password']==password:
            while True:
                choose=int(input('''Enter your choice: 
                1: user edit
                2: product edit
                3: see all admins: 
                4: quit
                '''))
                if choose==1:
                    print('''Users
                    1: see all users
                    2: set admin
                    3: add user
                    4: remove user
                    ''')
                    choice = int(input('Enter choice: '))
                    user_edit(choice)
                elif choose==2:
                    print('''Users
                    1: see all products
                    2: edit product
                    3: add product
                    4: remove product
                    ''')
                    choice = int(input('Enter choice: '))
                    product_edit(choice)
                elif choose==3:
                    see_all_admins()
                elif choose==4:
                    print("Program terminated")
                    break
                else:
                    print("invalid choice")
        else:
            print('Invalid password or username')

def user_main(username, password, choose):

    if choose=='sign up':
        sign_up(username, password)
    elif choose=="login":
        login(username, password)
    else:
        print('invalid choise')

    print('Welcome!!!')

    while True:
        choice=int(input('''What do you want to do?
    1: see all products,
    2: add product to cart,
    3: see cart, 
    4: remove product from cart,
    5: purchase history: 
    6: quit
    '''))
        if choice==1:
            see_all_products()
        elif choice==2:
            product=input("Enter the product name you want to add cart: ")
            add_to_cart(product)
        elif choice==3:
            see_cart(username, password)
        elif choice==4:
            remove(username, password)

        elif choice==6:
            break
        else:
            print("invalid choice")

def main():
    while True:
        who=input("Are you a user or an admin or quit: ").strip().lower()

        if who=='admin':
            username = input("Enter your username: ")
            password = input("Enter password: ")
            admin_login(username, password)
        elif who=='user':
            choose = input("If you have an account login, if not sign up: ").strip().lower()
            username = input("Enter your username: ")
            password = input("Enter password: ")
            user_main(username, password, choose)
        elif who=='quit':
            break
        else:
            print("Invalid choice")
main()


















