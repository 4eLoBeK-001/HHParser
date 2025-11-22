import os
import json

path = 'hh_app/progress.json'

def load_json(path: str) -> dict:
    # Если файла нет - создаём новый
    if not os.path.exists(path):
        with open(path, 'w', encoding='utf-8') as f:
            json.dump({}, f, ensure_ascii=False, indent=4)
        return {}
    
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def next_page_json(path: str):
    """Сдвигает страницу на 1"""
    data = load_json(path=path)
    data['page'] += 1

    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


next_page_json(path)
