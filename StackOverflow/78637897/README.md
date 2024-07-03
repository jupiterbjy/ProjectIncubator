This is written in assumption that you meant to implement `typing.Sequence` protocol, not directly inherit from `numpy.ndarray` as it doesn't need any overrides anyway.


# Similarity - Operator Overloading

Assuming that you're from C++ base, I think it'll be better starting with similar concept. Here's operator overloading example.

```cpp
#include <iostream>


class SomeSequence {
public:
    void operator[](size_t idx) {
        std::cout << "operator[] called with " << idx << std::endl;
    }
};


int main() {
    SomeSequence seq;
    
    // This work
    seq[0];

    // ... but this work too!
    seq.operator[](1);
}
```

<!-- Language: lang-none -->
```
operator[] called with 0
operator[] called with 1
```

We obviously can use operator `[]` but also we can directly use `.operator[]()` member function.

Those methods that starts & ends with double underscore like `__getitem__` in Python is similar(or even identical this case).

Such methods are called *dunder method*. (Shorthand for double underscore)

```python
class SomeSequence:
    def __getitem__(self, index):
        print(f"__getitem__ called with {index}")


def main():
    seq = SomeSequence()

    seq[0]
    seq.__getitem__(1)


if __name__ == "__main__":
    main()
```

<!-- Language: lang-none -->
```
__getitem__ called with 0
__getitem__ called with 1
```

---

<br>

# Answer

So no, `numpy.ndarray.abs()` (which I assume what you mean by `numpy.abs()`)  ain't dunder method, it's just like adding `SomeArray SomeSequence::abs()` member function which doesn't magically carry over to other independent class.

However python goes one step further than simple operator overloading, which is part you were reading.

---

<br>

# Protocols, and [Duck Typing](https://docs.python.org/3/glossary.html#term-duck-typing)

Let's start with a touching story I just made up:

> Guido's walking down the street, and saw dark silhouette rushing toward at him. 
> 
> In tense moment, he starts analyzing the potential threat;  
> He realises that it quacks like a duck, and waddles like a duck.
> 
> By analyzing it's traits, he quickly concludes that it must be a duck or at least expected to continue behaving like one, which means it's next move is biting his beloved left leg.


... and let me translate it a bit.
```python
>>> unknown_threat = UnknownThreat()

>>> unknown_threat.quack()
Quaaack!

>>> unknown_threat.waddle()
(It waddles towards you menacingly.)
```

We don't know what `UnknownThreat` class is, but by looking at it implementing the `.quack()` and `.waddle()` methods(interface), it satisfies our Duck requirements, and will behave like one regardless of what class it is.

```python
class UnknownThreat:
    """We don't know what this is, but looks menancing."""

    def quack(self):
        print("Quaaack!")
    
    def waddle(self):
        print("(It waddles towards you menacingly.)")

```

<br>

Such seems possible with Interface Class, but Interface classes differ that it *ENFORCE* you to implement it;

```cpp
class DuckInterface {
    virtual void quack() = 0;
    virtual void waddle() = 0;
}
```

```python
class DuckInterface:
    """Enforce the implementation of duckiness."""

    def quack(self):
        raise NotImplemented
    
    def waddle(self):
        raise NotImplemented
```

<br>

...Meanwhile *Duck-Typing* doesn't!

```cpp
#include <iostream>

class DuckProtocol {
public:
    void (*quack)() = nullptr;
    void (*waddle)() = nullptr;
};


// using inheritance here because of static typing
class UnknownThreat : public DuckProtocol {
public:
    UnknownThreat() {
        quack = []() { std::cout << "Quaaack!" << std::endl; };
        waddle = []() { std::cout << "(It waddles towards you menacingly.)" << std::endl; };
    }
};
```

```python
class DuckProtocol:
    def quack(self):
        pass

    def waddle(self):
        pass


class UnknownThreat:
    def quack(self):
        print("Quaaack!")

    def waddle(self):
        print("(It waddles towards you menacingly.)")


unknown_threat = UnknownThreat()
```

<br>

Likewise, python defines specific sets of *Special names* that python internals will [*try on*](https://docs.python.org/3/glossary.html#term-EAFP) - which are dunder methods.

Python (mostly) doesn't care what class an object is! If it act like a duck, it gotta be a duck.


```python
def auto_quacker_9000(entity):
    """Professional function to make the quack out of given entity"""
    
    try:
        entity.quack()
        
    except AttributeError:
        print("I don't think it's a duck...")


auto_quacker_9000(unknown_threat)
auto_quacker_9000("not a duck")
```

<!-- Language: lang-none -->
```
Quaaack!
I don't think this is a duck...
```


And that's the core part of *Emulating Container*! If something implements required set of dunder methods, it is a valid container and python will happily accept it.

```
>>> class SomeContainer:
...     def __getitem__(self, idx):
...         if idx < 5:
...             return idx
...         raise IndexError
... # For this class iteration will continue until IndexError

>>> cont = SomeContainer()
>>> for n in cont :
...     print(n)
0
1
2
3
4

>>> print(*cont)
0 1 2 3 4

>>> cont[4]
4
```

So, if you know what your emulated container needs, you only need to implement those, with some help of [Official Docs for datamodel](https://docs.python.org/3/reference/datamodel.html#sequences) identifying required methods, or can inherite interface from `collections.abc` to enforce it.