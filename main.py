import re

# CONSTANTS

DIGITS = '0123456789'
UALPHA = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
LALPHA = UALPHA.lower()
KEYWORDS = ['balik', 'bool', 'des', 'desimal', 'doble', 'int', 'integro', 'ipakita', 'kar', 'karakter', 'kundi', 'kung',
            'pangungusap', 'para', 'pasok', 'tigil', 'walangbalik']
RESWORDS = ['mali', 'magpatuloy', 'pumuntasa', 'simula', 'tama']
ARITHMETIC_OP = []


# ERRORS

class Error:
    def __init__(self, pos_start, pos_end, error_name, details):
        self.pos_start = pos_start
        self.pos_end = pos_end
        self.error_name = error_name
        self.details = details

    def as_string(self):
        result = f'{self.error_name}: {self.details}\n'
        result += f'File {self.pos_start.fn}, line {self.pos_start.ln + 1}'
        return result


class IllegalCharError(Error):
    def __init__(self, pos_start, pos_end, details):
        super().__init__(pos_start, pos_end, 'Illegal Character', details)


# POSITION

class Position:
    def __init__(self, idx, ln, col, fn, ftxt):
        self.idx = idx
        self.ln = ln
        self.col = col
        self.fn = fn
        self.ftxt = ftxt

    def advance(self, current_char):
        self.idx += 1
        self.col += 1

        if current_char == '\n':
            self.ln += 1
            self.col = 0

        return self

    def copy(self):
        return Position(self.idx, self.ln, self.col, self.fn, self.ftxt)


# TOKENS

# arithmetic
inte = 'int'
flt = 'float'
add = '+'
sub = '-'
mul = '*'
div = '/'
mod = '%'
exp = ':'

# relational
eq_to = '=='
not_eq = '!='
l_than = '<'
l_eq = '<='
g_than = '>'
g_eq = '>='

# logical
l_and = '@'
l_or = '//'
nt = '~'

# assignment
assgn = '='
add_assgn = '+='
sub_assgn = '-='
mul_assgn = '*='
div_assgn = '/='

# unary
inc = '++'
dec = '--'

# comments
s_com = '^'
m_com_open = '^~'
m_com_close = '~^'

# delimiters
l_par = '('
r_par = ')'

# delimiters
semi_colon = ';'
left_bracket = '['
right_bracket = ']'
simula = 'simula'
wakas = 'wakas'
double_quotes = 'String'


class Token:
    def __init__(self, type_, value=None):
        self.type = type_
        self.value = value

    def __repr__(self):
        if self.value: return f'{self.type}:{self.value}'
        return f'{self.type}'


# LEXER


