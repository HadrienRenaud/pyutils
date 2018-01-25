"""Module python implémentant une classe Unique qui permet de créer des classes
avec une seule instance."""

import abc
import functools


class StoreInstances(metaclass=abc.ABCMeta):
    """Classe abstraite permettant pour une classe de stocker ses instances.

    Les instances sont stockées dans l'attribut de classe _instances."""

    _instances = []

    def __new__(cls, *args, **kwargs):
        inst = super().__new__(cls)
        cls._instances.append(inst)
        return inst

    def __init_subclass__(cls) -> None:
        cls._instances = []
        super().__init_subclass__()

    def __del__(self):
        type(self)._instances.remove(self)


class Unique(StoreInstances, metaclass=abc.ABCMeta):
    """Classe abstraite ne laissant possible qu'une seule instance de la
    classe."""

    def __new__(cls):
        if len(cls._instances) == 0:
            return super().__new__(cls)
        else:
            return cls._instances[0]


def access_all(fun):
    """Décorateur permettant de transformer une fonction qui a effet sur un
    élément d'un classe en une fonction ayant effet sur tous les éléments de la
    classe."""

    @functools.wraps(fun)
    def new_fun(self, *args, **kwargs):
        return [fun(i, *args, **kwargs) for i in self._instances]

    return classmethod(new_fun)
