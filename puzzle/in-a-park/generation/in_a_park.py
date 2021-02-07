import csv
import os

fname = "Runaround"
data_name = "Form Respon"
spec_name = "Sheet2"
spec_filename = None
data_filename = None
files = os.listdir('.')
for filename in files:
    if fname in filename and filename.endswith('.csv'):
        # print(filename)
        if spec_name in filename:
            spec_filename = filename
        if data_name in filename:
            data_filename = filename

data = {}
beginning = []
ending = {}
answers = {}

# Decoys
ending["D"] = "What is the first word of the name of the station halfway between the Canal Exploration Center and the Peninsula Depot stations?"
ending["Y"] = "What is the distance in feet between the parking lots at the entrances to the Big Plateau Trail and the Jones Creek Trail, rounded to the nearest multiple of 1000?"
ending["M"] = "What creature seen in Tolkien names a chasm in a national park?"
ending["BRECKSVILLE"] = "How many benches are on the roof of the Eielson Visitor Center?"
ending["1986"] = "What is the second word of a famous hike that involves 400 foot cables near the end?"
ending["1912"] = "Go to the basketball hoop closest to the northern edge of the park. Looking at a circular area nearby, consider the two directions that the paths lead this circular area. From this vantage point, what semaphore letter do they make?"

ending["H"] = "How many boats can be parked at once in the lot outside the Kenai Fjords National Park Visitor Center?"
ending["36"] = "What is the direction, to the nearest 10 degrees, from the southwest corner of the park to the pavilion?"
ending["0"] = "Find the number of dogs in the park, and multiply by 7."
ending["SOUTH"] = "Go to the lowest point in the park. Go north until you run into a wall. What is the third word listed on that wall?"
ending["6"] = "How many trees in the park have an even number of leaves?"

row_credit = {}

with open(data_filename) as f:
    data_csv = csv.reader(f)
    for rownum,data_row in enumerate(data_csv):
        # print(data_row)
        if not rownum: continue
        for i in range(8,28,2):
            clue = data_row[i]
            answer = data_row[i+1]
            if clue == 'LOCUST':
                print(rownum, clue, answer, "\n".join(data_row))
            # if answer in data:
            #     raise Exception("Duplicate Key: "+answer)
            data[(rownum,answer.upper())] = clue
        row_credit[rownum] = data_row[1]

print(row_credit, len(row_credit))
credit = []
# print(data)
endanswers = "XA4"
with open(spec_filename) as f:
    spec_csv = csv.DictReader(f)
    for spec_i,spec_row in enumerate(spec_csv):
        inst = spec_row["Instruction"].strip()
        if not inst.endswith("."):
            inst += '.'
        beginning.append(f'<b>{spec_row["City"]}: {spec_row["Park"]}</b> - {inst}')
        ending[spec_row["Park"].upper()] = spec_row["Clue"]
        answers[spec_row['Clue']] = spec_row['3 clues']
        credit.append((spec_row['Park'],row_credit[spec_i+1]))
        print(spec_i)
        groups = [[],[],[]]
        endadd = ["","",""]
        for i,a in enumerate(spec_row['3 clues'].split(' ')):
            groups[i].append(a)
        for i in range(1,4):
            for j in range(1,4):
                groups[i-1].append(spec_row[f"c{i}{j}"])
            endkey = f'c{i}3_add'
            if endkey in spec_row:
                endadd[i-1] = spec_row[endkey]
        # print(groups)
        for ei,(group,ea) in enumerate(zip(groups, endadd)):
            for i,a in enumerate(group[:-1]):
                if a in ending:
                    raise Exception("Duplicate key: "+a)
                ending[a] = data[spec_i+1, group[i+1]]
                answers[ending[a]] = group[i+1]
                if i == 2:
                    ending[a] += ' '+ea
                    answers[ending[a]] = endanswers[ei]


