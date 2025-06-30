# interpretator.py
from parser import Program, WriteStatement, Number, String, Identifier, Assignment, BinOp

class Interpreter:
    def __init__(self):
        self.functions = {}  # Збереження визначених функцій
        self.variables = {}

    def execute(self, program):
        # program — це об’єкт класу Program
        return self.visit(program)

    def visit(self, node):
        node_type = type(node).__name__
        method_name = 'visit_' + node_type
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        raise Exception(f"Unknown node type: {type(node)}")

    def visit_Program(self, node):
        for stmt in node.statements:
            self.visit(stmt)

    def visit_WriteStatement(self, node):
        val = self.visit(node.expression)
        print(val)

    def visit_Number(self, node):
        return node.value

    def visit_String(self, node):
        return node.value

    def visit_Identifier(self, node):
        if node.name in self.variables:
            return self.variables[node.name]
        else:
            raise Exception(f"Undefined variable {node.name}")

    def visit_Assignment(self, node):
        val = self.visit(node.expression)
        self.variables[node.identifier.name] = val
        return val

    def visit_BinOp(self, node):
        left = self.visit(node.left)
        right = self.visit(node.right)
        if node.op == '+':
            return left + right
        elif node.op == '-':
            return left - right
        elif node.op == '*':
            return left * right
        elif node.op == '/':
            return left / right

    def visit_IfStatement(self, node):
        condition = self.visit(node.condition)
        if condition:
            for stmt in node.body:
                self.visit(stmt)

    def visit_FuncDef(self, node):
        # Зберігаємо функцію для подальшого виклику
        self.functions[node.name] = node

    def visit_FuncCall(self, node):
        func = self.functions.get(node.name)
        if not func:
            raise Exception(f"Undefined function {node.name}")
        if len(func.params) != len(node.args):
            raise Exception(f"Function {node.name} expects {len(func.params)} arguments, got {len(node.args)}")

        # Створюємо локальний контекст змінних
        local_vars_backup = self.variables.copy()

        # Обчислюємо аргументи
        args_values = [self.visit(arg) for arg in node.args]
        for param_name, arg_val in zip(func.params, args_values):
            self.variables[param_name] = arg_val

        # Виконуємо тіло функції
        for stmt in func.body:
            self.visit(stmt)

        # Відновлюємо глобальні змінні після виконання функції
        self.variables = local_vars_backup