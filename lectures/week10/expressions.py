"""Abstract Syntax Trees

=== CSC148 Fall 2018 ===
Department of Computer Science,
University of Toronto

=== Module Description ===
This contains the code from lecture, in which we moved beyond expressions to
more general form of statements. We studied two main extensions:

    - handling variable bindings in an *environment*
    - simple control flow structures
"""
from __future__ import annotations
from typing import Any, Dict, List, Optional, Tuple, Union


class Module:
    """A class representing a full Python program.

    === Attributes ===
    body: A sequence of statements.
    """
    body: List[Statement]

    def __init__(self, body: List[Statement]) -> None:
        """Initialize a new module with the given body."""
        self.body = body

    def evaluate(self) -> None:
        """Execute the statements in this module."""
        env = {}
        for statement in self.body:
            statement.evaluate(env)

    def __str__(self) -> str:
        """Return a string representation of this module."""
        return '\n'.join(str(stmt) for stmt in self.body)


class Statement:
    """An abstract class representing a Python statement.

    We think of a Python statement as being a more general piece of code than a
    single expression, and that can have some kind of "effect".
    """
    def evaluate(self, env: Dict[str, Any]) -> Optional[Any]:
        """Evaluate this statement with the given environment.

        This should have the same effect as evaluating the statement by the
        real Python interpreter.

        Note that the return type here is Optional[Any]: evaluating a statement
        could produce a value (this is true for all expressions), but it might
        only have a *side effect* like mutating `env` or printing something.
        """
        raise NotImplementedError


################################################################################
# Expressions
################################################################################
class Expr(Statement):
    """An abstract class representing a Python expression.

    This subclass is useful even though it adds no additional methods or
    attributes to its superclass, because we use it to *restrict the types of
    expressions that can appear inside other expressions*.

    For example, in a BinOp instance, its left and right attributes must refer
    to *expressions*, and cannot use other forms of statements like assignments.
    """
    pass


class Num(Expr):
    """A numeric constant literal.

    === Attributes ===
    n: the value of the constant
    """
    n: Union[int, float]

    def __init__(self, number: Union[int, float]) -> None:
        """Initialize a new numeric constant."""
        self.n = number

    def evaluate(self, env: Dict[str, Any]) -> Optional[Any]:
        """Return the *value* of this expression.

        The returned value should the result of how this expression would be
        evaluated by the Python interpreter.

        >>> expr = Num(10.5)
        >>> expr.evaluate({})
        10.5
        """
        return self.n  # Simply return the value itself!

    def __str__(self) -> str:
        """Return a string representation of this expression.

        One feature we'll stick with for all Expr subclasses here is that we'll
        want to return a string that is valid Python code representing the same
        expression.

        >>> str(Num(5))
        '5'
        """
        return str(self.n)


class BinOp(Expr):
    """An arithmetic binary operation.

    === Attributes ===
    left: the left operand
    op: the name of the operator
    right: the right operand

    === Representation Invariants ===
    - self.op == '+' or self.op == '*'
    """
    left: Expr
    op: str
    right: Expr

    def __init__(self, left: Expr, op: str, right: Expr) -> None:
        """Initialize a new binary operation expression.

        Precondition: <op> is the string '+' or '*'.
        """
        self.left = left
        self.op = op
        self.right = right

    def evaluate(self, env: Dict[str, Any]) -> Optional[Any]:
        """Return the *value* of this expression.

        The returned value should the result of how this expression would be
        evaluated by the Python interpreter.

        >>> expr = BinOp(Num(10.5), '+', Num(30))
        >>> expr.evaluate({})
        40.5
        """
        left_val = self.left.evaluate(env)
        right_val = self.right.evaluate(env)

        if self.op == '+':
            return left_val + right_val
        elif self.op == '*':
            return left_val * right_val
        else:
            raise ValueError(f'Invalid operator {self.op}')

    def __str__(self) -> str:
        """Return a string representation of this expression.

        One feature we'll stick with for all Expr subclasses here is that we'll
        want to return a string that is valid Python code representing the same
        expression.

        >>> expr = BinOp(Num(10.5), '+', Num(30))
        >>> str(expr)
        '(10.5 + 30)'
        """
        return f'({str(self.left)} {self.op} {str(self.right)})'


