import requests
from bs4 import BeautifulSoup
from time import sleep


#import tkinter as tk
#
# def click(value):
#     entry.insert(tk.END, value)
#
# def clear():
#     entry.delete(0, tk.END)
#
# def calculate():
#     try:
#         result = eval(entry.get())
# #         clear()
# #         entry.insert(0, str(result))
# #     except:
# #         clear()
# #         entry.insert(0, "Ошибка")
#
# root = tk.Tk()
# root.title("Калькулятор")
# root.geometry("300x400")
# root.resizable(False, False)
#
# entry = tk.Entry(root, font=("Arial", 20), justify="right")
# entry.grid(row=0, column=0, columnspan=4, padx=10, pady=10)
#
# buttons = [
#     "7", "8", "9", "/",
#     "4", "5", "6", "*",
#     "1", "2", "3", "-",
#     "0", ".", "=", "+"
# ]
#
# row = 1
# col = 0
#
# for btn in buttons:
#     if btn == "=":
#         tk.Button(root, text=btn, font=("Arial", 18),
#                   command=calculate).grid(row=row, column=col, sticky="nsew")
#     else:
#         tk.Button(root, text=btn, font=("Arial", 18),
#                   command=lambda b=btn: click(b)).grid(row=row, column=col, sticky="nsew")
#
#     col += 1
#     if col > 3:
#         col = 0
#         row += 1
#
# tk.Button(root, text="C", font=("Arial", 18),
#           command=clear).grid(row=row, column=0, columnspan=4, sticky="nsew")
#
# for i in range(4):
#     root.columnconfigure(i, weight=1)
# for i in range(row + 1):
#     root.rowconfigure(i, weight=1)
#
# root.mainloop()


import requests
from bs4 import BeautifulSoup
from time import sleep

headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36'}

def get_url():
    for count in range(1, 51):
        url = f'https://books.toscrape.com/catalogue/page-{count}.html'
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'lxml')
        data = soup.find_all('li', class_='col-xs-6 col-sm-4 col-md-3 col-lg-3')
        for i in data:
            card_url = 'https://books.toscrape.com/catalogue/' + i.find('a').get('href')
            yield card_url

for card_url in get_url():
    response = requests.get(card_url, headers=headers)
    sleep(3)
    soup = BeautifulSoup(response.text, 'lxml')
    data = soup.find('div', class_='content')
    name = data.find('h1').text
    price = data.find('p', class_='price_color').text
    text = data.find('p', class_=None).text
    card_img = 'https://books.toscrape.com/catalogue/' + data.find('img').get('src')
    print(name + '\n' + price + '\n' + text + '\n' + card_img + '\n\n')