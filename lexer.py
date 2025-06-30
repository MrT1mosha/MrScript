import re
from collections import namedtuple

Token = namedtuple('Token', ['type', 'value'])

def tokenize(source_code):
    keywords = {'START', 'write', 'if', 'func'}

    token_specification = [
        ('NUMBER',    r'\d+'),
        ('STRING',    r'"[^"]*"'),
        ('EQUALS',    r'='),
        ('PLUS',      r'\+'),
        ('MINUS',     r'-'),
        ('MULTIPLY',  r'\*'),
        ('DIVIDE',    r'/'),
        ('LPAREN',    r'\('),
        ('RPAREN',    r'\)'),
        ('LBRACE',    r'\{'),
        ('RBRACE',    r'\}'),
        ('COMMA', r','),
        ('IDENTIFIER',r'[A-Za-z_]\w*'),
        ('NEWLINE',   r'\n'),
        ('SKIP',      r'[ \t]+'),
        ('MISMATCH',  r'.'),
    ]

    tok_regex = '|'.join(f'(?P<{name}>{regex})' for name, regex in token_specification)
    get_token = re.compile(tok_regex).match

    pos = 0
    tokens = []
    mo = get_token(source_code, pos)

    while mo is not None:
        kind = mo.lastgroup
        value = mo.group()

        if kind == 'NUMBER':
            tokens.append(Token('NUMBER', value))
        elif kind == 'STRING':
            tokens.append(Token('STRING', value.strip('"')))
        elif kind == 'IDENTIFIER':
            if value in keywords:
                tokens.append(Token('KEYWORD', value))
            else:
                tokens.append(Token('IDENTIFIER', value))
        elif kind == 'NEWLINE' or kind == 'SKIP':
            pass
        elif kind == 'MISMATCH':
            raise RuntimeError(f'Unexpected character {value!r}')
        elif kind == 'EQUALS':
            tokens.append(Token('EQUALS', value))
        elif kind in {'PLUS', 'MINUS', 'MULTIPLY', 'DIVIDE'}:
            tokens.append(Token('OPERATOR', value))
        elif kind in {'LPAREN', 'RPAREN', 'LBRACE', 'RBRACE'}:
            tokens.append(Token(kind, value))

        pos = mo.end()
        mo = get_token(source_code, pos)

    return tokens