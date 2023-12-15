import asyncio
from pprint import pprint

import aiohttp
from models import Session, SwapiPeople, init_db
from more_itertools import chunked

CHUNK_SIZE = 10  # Chank - кусочек


# Запрос на вложенные ссылки. Возврат наименований в виде строки.
async def internal_data(url_list, session):
    string = []
    for url in url_list:
        responce = await session.get(url)
        data = await responce.json()
        string.append(data["name"] if "name" in data else data["title"])

    return ", ".join(string)


# Получение информации о персонаже.
async def get_person(person_id, session):
    try:
        url = f"https://swapi.dev/api/people/{person_id}/"
        response = await session.get(url)
        data = await response.json()

        if response.status == 404:
            return

        # Удаление лишних полей.
        del data["created"]
        del data["edited"]
        del data["url"]

        data["mass"] = int(data["mass"])
        data["height"] = int(data["height"])
        data["films"] = await internal_data(data["films"], session)
        data["species"] = await internal_data(data["species"], session)
        data["starships"] = await internal_data(data["starships"], session)
        data["vehicles"] = await internal_data(data["vehicles"], session)

        return data

    except:
        return


async def insert_to_db(poeple_list: list):  # Принимает на вход список. + Типизируем.
    async with Session() as session:  # Открываем сессию.
        people = [SwapiPeople(**data) for data in poeple_list if data is not None]
        # Создаём ORM-модели с помощью list comprehension
        # + Закидываем полученную информацию в эти модели.
        session.add_all(people)  # Добавляем сессию.
        await session.commit()  # Комитимся.


async def main():
    await init_db()  # Инициализируем БД.
    session = aiohttp.ClientSession()  # Содаём сессию

    for people_id_chunk in chunked(
        range(1, 1000), CHUNK_SIZE
    ):  # Разбиваем на последовательности по 10
        # Без create_task мы можем перейти на следующий цикл итерации только после того,
        # как произойдёт вставка в базу
        coros = [get_person(person_id, session) for person_id in people_id_chunk]
        # Создаём карутины (предподготовленные запросы)
        result = await asyncio.gather(*coros)
        asyncio.create_task(
            insert_to_db(result)
        )  # Объект задач (create_task) формируется на базе карутин и начинает
        # выполняться сразу после создания. Но при этом задача не блокирует дальнейшее выполнение кода.
        # Это означает, что вставка в базу будет происходить конкурентно с получением следующей пачки персонажей.
        # Со следующей итерацией нашего цикла.
        pprint(result)

    await session.close()

    set_of_tasks = asyncio.all_tasks() - {
        asyncio.current_task()
    }  # Исключаем из сета задач main
    await asyncio.gather(*set_of_tasks)


if __name__ == "__main__":
    asyncio.run(main())
