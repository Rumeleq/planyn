from collections.abc import Iterator
import requests as req
from bs4 import BeautifulSoup as bs, ResultSet, Tag
import json

URL: str = 'https://www.zsk.poznan.pl/plany_lekcji/2023plany/technikum/plany/'
WEEK: list[str] = ['poniedzialek', 'wtorek', 'sroda', 'czwartek', 'piatek']
PLANY = dict()
#debuging
PLAIN_TEXT = dict()

with open('./JSON/lessons.json', 'r', encoding='utf-8') as f:
    LESSONS = json.load(f)
with open('./JSON/teachers.json', 'r', encoding='utf-8') as f:
    TEACHERS = json.load(f)
with open('./JSON/plain_text_solution.json', 'r', encoding='utf-8') as f:
    PLAIN_TEXT_SOLUTION = json.load(f)

def extract_data(span: ResultSet[Tag], num_col: int, num_row: int, grade: str) -> None:
    lesson_title: str = span[0].text.split('-')[0] if span[0].text not in LESSONS else LESSONS[span[0].text]
    lesson_teacher: str = span[1].text if span[1].text[0] != '#' else TEACHERS[span[1].text]
    lesson_classroom: str = span[2].text
    if lesson_teacher not in PLANY:
        #add names instead of initials
        PLANY[lesson_teacher] = {day: ['' for _ in range(11)] for day in WEEK}
    if PLANY[lesson_teacher][WEEK[num_col]][num_row] == '':
        PLANY[lesson_teacher][WEEK[num_col]][num_row] = f'{grade} {lesson_title} {lesson_classroom}'
    elif PLANY[lesson_teacher][WEEK[num_col]][num_row].split(' ')[1] == lesson_title and PLANY[lesson_teacher][WEEK[num_col]][num_row].split(' ')[2] == lesson_classroom:
        PLANY[lesson_teacher][WEEK[num_col]][num_row] = f'{PLANY[lesson_teacher][WEEK[num_col]][num_row].split(' ')[0]},{grade} {lesson_title} {lesson_classroom}'
    else:
        raise ValueError(f'Error: {PLANY[lesson_teacher][WEEK[num_col]][num_row]} != {grade} {lesson_title} {lesson_classroom}')

def main() -> None:
    for i in range(1, 32):
        page: req.Response = req.get(f'{URL}o{i}.html')
        soup: bs = bs(page.content, 'html.parser')
        grade: str = soup.find('span', class_ = 'tytulnapis').text.split(' ')[0]
        print(grade)
        num_row: int; row: Tag
        for num_row, row in enumerate(soup.find('table', class_='tabela').find_all('tr')[1:]):
            num_col: int; col: Tag
            for num_col, col in enumerate(row.find_all('td')[2:]):
                col_spans: ResultSet[Tag] = col.find_all('span', recursive=False)
                if len(col_spans) == 0:
                    if col.text == '\xa0': continue
                    if grade not in PLAIN_TEXT:
                        PLAIN_TEXT[grade] = dict()
                    if num_col not in PLAIN_TEXT[grade]:
                        PLAIN_TEXT[grade][num_col] = dict()
                    PLAIN_TEXT[grade][num_col][num_row] = col.text
                    
                    if col.text not in PLAIN_TEXT_SOLUTION:
                        raise ValueError(f'Error: {col.text} not in PLAIN_TEXT_SOLUTION')
                    if PLAIN_TEXT_SOLUTION[col.text] is None:
                        continue
                    else:
                        if '/' in PLAIN_TEXT_SOLUTION[col.text]:
                            col_spans: list[str] = PLAIN_TEXT_SOLUTION[col.text].split('/')
                            for span in col_spans:
                                span: ResultSet[Tag] = [bs(f'<span>{x}</span>', 'html.parser').find('span', recursive=False) for x in span.split(' ')]
                                extract_data(span, num_col, num_row, grade)
                        else:
                            span: ResultSet[Tag] = [bs(f'<span>{x}</span>', 'html.parser').find('span', recursive=False) for x in PLAIN_TEXT_SOLUTION[col.text].split(' ')]
                            extract_data(span, num_col, num_row, grade)
                    
                    #to be added (plain text problem)
                elif len(col_spans) == 3:
                    extract_data(col_spans, num_col, num_row, grade)
                elif len(col_spans) == 2:
                    span: Tag
                    for span in col_spans:
                        extract_data(span.find_all('span'), num_col, num_row, grade)
                elif len(col_spans) == 1:
                    col_spans: ResultSet[Tag] = col_spans[0].find_all('span', recursive=False)
                    extract_data(col_spans, num_col, num_row, grade)
                else:
                    it: Iterator[Tag] = iter(col_spans)
                    col_spans: zip[tuple[Tag, Tag, Tag]] = zip(it, it, it)
                    span: Tag
                    for span in col_spans:
                        extract_data(span, num_col, num_row, grade)
                    
if __name__ == '__main__':
    main()  
    with open('./JSON/plany.json', 'w', encoding='utf-8') as f:
        json.dump(PLANY, f, ensure_ascii=False, indent=4)
    with open('./JSON/plain_text.json', 'w', encoding='utf-8') as f:
        json.dump(PLAIN_TEXT, f, ensure_ascii=False, indent=4)