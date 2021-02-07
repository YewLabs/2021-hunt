import base64

from mistletoe.span_tokenizer import tokenize_span
from mistletoe.span_tokens import (Emphasis, LineBreak, RawText, Strong)

from hunt.special_puzzles.cafe_luge.question_parser import Question, QuestionSet

def path_to_b64encode(path):
    with open(path, 'rb') as fd:
        return base64.b64encode(fd.read()).decode('utf-8')


def markdown_text_to_json(text):
    # Converts Markdown text to a JSON-friendly form.
    r = []
    spans = tokenize_span(text)
    bold = False
    italic = False

    def _r(t):
        nonlocal italic
        nonlocal bold
        if isinstance(t, Emphasis):
            bold = True
            for c in t.children:
                _r(c)
            bold = False
            return

        if isinstance(t, Strong):
            italic = True
            for c in t.children:
                _r(c)
            italic = False
            return

        if isinstance(t, RawText):
            _d = {'type': 'text', 'value': t.content}
            if italic:
                _d['italic'] = True
            if bold:
                _d['bold'] = True
            r.append(_d)
            return

        if isinstance(t, LineBreak):
            return

        print(f'Invalid token {t} in text {text}')

    for span in spans:
        _r(span)
    return r


def question_to_msg(question):
    r = []

    for chunk in question.content:
        chunk_type, content = next(iter(chunk.items()))

        if chunk_type == 'answer' or chunk_type == 'credit':
            continue

        if chunk_type == 'text':
            for fragment in markdown_text_to_json(content):
                r.append(fragment)
            continue
        if chunk_type == 'image' or chunk_type == 'audio':
            path = f'2021-hunt/hunt/special_puzzles/cafe_luge/puzzles/{content}'
            encoded_content = path_to_b64encode(path)
            r.append({'type': chunk_type, 'value': encoded_content})
            continue
        if chunk_type == 'twocolumn':
            r.append({
                'type': chunk_type,
                'value': [
                    markdown_text_to_json(content[0]['text']),
                    markdown_text_to_json(content[1]['text']),
                ]
            })
            continue

        print(f'Unknown chunk type {chunk_type}')

    return r