class Lexer:
    def __init__(self, fn, text):
        self.fn = fn
        self.text = text
        self.pos = Position(-1, 0, -1, fn, text)
        self.current_char = None
        self.advance()

    def advance(self):
        self.pos.advance(self.current_char)
        self.current_char = self.text[self.pos.idx] if self.pos.idx < len(self.text) else None

    def make_tokens(self):
        tokens = []

        while self.current_char != None:
            if self.current_char in ' \t':
                self.advance()
            elif self.current_char in DIGITS:
                tokens.append(self.digit())
            elif self.current_char in UALPHA + LALPHA:
                tokens.append(self.str())
            elif self.current_char == '+':
                self.advance()
                if self.current_char == '+':
                    tokens.append(Token(inc))
                    self.advance()
                elif self.current_char == '=':
                    tokens.append(Token(add_assgn))
                    self.advance()
                else:
                    tokens.append(Token(add))  # napaltan ko
                    self.advance()
            elif self.current_char == '-':
                self.advance()
                if self.current_char == '-':
                    tokens.append(Token(dec))
                    self.advance()
                elif self.current_char == '=':
                    tokens.append(Token(sub_assgn))
                    self.advance()
                else:
                    tokens.append(Token(sub))
                    self.advance()
            elif self.current_char == '*':
                self.advance()
                if self.current_char == '=':
                    tokens.append(Token(mul_assgn))
                    self.advance()
                else:
                    tokens.append(Token(mul))
                    self.advance()
            elif self.current_char == '/':
                self.advance()
                if self.current_char == '=':
                    tokens.append(Token(div_assgn))
                    self.advance()
                elif self.current_char == '/':
                    tokens.append(Token(l_or))
                    self.advance()
                else:
                    tokens.append(Token(div))
                    self.advance()
            elif self.current_char == '(':
                tokens.append(Token(l_par))
                self.advance()
            elif self.current_char == ')':
                tokens.append(Token(r_par))
                self.advance()
            elif self.current_char == '%':
                tokens.append(Token(mod))
                self.advance()
            elif self.current_char == ':':
                tokens.append(Token(exp))
                self.advance()
            elif self.current_char == '=':
                self.advance()
                if self.current_char == '=':
                    tokens.append(Token(eq_to))
                    self.advance()
                else:
                    tokens.append(Token(assgn))
                    self.advance()
            elif self.current_char == '#':
                self.advance()
                keyword = ''
                while self.current_char is not None and (self.current_char in UALPHA or self.current_char in LALPHA):
                    keyword += self.current_char
                    self.advance()
                if keyword.lower() == 'simula':
                    tokens.append(Token('simula'))
                elif keyword.lower() == 'wakas':
                    tokens.append(Token('wakas'))
                else:
                    pos_start = self.pos.copy()
                    char = self.current_char if self.current_char else ''  # Handle None case
                    self.advance()
                    return [], IllegalCharError(pos_start, self.pos, "'" + "Error delimiter" + "'")
            elif self.current_char == '~':
                self.advance()
                if self.current_char == '^':
                    tokens.append(Token(m_com_close))
                    while self.current_char and self.current_char != '\n':
                        self.advance()
                    self.advance()
                else:
                    tokens.append(Token(not_eq))
                    self.advance()
            elif self.current_char == '<':
                self.advance()
                if self.current_char == '=':
                    tokens.append(Token(l_eq))
                    self.advance()
                else:
                    tokens.append(Token(l_than))
                    self.advance()
            elif self.current_char == '>':
                self.advance()
                if self.current_char == '=':
                    tokens.append(Token(g_eq))
                    self.advance()
                else:
                    tokens.append(Token(g_than))
                    self.advance()
            elif self.current_char == '@':
                tokens.append(Token(l_and))
                self.advance()
            elif self.current_char == '^':
                self.advance()
                if self.current_char == '~':
                    tokens.append(Token(m_com_open))
                    # Ignore characters until '~^' for multi-line comments
                    while self.current_char and not (self.current_char == '~' and self.peek() == '^'):
                        self.advance()
                    self.advance()  # Move past the closing '~'
                    self.advance()  # Move past the '^'
                else:
                    pos_start = self.pos.copy()
                    char = self.current_char
                    comment_text = ''
                    while self.current_char and self.current_char != '\n':
                        comment_text += self.current_char
                        self.advance()
                    tokens.append(Token(s_com, comment_text.strip()))
            elif self.current_char == ';':
                tokens.append(Token(semi_colon))
                self.advance()
            elif self.current_char == '[':
                tokens.append(Token(left_bracket))
                self.advance()
            elif self.current_char == ']':
                tokens.append(Token(right_bracket))
                self.advance()
            elif self.current_char == '"':
                self.advance()
                str_value = ''
                while self.current_char and self.current_char != '"':
                    str_value += self.current_char
                    self.advance()
                tokens.append(Token(double_quotes, str_value))
                self.advance()
            else:
                pos_start = self.pos.copy()
                char = self.current_char
                self.advance()
                return [], IllegalCharError(pos_start, self.pos, "'" + char + "'")

        return tokens, None

    def digit(self):
        num_str = ''
        dot_count = 0

        while self.current_char != None and self.current_char in DIGITS + '.':
            if self.current_char == '.':
                if dot_count == 1: break
                dot_count += 1
                num_str += '.'
            else:
                num_str += self.current_char
            self.advance()

        if dot_count == 0:
            return Token('int', int(num_str))
        else:
            return Token('float', float(num_str))

    def str(self):
        str = ''
        while self.current_char != None and (self.current_char in UALPHA or self.current_char in LALPHA):
            str += self.current_char
            self.advance()
        if str.lower() in ['imal', 'egro', 'akter']:
            return Token('noise word', str)
        elif str in KEYWORDS:
            return Token('keyword', str)
        elif str in RESWORDS:
            return Token('reserved word', str)
        else:
            return Token('identifier', str)

    def peek(self):
        peek_idx = self.pos.idx + 1
        return self.text[peek_idx] if peek_idx < len(self.text) else None


# RUN

def run(fn, text):
    lexer = Lexer(fn, text)
    tokens, error = lexer.make_tokens()

    return tokens, error

def generate_symbol_table(tokens):
    symbol_table = {}

    for token in tokens:
        if (token.type == 'identifier' or token.type == 'keyword' or token.type == 'reserved word' or
                token.type == 'noise word'):
            lexeme = token.value
            token_type = token.type
            if lexeme not in symbol_table:
                symbol_table[lexeme] = token_type
            else:
                symbol_table[lexeme] += f', {token_type}'
        elif token.type == 'int' or token.type == 'float':
            lexeme = str(token.value)
            token_type = token.type
            if lexeme not in symbol_table:
                symbol_table[lexeme] = token_type
            else:
                symbol_table[lexeme] += f', {token_type}'
        elif token.type in ['+', '-', '*', '/', '%', ':']:
            lexeme = token.type
            token_type = 'arithmetic operator'
            if lexeme not in symbol_table:
                symbol_table[lexeme] = token_type
            else:
                symbol_table[lexeme] += f', {token_type}'
        elif token.type in ['==', '<=', '<=', '>',
                            '>=']:
            lexeme = token.type
            token_type = 'relational operator'
            if lexeme not in symbol_table:
                symbol_table[lexeme] = token_type
            else:
                symbol_table[lexeme] += f', {token_type}'
        elif token.type in ['and', 'or', 'not']:
            lexeme = token.type
            token_type = 'logical operator'
            if lexeme not in symbol_table:
                symbol_table[lexeme] = token_type
            else:
                symbol_table[lexeme] += f', {token_type}'
        elif token.type in ['=', '+=', '-=', '*=',
                            '/=']:
            lexeme = token.type
            token_type = 'assignment operator'
            if lexeme not in symbol_table:
                symbol_table[lexeme] = token_type
            else:
                symbol_table[lexeme] += f', {token_type}'
        elif token.type in ['++', '--']:
            lexeme = token.type
            token_type = 'unary operator'
            if lexeme not in symbol_table:
                symbol_table[lexeme] = token_type
            else:
                symbol_table[lexeme] += f', {token_type}'

        # Add other token types as needed following a similar pattern

    return symbol_table


def visualize_symbol_table(symbol_table, file_name):
    with open(file_name, 'w') as file:
        file.write("Lexeme\t\t\tToken\n")  # Writing headers to the file

        # Write lexemes and tokens into the file in a tabular format
        for lexeme, token in symbol_table.items():
            file.write(f"{lexeme.ljust(15)}\t{token}\n")