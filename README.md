# monad_comprehension.py

monad_comprehension.py enables you to perform monadic computations with the list comprehension syntax, as suggested by [this article](http://blog.sigfpe.com/2012/03/overloading-python-list-comprehension.html). It is powered by [ast transformations](https://docs.python.org/3.7/library/ast.html).

It is known to work with Python 3.6 and above.

# Example: the Maybe monad

Let's define the Maybe monad like this:

```py3
class Maybe(object):

    def __init__(self, value):
        self.value = value

    @classmethod
    def unit(cls, value):
        return cls(value)

    @classmethod
    def nothing(cls):
        return cls(None)

    def is_nothing(self):
        return self.value is None

    def bind(self, f):
        if self.value is None:
            return self
        return f(self.value)

    def map(self, f):
        if self.value is None:
            return self
        new_value = f(self.value)
        return Maybe.unit(new_value)

    def __str__(self):
        if self.is_nothing():
            return f"Nothing"
        return f"Just {self.value}"
```

We can then adapt the semantics of the comprehension syntax with this:
```py3
@monad_comprehension(Maybe)
def f():
    return [
        (x + y)
        for x in Maybe(5)
        for y in Maybe(6)
    ]

f()  # outputs `Just 11`

@monad_comprehension(Maybe)
def g():
    return [
        (x + y)
        for x in Maybe(5)
        for y in Maybe.nothing()
    ]

g()  # outputs `Nothing`
```

# Comprehending an arbitrary monad

You can provide any class which implements `unit` and `bind` methods to the `monad_comprehension`decorator.

# Status of the project

This is still in a very experimental stage, and is probably not ready yet for production use.

# References

This is inspired by this [blog post](http://blog.sigfpe.com/2012/03/overloading-python-list-comprehension.html). Also, this idea of monad comprehension is very similar to [Haskell's do notation](https://en.wikibooks.org/wiki/Haskell/do_notation).

Besides, this is derived for [this talk](http://slides.com/v-perez/pythonic-monads-in-real-life#/) I gave at PyconFR.
