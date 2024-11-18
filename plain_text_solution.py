import json

PLAIN_TEXT_SOLUTION: dict[str, str] = dict() # dictionary for plain text solutions

with open('./JSON/plain_text.json', 'r', encoding='utf-8') as f:
    PLAIN_TEXT: dict[str, dict[str, dict[str, str]]] = json.load(f) # dictionary for plain text lessons {grade: {day: {lesson: lesson_text}}}
                                                                    # generated by main.py; finally used here

for grade in PLAIN_TEXT: # iterate over the grades in PLAIN_TEXT
    for day in PLAIN_TEXT[grade]: # iterate over the days in PLAIN_TEXT[grade]
        for lesson in PLAIN_TEXT[grade][day]: # iterate over the lessons in PLAIN_TEXT[grade][day]
            if PLAIN_TEXT_SOLUTION.get(PLAIN_TEXT[grade][day][lesson]) is not None: # if the lesson is already in the PLAIN_TEXT_SOLUTION, skip it
                continue
            print(f'{grade}/{day}/{lesson}: {PLAIN_TEXT[grade][day][lesson]}: ', end='') # else print the lesson and ask for the solution 
                                                                                         # (must be done by hand sorry :/)
            w=input()
            PLAIN_TEXT_SOLUTION[PLAIN_TEXT[grade][day][lesson]] = w if w != '' else None # if the solution is not empty, 
                                                                                         # add it to the PLAIN_TEXT_SOLUTION
                                                                                         # else add None (it's not necessary)
            print()
with open('./JSON/plain_text_solution.json', 'w', encoding='utf-8') as f:
    json.dump(PLAIN_TEXT_SOLUTION, f, ensure_ascii=False, indent=4) # save the PLAIN_TEXT_SOLUTION to the file