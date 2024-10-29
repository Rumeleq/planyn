import requests
from bs4 import BeautifulSoup as bs, Tag
import json

URL = 'https://www.zsk.poznan.pl/plany_lekcji/2023plany/technikum/plany/'
WEEK = ['poniedzialek', 'wtorek', 'sroda', 'czwartek', 'piatek']
PLANY = dict()

with open('./JSON/lessons.json', 'r', encoding='utf-8') as f:
    LESSONS = json.load(f)
with open('./JSON/teachers.json', 'r', encoding='utf-8') as f:
    TEACHERS = json.load(f)


def extract_data(span: tuple[Tag, Tag, Tag], num_col: int, num_row: int, class_id: str) -> None:
    lesson_title = span[0].text.split('-')[0] \
        if span[0].text not in LESSONS \
        else LESSONS[span[0].text]
    lesson_teacher = span[1].text \
        if span[1].text[0] != '#' \
        else TEACHERS[span[1].text]
    lesson_classroom = span[2].text

    if lesson_teacher not in PLANY:
        #  add names instead of initials
        PLANY[lesson_teacher] = {day: ['' for _ in range(11)] for day in WEEK}
    if PLANY[lesson_teacher][WEEK[num_col - 2]][num_row - 1] == '':
        PLANY[lesson_teacher][WEEK[num_col - 2]][num_row - 1] = f'{class_id} {lesson_title} {lesson_classroom}'
    elif PLANY[lesson_teacher][WEEK[num_col - 2]][num_row - 1].split(' ')[1] == lesson_title and \
            PLANY[lesson_teacher][WEEK[num_col - 2]][num_row - 1].split(' ')[2] == lesson_classroom:
        PLANY[lesson_teacher][WEEK[num_col - 2]][
            num_row - 1] = f'{PLANY[lesson_teacher][WEEK[num_col - 2]][num_row - 1].split(' ')[0]},{class_id} {lesson_title} {lesson_classroom}'
    else:
        raise ValueError(
            f'Error: {PLANY[lesson_teacher][WEEK[num_col - 2]][num_row - 1]} != {class_id} {lesson_title} {lesson_classroom}')


def main():
    i = 0
    while True:
        i += 1
        class_schedule = requests.get(f'{URL}o{i}.html')
        if class_schedule.status_code != 200:
            break
        soup = bs(class_schedule.content, 'html.parser')
        class_id = soup.find('span', class_='tytulnapis').text.split(' ')[0]
        print(class_id)
        for num_row, row in enumerate(soup.find('table', class_='tabela').find_all('tr')[1:], start=1):
            for num_col, col in enumerate(row.find_all('td')[2:], start=2):
                col_spans = col.find_all('span', recursive=False)
                if len(col_spans) == 0:
                    pass
                    # if col.text != '\xa0':
                    #     print(col)
                    #  to be added (plain text problem)
                elif len(col_spans) == 2:
                    for span in col_spans:
                        extract_data(span.find_all('span'), num_col, num_row, class_id)
                elif len(col_spans) == 3:
                    extract_data(col_spans, num_col, num_row, class_id)
                else:
                    it = iter(col_spans)
                    col_spans = zip(it, it, it)
                    for span in col_spans:
                        extract_data(span, num_col, num_row, class_id)


if __name__ == '__main__':
    main()
    with open('./JSON/plany.json', 'w', encoding='utf-8') as f:
        json.dump(PLANY, f, ensure_ascii=False, indent=4)
