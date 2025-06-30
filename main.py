from lexer import tokenize
from parser import Parser
from interpretator import Interpreter

def run_mrscript(source_code):
    tokens = tokenize(source_code)

    parser = Parser(tokens)
    ast = parser.parse()

    interpreter = Interpreter()
    interpreter.execute(ast)

if __name__ == "__main__":
    path = input("Enter path to MS File: ")
    try:
        with open(path, "r", encoding="utf-8") as file:
            source = file.read()
        run_mrscript(source)
    except FileNotFoundError:
        print(f"File not found: {path}")
    except Exception as e:
        print(f"Error: {e}")
