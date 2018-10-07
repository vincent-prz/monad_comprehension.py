import ast
import inspect
from functools import wraps

class ComprehensionTransformer(ast.NodeTransformer):

    def visit_FunctionDef(self, node):
        self.visit(node.body[0])
        node.decorator_list = []
        return node

    def visit_ListComp(self, node):
        def build_call(generators, elt):
            if generators == []:
                return ast.Call(
                    func=ast.Name(id='__unit__', ctx=ast.Load()),
                    args=[node.elt],
                    keywords=[]
                )
            else:
                first_generator, *rest = generators
                return ast.Call(
                    func=ast.Name(id='__bind__', ctx=ast.Load()),
                    args=[
                        first_generator.iter,
                        ast.Lambda(
                            args=ast.arguments(args=[ast.arg(arg=first_generator.target.id, annotation=None)],
                                vararg=None,
                                kwonlyargs=[],
                                kw_defaults=[],
                                kwarg=None,
                                defaults=[]),
                            body=build_call(rest, elt)
                        )
                    ],
                    keywords=[]
                )

        return build_call(node.generators, node.elt)


def monad_comprehension(monad_cls):
    def decorator(f):
        # first, uncompile the code into an ast
        source = inspect.getsource(f)
        tree = ast.parse(source)

        # transform the tree -> replace list comprehension syntax with bind /
        # unit expression
        tree.body[0] = ComprehensionTransformer().visit(tree.body[0])
        ast.fix_missing_locations(tree)

        # recompile it
        code = compile(tree, '', 'exec')
        globs = {
            **f.__globals__,
            '__unit__': monad_cls.unit,
            '__bind__': monad_cls.bind,
        }
        context = {}
        # exec the code: effectively replaces the former implementation of the
        # function
        exec(code, globs, context)
        return context[f.__name__]
    return decorator