ending["X"] = "What sport’s world record is exactly the elevation gain of the Modelo Trail?"
ending["A"] = "What used to be mined in the place that is a 92.5 mile bus ride into a park?"
ending["4"] = "Take the price of Yellowstone in National Parks Monopoly, and multiply by the number of counties Yellowstone spans. Add the number of US National Parks that had more than 2.5 million visitors in 2019."

answers[ending["X"]] = "MEN'S JAVELIN"
answers[ending["A"]] = "GOLD"
answers[ending["4"]] = "2012"

from typing import Tuple
def getkey(item: Tuple[str,str]):
    x,y = item
    if x.isnumeric():
        return x.zfill(10)
    else:
        return x
top_bit = """{% if 'in-a-park' in solved %}
<iframe src="https://docs.google.com/forms/d/e/1FAIpQLSe0V5uw8r84nZ9XJf7RbB3mI15wHxz7C0HkIo6FGgV7W9FhNQ/viewform" width="80%" height="1000px"></iframe>
{% endif %}"""
with open('../index.html','w') as puzzle:
    print(f"""{top_bit}
<div class="fourthwall">This puzzle will be extremely difficult or impossible to do without actually visiting the park. Hints are immediately open on this puzzle in case you have an issue while you are in the park itself.</div><p>Find a park near you from the list below. </p>""",file=puzzle)
    print("<br>\n".join(sorted(beginning)),file=puzzle)
    print("<img width='100%' src='{{sroot}}path.png'>",file=puzzle)
    print("<br>\n".join(f"<b>{x}</b>: {y}" for x,y in sorted(ending.items(),key=getkey)),file=puzzle)

header = f"""
<p>This puzzle is an in-person runaround in one of twenty or so parks in different cities. First, we must choose a park to visit from the list, and go there. Once we're in one of the parks (let's use <b>Fort Greene Park</b> as an example), we look the name of the park up in the huge list. That gives us a clue with a three word answer. In this case, the answer is <b>SPLENDOR ANOTHER CENTURY</b>.</p>

<img width='100%' src='{{sproot}}path.png'>

<p>Now, we look to the image in the puzzle that points to the path splitting in three. We can look up each of the three words in our answer in the list to get another clue. Each clue gives an answer that we can look up in the list again. We repeat this process three times, following the paths in the image. The third clue in each chain will resolve to a clue that does not appear to be about the park we are in:</p>

<br>
<b>X</b>: What sport’s world record is exactly the elevation gain of the Modelo Trail?<br>
<b>A</b>: What used to be mined in the place that is a 92.5 mile bus ride into a park?<br>
<b>4</b>: Take the price of Yellowstone in National Parks Monopoly, and multiply by the number of counties Yellowstone spans. Add the number of US National Parks that had more than 2.5 million visitors in 2019.
<br>

<p>These clues are about US National Parks. Their answers, which fit in the red blanks in the image, are respectively <b>MEN'S JAVELIN</b>, <b>GOLD</b> and <b>2012</b>. The winner of the gold medal in the Men's Javelin in the 2012 Olympics was <span class="answer">Keshorn Walcott</span>, who fits the enumeration in the image.</p>

<div class="author-note">
<h2>Authors’ Notes</h2>

We thought it wouldn't truly be a Mystery Hunt without a real runaround puzzle. We hope any runaround fans liked this one!
<p>
In our hunt registration, we asked teams where in the world they would be solving from, and we aimed to have at least one park in every popular area. We sought out friends and friends-of-friends to help us write clues in some places where none of our teammates live.

</div>

<h2>Appendix</h2>
"""

with open('../solution/index.html','w') as solution:
    print(header,file=solution)
    print("<br>\n".join(f"<b>{x}</b>: {y} &rightarrow; <b>{answers.get(y,'(decoy)')}</b>" for x,y in sorted(ending.items(),key=getkey)),file=solution)

print('<br>'.join(f'{park} clues by {person}' for (park, person) in sorted(credit)))