class Bool(Expr):
    """A boolean constant literal.

    === Attributes ===
    b: the value of the constant
    """
    b: bool

    def __init__(self, b: bool) -> None:
        """Initialize a new boolean constant."""
        self.b = b

    def evaluate(self, env: Dict[str, Any]) -> Optional[Any]:
        """Return the *value* of this expression.

        The returned value should the result of how this expression would be
        evaluated by the Python interpreter.

        >>> expr = Bool(True)
        >>> expr.evaluate({})
        True
        """
        return self.b

    def __str__(self) -> str:
        """Return a string representation of this expression.

        One feature we'll stick with for all Expr subclasses here is that we'll
        want to return a string that is valid Python code representing the same
        expression.

        >>> str(Bool(True))
        'True'
        """
        return str(self.b)


class Name(Expr):
    """A variable name.

    === Attributes ===
    id: The variable name in this expression.
    """
    id: str

    def __init__(self, id_: str) -> None:
        self.id = id_

    def __str__(self) -> str:
        """Return a string representation of this comparison expression.

        >>> expr = Name('x')
        >>> str(expr)
        'x'
        """
        return self.id

    def evaluate(self, env: Dict[str, Any]) -> Optional[Any]:
        """Return the *value* of this expression.

        The returned value should the result of how this expression would be
        evaluated by the Python interpreter.

        The name should be looked up in the `env` argument to this method.
        Raise a NameError if the name is not found.

        >>> expr = Name('x')
        >>> expr.evaluate({'x': 10})
        10
        """
        if self.id in env:
            return env[self.id]
        else:
            raise NameError


class Print(Expr):
    """An expression representing a call to the `print` function.

    === Attributes ===
    argument: The argument expression to the `print` function.
    """
    argument: Expr

    def __init__(self, argument: Expr) -> None:
        self.argument = argument

    def __str__(self) -> str:
        """Return a string representation of this statement."""
        return f'print({str(self.argument)})'

    def evaluate(self, env: Dict[str, Any]) -> Optional[None]:
        """Evaluate this statement.

        This evaluates the argument of the print call, and then actually
        prints it. Note that it doesn't return anything, since `print` doesn't
        return anything.
        """
        print(self.argument.evaluate(env))


################################################################################
# Assignment statements
################################################################################
class Assign(Statement):
    """An assignment statement (with a single target).

    === Attributes ===
    target: the variable name on the left-hand side of the equals sign
    value: the expression on the right-hand side of the equals sign
    """
    target: str
    value: Expr

    def __init__(self, target: str, value: Expr) -> None:
        self.target = target
        self.value = value

    def __str__(self) -> str:
        """Return a string representation of this statement."""
        return f'{self.target} = {self.value}'

    def evaluate(self, env: Dict[str, Any]) -> None:
        """Evaluate this statement.

        This does the following: evaluate the right-hand side expression,
        and then update <env> to store a binding between this statement's
        target and the corresponding value.

        >>> stmt = Assign('x', BinOp(Num(10), '+', Num(3)))
        >>> env = {}
        >>> stmt.evaluate(env)
        >>> env['x']
        13
        """
        # Remember to call `evaluate` and pass in `env` here! (Why?)
        env[self.target] = self.value.evaluate(env)


