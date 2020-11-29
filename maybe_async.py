import ast
import asyncio
import functools
import inspect
import textwrap


class Transformer(ast.NodeTransformer):
    def visit_Call(self, node):
        return ast.Yield(value=node)


def _make_generator(func):
    filename = inspect.getsourcefile(func)
    lines, offset = inspect.getsourcelines(func)
    source = textwrap.dedent('\n'.join(lines))

    tree = ast.parse(source)
    tree = Transformer().visit(tree)
    tree = ast.fix_missing_locations(tree)
    tree = ast.increment_lineno(tree, offset - 1)

    code = compile(tree, filename or '<string>', 'exec')

    ns = func.__globals__
    if func.__closure__ is not None:
        ns.update({
            name: cell.cell_contents for name, cell in
            zip(func.__code__.co_freevars, func.__closure__)
        })

    ns['__bypass_decorator'] = True
    exec(code, ns)
    del ns['__bypass_decorator']
    return ns[func.__name__]


def maybe_async(func):
    if '__bypass_decorator' in func.__globals__:
        return func

    if not (
        inspect.isroutine(func) and
        not inspect.iscoroutinefunction(func) and
        not inspect.isgeneratorfunction(func) and
        not inspect.isasyncgenfunction(func)
    ):
        raise ValueError('Only a normal function allowed')

    gen_func = _make_generator(func)

    async def async_executor(gen, val):
        while True:
            if inspect.isawaitable(val):
                val = await val
            try:
                val = gen.send(val)
            except StopIteration as exc:
                return exc.value

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        gen = gen_func(*args, **kwargs)
        if not inspect.isgenerator(gen):
            return gen

        val = None
        while True:
            try:
                val = gen.send(val)
                if inspect.isawaitable(val):
                    return async_executor(gen, val)
            except StopIteration as exc:
                return exc.value

    return wrapper
