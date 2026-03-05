import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import random

#Логирование
def log_action(message):
    with open('log.txt', 'a', encoding='utf-8') as f:
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        f.write(f'{now} — {message}\n')

#Настройки отображения
pd.set_option('display.width', 200)
pd.set_option('display.max_columns', None)

#Справочники
room_type_list   = ['Стандарт', 'Люкс', 'Полулюкс', 'Семейный']
hotel_list       = ['Marriott', 'Hilton', 'Hyatt', 'Radisson', 'Azimut']
guest_name_list  = ['Иванов', 'Петров', 'Сидоров', 'Козлов', 'Новиков',
                    'Морозов', 'Волков', 'Лебедев', 'Соколов', 'Орлов']

#Генерация данных
n = 10
log_action("Запуск программы. Начальное количество броней — " + str(n))

np.random.seed(42)

booking_id   = np.arange(1001, 1001 + n)
hotels       = np.random.choice(hotel_list, size=n)
room_types   = np.random.choice(room_type_list, size=n)
room_numbers = np.random.randint(100, 500, size=n)
guests       = np.random.choice(guest_name_list, size=n)
checkin_day  = np.random.randint(1, 28, size=n)
nights       = np.random.randint(1, 14, size=n)
checkout_day = checkin_day + nights
price_night  = np.array([
    np.random.randint(2000, 5000) if rt == 'Стандарт' else
    np.random.randint(8000, 20000) if rt == 'Люкс' else
    np.random.randint(5000, 8000) if rt == 'Полулюкс' else
    np.random.randint(4000, 7000)
    for rt in room_types
])
total_price  = price_night * nights
status_list  = ['Забронировано', 'Заселён', 'Выселен']
statuses     = np.random.choice(status_list, size=n)

df = pd.DataFrame({
    'ID брони':         booking_id,
    'Отель':            hotels,
    'Тип номера':       room_types,
    'Номер комнаты':    room_numbers,
    'Гость':            guests,
    'День заезда':      checkin_day,
    'День выезда':      checkout_day,
    'Ночей':            nights,
    'Цена за ночь':     price_night,
    'Итого':            total_price,
    'Статус':           statuses,
})

log_action("Исходная таблица броней создана")


#Вспомогательные функции
def next_id(df):
    if df.empty:
        return 1001
    return int(df['ID брони'].max()) + 1


#Добавить бронь
def add_booking(df):
    log_action("Запрос на добавление брони")
    print("Отели:", hotel_list)
    hotel = input("Отель: ").strip()
    if hotel not in hotel_list:
        print("Такого отеля нет в списке.")
        log_action("Ошибка: неизвестный отель — " + hotel)
        return df

    print("Типы номеров:", room_type_list)
    room_type = input("Тип номера: ").strip()
    if room_type not in room_type_list:
        print("Такого типа номера нет.")
        log_action("Ошибка: неизвестный тип номера — " + room_type)
        return df

    try:
        room_num   = int(input("Номер комнаты (100–499): "))
        guest      = input("Фамилия гостя: ").strip()
        checkin    = int(input("День заезда (1–28): "))
        checkout   = int(input("День выезда (2–31): "))
        price      = int(input("Цена за ночь (руб.): "))
    except ValueError:
        print("Ошибка ввода — проверьте формат данных.")
        log_action("Ошибка ввода при добавлении брони")
        return df

    if checkout <= checkin:
        print("День выезда должен быть позже дня заезда.")
        log_action("Ошибка: день выезда <= день заезда")
        return df

    #Проверка
    busy = df[
        (df['Отель'] == hotel) &
        (df['Номер комнаты'] == room_num) &
        (df['Статус'] != 'Выселен') &
        (df['День заезда'] < checkout) &
        (df['День выезда'] > checkin)
    ]
    if not busy.empty:
        print("Номер уже занят в указанный период!")
        log_action(f"Конфликт броней: отель {hotel}, комната {room_num}")
        return df

    nts   = checkout - checkin
    total = price * nts
    bid   = next_id(df)

    new_row = {
        'ID брони':      bid,
        'Отель':         hotel,
        'Тип номера':    room_type,
        'Номер комнаты': room_num,
        'Гость':         guest,
        'День заезда':   checkin,
        'День выезда':   checkout,
        'Ночей':         nts,
        'Цена за ночь':  price,
        'Итого':         total,
        'Статус':        'Забронировано',
    }
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    print(f"Бронь #{bid} добавлена. Итого: {total} руб.")
    log_action(f"Добавлена бронь #{bid}, гость: {guest}, отель: {hotel}")
    return df


