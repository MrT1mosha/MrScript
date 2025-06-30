from lexer import Token  # твій лексер, який повертає Token

# --- AST вузли ---

class Program:
    def __init__(self, statements):
        self.statements = statements

class WriteStatement:
    def __init__(self, expression):
        self.expression = expression

class Number:
    def __init__(self, value):
        self.value = value

class String:
    def __init__(self, value):
        self.value = value

class Identifier:
    def __init__(self, name):
        self.name = name

class Assignment:
    def __init__(self, identifier, expression):
        self.identifier = identifier  # об’єкт Identifier
        self.expression = expression

class BinOp:
    def __init__(self, left, op, right):
        self.left = left
        self.op = op  # '+', '-', '*', '/'
        self.right = right

class IfStatement:
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body

class FuncDef:
    def __init__(self, name, params, body):
        self.name = name
        self.params = params  # список параметрів (імен)
        self.body = body

class FuncCall:
    def __init__(self, name, args):
        self.name = name
        self.args = args  # список аргументів

# --- Parser ---

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def current_token(self):
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None

    def advance(self):
        self.pos += 1

    def expect(self, type_, value=None):
        token = self.current_token()
        if token is None:
            raise SyntaxError("Unexpected end of input")

        if token.type != type_ or (value is not None and token.value != value):
            raise SyntaxError(f"Expected {type_} {value}, got {token}")

        self.advance()
        return token

    def parse(self):
        self.expect('KEYWORD', 'START')
        statements = self.parse_block()
        return Program(statements)

    def statement(self):
        token = self.current_token()

        if token.type == 'KEYWORD':
            if token.value == 'write':
                self.advance()
                expr = self.expression()
                return WriteStatement(expr)
            elif token.value == 'if':
                self.advance()
                condition = self.expression()
                body = self.parse_block()
                return IfStatement(condition, body)
            elif token.value == 'func':
                self.advance()
                name_token = self.expect('IDENTIFIER')
                self.expect('LPAREN')
                params = self.parse_param_list()
                self.expect('RPAREN')
                body = self.parse_block()
                return FuncDef(name_token.value, params, body)

        elif token.type == 'IDENTIFIER':
            next_token = self.tokens[self.pos + 1] if self.pos + 1 < len(self.tokens) else None
            if next_token and next_token.type == 'LPAREN':
                name = token.value
                self.advance()  # ім'я функції
                self.advance()  # '('
                args = self.parse_arguments()
                return FuncCall(name, args)
            else:
                id_node = Identifier(token.value)
                self.advance()
                self.expect('EQUALS')
                expr = self.expression()
                return Assignment(id_node, expr)

        raise SyntaxError(f"Unexpected token {token}")

    def parse_block(self):
        self.expect('LBRACE')
        statements = []
        while True:
            token = self.current_token()
            if token is None:
                raise SyntaxError("Unexpected end of input, expected '}'")
            if token.type == 'RBRACE':
                self.advance()
                break
            stmt = self.statement()
            statements.append(stmt)
        return statements

    def expression(self):
        node = self.term()
        while True:
            token = self.current_token()
            if token and token.type == 'OPERATOR' and token.value in ('+', '-'):
                op = token.value
                self.advance()
                right = self.term()
                node = BinOp(node, op, right)
            else:
                break
        return node

    def term(self):
        node = self.factor()
        while True:
            token = self.current_token()
            if token and token.type == 'OPERATOR' and token.value in ('*', '/'):
                op = token.value
                self.advance()
                right = self.factor()
                node = BinOp(node, op, right)
            else:
                break
        return node

    def factor(self):
        token = self.current_token()
        if token.type == 'NUMBER':
            self.advance()
            return Number(int(token.value))
        elif token.type == 'IDENTIFIER':
            self.advance()
            return Identifier(token.value)
        elif token.type == 'STRING':
            self.advance()
            return String(token.value)
        elif token.type == 'LPAREN':
            self.advance()
            node = self.expression()
            self.expect('RPAREN')
            return node
        else:
            raise SyntaxError(f"Unexpected token in expression: {token}")

    def parse_arguments(self):
        args = []
        token = self.current_token()
        if token.type == 'RPAREN':
            self.advance()  # закриваємо скобку
            return args
        while True:
            arg = self.expression()
            args.append(arg)
            token = self.current_token()
            if token.type == 'RPAREN':
                self.advance()
                break
            elif token.type == 'OPERATOR' and token.value == ',':
                self.advance()
            else:
                raise SyntaxError(f"Unexpected token in argument list: {token}")
        return args

    def parse_param_list(self):
        params = []
        token = self.current_token()
        if token.type == 'RPAREN':
            return params  # пустий список параметрів
        while True:
            param_token = self.expect('IDENTIFIER')
            params.append(param_token.value)
            token = self.current_token()
            if token.type == 'RPAREN':
                break
            elif token.type == 'OPERATOR' and token.value == ',':
                self.advance()
            else:
                raise SyntaxError(f"Unexpected token in parameter list: {token}")
        return params