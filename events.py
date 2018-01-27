"""
Ce module implémente des classes servant pour faire une gestion d'évènements.
"""
from typing import List, Callable, Any
import logging

_logger = logging.getLogger(__name__)


class Event:
    """Classe évènement.

    Cette classe stocke des fonctions à appeler quand l'évènement est appelé.
    """

    def __init__(self):
        self._callbacks = []

    def add_listener(self, fun: Callable):
        """Ajoute la fonction fun à la liste des callbacks."""
        self._callbacks.append(fun)

    def remove_listener(self, fun: Callable):
        """Enlève la fonction fun à la liste des callbacks."""
        self._callbacks.remove(fun)

    def call(self):
        """Appelle chacun de ses callbacks."""
        _logger.debug(f"Event Call at {id(self)}")
        for f in self._callbacks:
            f()

    def __call__(self):
        """Appelle chacun de ses callbacks."""
        return self.call()

    def __iadd__(self, fun: Callable):
        """Raccourci pour `add_listener`."""
        return self.add_listener(fun)

    def __isub__(self, fun: Callable):
        """Raccourci pour `remove_listener`."""
        return self.remove_listener(fun)

    def __repr__(self):
        return f"Event({self._callbacks})"

    def __str__(self):
        return f"Event with {len(self._callbacks)} callbacks."


class StoredFunc:
    """
    Classe de fonctions mises en cache avec évaluation que lors si un
    évènement a été appelé depuis la dernière exécution.

    Ces fonctions ne prennent pas d'arguments.

    Cette classe a deux évènements :
    * :attr:`changed` quand la valeur calculée du paramètre a changé
    * :attr:`cache_cleared` quand un des évènements dont elle dépend a été
      appelé.
    """

    stored = False
    res = None

    def __init__(self, fun: Callable, event_list: List[Event]) -> None:
        """
        :param function fun: la fonction à décorer
        :param event_list: la liste d'évènements à surveiller
        :type event_list: List[Event]
        """
        super().__init__()
        self.fun = fun
        self.changed = Event()
        self.cache_cleared = Event()
        self.__doc__ = fun.__doc__
        self.__name__ = fun.__name__

        for e in event_list:
            e.add_listener(self.cache_clear)

    def cache_clear(self):
        self.stored = False
        self.res = None
        self.cache_cleared.call()

    def __call__(self):
        if not self.stored:
            self.res = self.fun()
            self.stored = True
            self.changed.call()
        return self.res


def store_until_events(event_list: List[Event]):
    """
    Decorator transformant la fonction en `StoredFunc`

    :param event_list: la liste des évènements à surveiller
    :type event_list: List[Event]
    :return: la fonction décorée en `StoredFunc`
    :rtype: StoredFunc
    """

    def decorator(fun: Callable):
        return StoredFunc(fun, event_list)

    return decorator


class Master:
    """Objet Maître du couple maître esclave.

    .. attribute:: value
        :annotation:

        C'est une propriété qui quand elle change de valeur est reprise par
        chaque esclave.

    .. attribute:: changed
        :annotation: `Event`

        C'est l'évènement appelé quand il change de valeur.

    """
    def __init__(self, value: Any):
        self._value = value
        self.changed = Event()

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value
        self.changed.call()


class Slave:
    """Objet Esclave du couple Maître/Esclave.

    Remarquons qu'on peut parfaitement utiliser un `Slave` comme Master d'un
    autre Slave...

    .. attribute:: value
        :annotation:

        C'est une propriété qui quand elle change de valeur chez le maître est
        reprise ici.

    .. attribute:: changed
        :annotation: `Event`

        C'est l'évènement appelé quand il change de valeur.
    """

    def __init__(self, master: Master):
        self.value = master.value
        self.master = master
        self.changed = Event()

        master.changed.add_listener(self.change_value)

    def change_value(self):
        self.value = self.master.value
        self.changed.call()


class SlaveFloat(Slave):

    def __init__(self, master: Master):
        super().__init__(master)
        self.value = float(self.value)

    def __float__(self):
        return self.value


class SlaveInt(Slave):

    def __init__(self, master: Master):
        super().__init__(master)
        self.value = int(self.value)

    def __int__(self):
        return self.value


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    m = Master(3.2)

    s = Slave(m)

    print("m", m.value)
    print("s", s.value)
    m.value = -45.3
    print("m", m.value)
    print("s", s.value)