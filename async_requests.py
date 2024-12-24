import asyncio
import datetime
import aiohttp
import more_itertools
from models import SwapiPeople, Session, init_orm, close_orm

MAX_COROS = 10

async def fetch_names_from_urls(urls, http_session):
    names = []
    for url in urls:
        async with http_session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                names.append(data.get('name', 'Unknown'))
    return names

async def get_people(person_id, http_session):
    url = f'https://swapi.py4e.com/api/people/{person_id}/'
    async with http_session.get(url) as response:
        if response.status != 200:
            return {'id': person_id, 'detail': 'not found'}
        json_data = await response.json()
        json_data['films'] = await fetch_names_from_urls(json_data.get('films', []), http_session)
        json_data['species'] = await fetch_names_from_urls(json_data.get('species', []), http_session)
        json_data['starships'] = await fetch_names_from_urls(json_data.get('starships', []), http_session)
        json_data['vehicles'] = await fetch_names_from_urls(json_data.get('vehicles', []), http_session)
        json_data['homeworld'] = await fetch_names_from_urls([json_data.get('homeworld')], http_session) if json_data.get('homeworld') else None
        return json_data

async def insert_people(json_list):
    async with Session() as session:
        session.add_all([
            SwapiPeople(
                id=int(item['url'].split('/')[-2]),
                birth_year=item.get('birth_year'),
                eye_color=item.get('eye_color'),
                films=', '.join(item.get('films', [])),
                gender=item.get('gender'),
                hair_color=item.get('hair_color'),
                height=int(item['height']) if item['height'].isdigit() else None,
                homeworld=', '.join(item.get('homeworld', [])) if item.get('homeworld') else None,
                mass=int(item['mass']) if item['mass'].isdigit() else None,
                name=item.get('name'),
                skin_color=item.get('skin_color'),
                species=', '.join(item.get('species', [])),
                starships=', '.join(item.get('starships', [])),
                vehicles=', '.join(item.get('vehicles', []))
            ) for item in json_list if 'url' in item
        ])
        await session.commit()

async def main():
    await init_orm()
    async with aiohttp.ClientSession() as http_session:
        tasks = []
        for i_list in more_itertools.chunked(range(1, 101), MAX_COROS):
            coros = [get_people(i, http_session) for i in i_list]
            result = await asyncio.gather(*coros)
            tasks.append(asyncio.create_task(insert_people(result)))
        await asyncio.gather(*tasks)
    await close_orm()


start = datetime.datetime.now()
asyncio.run(main())
print(datetime.datetime.now() - start)
