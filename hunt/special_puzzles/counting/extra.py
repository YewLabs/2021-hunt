from hunt.special_puzzles.counting.models import QuizbOwlQuestion


QUESTION_FILE_PATH = '2021-hunt/hunt/special_puzzles/counting/owl_questions.txt'


def load_trivia():
  with open(QUESTION_FILE_PATH, 'r') as f:
    lines = list(f)

  QuizbOwlQuestion.objects.all().delete()

  for line in lines:
    if not line.strip():
      continue
    answer, question = line.strip().split('|')
    item = QuizbOwlQuestion(question=question, answer=int(answer))
    item.save()

  print(f'Refreshed Quizb Owl question database with {len(lines)} questions.')