#Удалить бронь
def remove_booking(df):
    log_action("Запрос на удаление брони")
    try:
        bid = int(input("Введите ID брони для удаления: "))
    except ValueError:
        print("ID должен быть числом.")
        return df

    mask = df['ID брони'] == bid
    if df[mask].empty:
        print("Бронь не найдена.")
        log_action(f"Бронь #{bid} не найдена при удалении")
        return df

    df = df.drop(df[mask].index).reset_index(drop=True)
    print(f"Бронь #{bid} удалена.")
    log_action(f"Бронь #{bid} удалена")
    return df


#Поиск
def search_bookings(df):
    log_action("Запрос на поиск броней")
    print("1 — По фамилии гостя")
    print("2 — По отелю")
    print("3 — По типу номера")
    print("4 — По статусу")
    choice = input("Ваш выбор: ").strip()

    if choice == "1":
        guest = input("Фамилия гостя: ").strip()
        result = df[df['Гость'] == guest]
        log_action(f"Поиск по гостю: {guest}, найдено: {len(result)}")
    elif choice == "2":
        print("Отели:", hotel_list)
        hotel = input("Отель: ").strip()
        result = df[df['Отель'] == hotel]
        log_action(f"Поиск по отелю: {hotel}, найдено: {len(result)}")
    elif choice == "3":
        print("Типы:", room_type_list)
        rt = input("Тип номера: ").strip()
        result = df[df['Тип номера'] == rt]
        log_action(f"Поиск по типу номера: {rt}, найдено: {len(result)}")
    elif choice == "4":
        print("Статусы:", status_list)
        st = input("Статус: ").strip()
        result = df[df['Статус'] == st]
        log_action(f"Поиск по статусу: {st}, найдено: {len(result)}")
    else:
        print("Неизвестная команда.")
        log_action("Неизвестная команда в поиске: " + choice)
        return

    if result.empty:
        print("Ничего не найдено.")
    else:
        print(result.to_string(index=False))


#Заселить/Выселить 
def change_status(df):
    log_action("Запрос на смену статуса брони")
    try:
        bid = int(input("ID брони: "))
    except ValueError:
        print("ID должен быть числом.")
        return df

    mask = df['ID брони'] == bid
    if df[mask].empty:
        print("Бронь не найдена.")
        log_action(f"Бронь #{bid} не найдена при смене статуса")
        return df

    idx = df[mask].index[0]
    print("Текущий статус:", df.at[idx, 'Статус'])
    print("Статусы:", status_list)
    new_status = input("Новый статус: ").strip()
    if new_status not in status_list:
        print("Такого статуса нет.")
        return df

    df.at[idx, 'Статус'] = new_status
    print(f"Статус брони #{bid} изменён на '{new_status}'.")
    log_action(f"Статус брони #{bid} изменён на {new_status}")
    return df


#Статистика
def stats(df):
    log_action("Запрос на статистику")
    print("\nСТАТИСТИКА")

    #1. Средняя цена за ночь по типу номера
    print("\nСредняя цена за ночь по типу номера:")
    avg = df.groupby('Тип номера')['Цена за ночь'].mean()
    for k, v in avg.items():
        print(f"  {k}: {v:.0f} руб.")

    #2. Общая выручка по отелям
    print("\nОбщая выручка по отелям:")
    rev = df.groupby('Отель')['Итого'].sum().sort_values(ascending=False)
    for k, v in rev.items():
        print(f"  {k}: {v:,} руб.")

    #3. Топ 3 самых дорогих брони
    print("\nТоп-3 самых дорогих брони:")
    top = df.sort_values('Итого', ascending=False).head(3)
    print(top[['ID брони', 'Гость', 'Отель', 'Тип номера', 'Ночей', 'Итого']].to_string(index=False))

    #4. Средняя продолжительность пребывания
    avg_nights = df['Ночей'].mean()
    print(f"\nСредняя продолжительность пребывания: {avg_nights:.1f} ночей")

    #5. Брони с количеством ночей
    try:
        x = int(input("\nПоказать брони длиннее X ночей. Введите X: "))
    except ValueError:
        print("Некорректное значение.")
        return
    long_stays = df[df['Ночей'] > x]
    if long_stays.empty:
        print(f"Броней длиннее {x} ночей нет.")
    else:
        print(long_stays.to_string(index=False))

    log_action("Статистика выведена")


#Сортировка
def sortirovka(df):
    log_action("Запрос на сортировку")
    print("1 — По цене (возрастание)")
    print("2 — По цене (убывание)")
    print("3 — По дню заезда")
    print("4 — По количеству ночей")
    choice = input("Ваш выбор: ").strip()

    col_map = {"1": ("Итого", True), "2": ("Итого", False),
               "3": ("День заезда", True), "4": ("Ночей", False)}

    if choice not in col_map:
        print("Неизвестная команда.")
        log_action("Неизвестная команда сортировки: " + choice)
        return df

    col, asc = col_map[choice]
    sorted_df = df.sort_values(col, ascending=asc)
    print(sorted_df.to_string(index=False))
    log_action(f"Сортировка по '{col}', ascending={asc}")
    return df