class ParallelAssign(Statement):
    """A parallel assignment statement.

    === Attributes ===
    targets: the variable names being assigned to---the left-hand side of the =
    values: the expressions being assigned---the right-hand side of the =
    """
    targets: List[str]
    values: List[Expr]

    def __init__(self, targets: List[str], values: List[Expr]) -> None:
        self.targets = targets
        self.values = values

    def __str__(self) -> str:
        """Return a string representation of this statement."""
        targets_str = ', '.join(self.targets)
        values_str = ', '.join([str(v) for v in self.values])

        return f'{targets_str} = {values_str}'

    def evaluate(self, env: Dict[str, Any]) -> None:
        """Evaluate this statement.

        This does the following: evaluate each expression on the right-hand side
        and then bind each target to its corresponding expression.

        Raise a ValueError if the lengths of self.targets and self.values are
        not equal.

        >>> stmt = ParallelAssign(['x', 'y'],
        ...                       [BinOp(Num(10), '+', Num(3)), Num(-4.5)])
        >>> env = {}
        >>> stmt.evaluate(env)
        >>> env['x']
        13
        >>> env['y']
        -4.5
        """
        if len(self.targets) != len(self.values):
            raise ValueError

        new_env = {}
        for i in range(len(self.targets)):
            target = self.targets[i]
            value = self.values[i].evaluate(env)

            # THIS IS INCORRECT: if we update `env` here, the *new* value of
            # "target" will be used in subsequent evaluations, rather than the
            # original value.
            # env[target] = value

            # Instead, we save the new value in a temporary dictionary,
            # so that env is not updated inside the loop.
            new_env[target] = value

        # Here, we update the environment with the values stored in new_env.
        for target, value in new_env.items():
            env[target] = value


################################################################################
# Control flow structures
################################################################################
class If(Statement):
    """An if statement.

    This is a statement of the form:

        if <test>:
            <body>
        else:
            <orelse>

    === Attributes ===
    test: The condition expression of this if statement.
    body: A sequence of statements to evaluate if the condition is true.
    orelse: A sequence of statements to evaluate if the condition is false.
            (This would be empty in the case that there is no `else` block.)
    """
    test: Expr
    body: List[Statement]
    orelse: List[Statement]

    def __init__(self, test: Expr, body: List[Statement],
                 orelse: List[Statement]) -> None:
        self.test = test
        self.body = body
        self.orelse = orelse

    def evaluate(self, env: Dict[str, Any]) -> None:
        """Evaluate this statement.

        >>> stmt = If(Bool(True),
        ...           [Assign('x', Num(1))],
        ...           [Assign('y', Num(0))])
        ...
        >>> env = {}
        >>> stmt.evaluate(env)
        >>> env
        {'x': 1}
        """
        test_val = self.test.evaluate(env)
        if test_val:
            for statement in self.body:
                statement.evaluate(env)
        else:
            for statement in self.orelse:
                statement.evaluate(env)


class ForRange(Statement):
    """A for loop that loops over a range of numbers.

        for <target> in range(<start>, <stop>):
            <body>

    === Attributes ===
    target: The loop variable.
    start: The start for the range (inclusive).
    stop: The end of the range (this is *exclusive*, so <stop> is not included
          in the loop).
    body: The statements to execute in the loop body.
    """
    target: str
    start: Expr
    stop: Expr
    body: List[Statement]

    def __init__(self, target: str, start: Expr, stop: Expr,
                 body: List[Statement]) -> None:
        self.target = target
        self.start = start
        self.stop = stop
        self.body = body

    def evaluate(self, env: Dict[str, Any]) -> None:
        """Evaluate this statement.

        Raise a TypeError if either the start or stop expressions do *not*
        evaluate to integers. (This is technically a bit stricter than real
        Python.)

        >>> statement = ForRange('x', Num(1), BinOp(Num(2), '+', Num(3)),
        ...                      [Print(Name('x'))])
        >>> statement.evaluate({})
        1
        2
        3
        4
        """
        start_val = self.start.evaluate(env)
        stop_val = self.stop.evaluate(env)
        if not isinstance(start_val, int) or not isinstance(stop_val, int):
            raise TypeError

        for i in range(start_val, stop_val):
            env[self.target] = i  # Try commenting out this line. What happens?
            for statement in self.body:
                statement.evaluate(env)


if __name__ == '__main__':
    import doctest
    doctest.testmod()

    # import python_ta
    # python_ta.check_all()