#Маршруты по типу номера
def show_by_type(df):
    log_action("Запрос на вывод по типу номера")
    print("Типы номеров:", room_type_list)
    rt = input("Тип номера: ").strip()
    if rt not in room_type_list:
        print("Такого типа нет.")
        log_action("Введён неизвестный тип номера: " + rt)
        return
    result = df[df['Тип номера'] == rt]
    if result.empty:
        print("Броней с таким типом номера нет.")
    else:
        print(result.to_string(index=False))
    log_action(f"Вывод по типу номера '{rt}': найдено {len(result)}")


#Диаграмма 1: выручка по отелям
def diag_1(df):
    log_action("Запрос на диаграмму выручки по отелям")
    rev = df.groupby('Отель')['Итого'].sum()
    if rev.empty:
        print("Нет данных.")
        return
    plt.figure(figsize=(8, 4))
    plt.bar(rev.index, rev.values, color='steelblue', edgecolor='white')
    plt.xlabel('Отель')
    plt.ylabel('Выручка, руб.')
    plt.title('Выручка по отелям')
    plt.xticks(rotation=20, ha='right')
    plt.tight_layout()
    plt.savefig("diag1.png")
    plt.show()
    print("Диаграмма сохранена в diag1.png")
    log_action("Диаграмма diag1.png сохранена")


#Диаграмма 2: распределение по типам номеров
def diag_2(df):
    log_action("Запрос на диаграмму распределения типов номеров")
    counts = df['Тип номера'].value_counts()
    if counts.empty:
        print("Нет данных.")
        return
    plt.figure(figsize=(6, 6))
    plt.pie(counts.values, labels=counts.index, autopct='%1.0f%%',
            colors=['steelblue', 'coral', 'mediumseagreen', 'gold'])
    plt.title('Распределение броней по типам номеров')
    plt.tight_layout()
    plt.savefig("diag2.png")
    plt.show()
    print("Диаграмма сохранена в diag2.png")
    log_action("Диаграмма diag2.png сохранена")


#График: средняя цена по отелям
def gr_1(df):
    log_action("Запрос на график средней цены по отелям")
    avg = df.groupby('Отель')['Цена за ночь'].mean()
    if avg.empty:
        print("Нет данных.")
        return
    plt.figure(figsize=(8, 4))
    plt.bar(avg.index, avg.values, color='coral', edgecolor='white')
    plt.xlabel('Отель')
    plt.ylabel('Средняя цена за ночь, руб.')
    plt.title('Средняя цена за ночь по отелям')
    plt.xticks(rotation=20, ha='right')
    plt.tight_layout()
    plt.savefig("gr1.png")
    plt.show()
    print("График сохранён в gr1.png")
    log_action("График gr1.png сохранён")


#Экспорт в CSV
def save_csv(df):
    df.to_csv('result.csv', index=False, encoding='utf-8-sig')
    print("Данные сохранены в result.csv")
    log_action("Данные экспортированы в result.csv")


#Меню
def menu(df):
    log_action("Открыто главное меню")
    while True:
        print("СИСТЕМА БРОНИРОВАНИЯ ОТЕЛЕЙ")
        print(" 1  — Показать все брони")
        print(" 2  — Добавить бронь")
        print(" 3  — Удалить бронь")
        print(" 4  — Поиск броней")
        print(" 5  — Изменить статус брони")
        print(" 6  — Показать статистику")
        print(" 7  — Сортировка")
        print(" 8  — Фильтр по типу номера")
        print(" 9  — Диаграмма выручки по отелям")
        print(" 10 — Диаграмма типов номеров")
        print(" 11 — График средней цены по отелям")
        print(" 12 — Сохранить в CSV")
        print(" 0  — Выход")

        choice = input("Ваш выбор: ").strip()
        log_action("Выбран пункт меню: " + choice)

        if choice == "1":
            print(df.to_string(index=False))
            log_action("Показаны все брони")

        elif choice == "2":
            df = add_booking(df)

        elif choice == "3":
            df = remove_booking(df)

        elif choice == "4":
            search_bookings(df)

        elif choice == "5":
            df = change_status(df)

        elif choice == "6":
            stats(df)

        elif choice == "7":
            df = sortirovka(df)

        elif choice == "8":
            show_by_type(df)

        elif choice == "9":
            diag_1(df)

        elif choice == "10":
            diag_2(df)

        elif choice == "11":
            gr_1(df)

        elif choice == "12":
            save_csv(df)

        elif choice == "0":
            print("Выход из программы.")
            log_action("Выход из программы")
            break

        else:
            print("Неизвестная команда.")
            log_action("Неизвестная команда в меню: " + choice)

    return df


#Запуск
df = menu(df)
print("\nИтоговая таблица:")
print(df.to_string(index=False))
log_action("Программа завершена. Итоговое количество броней — " + str(len(df)))
