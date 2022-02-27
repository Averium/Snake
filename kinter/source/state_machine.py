from abc import ABC, abstractmethod


class State(ABC):

    """
    Abstract class for game states. Subclass this to create new game states
    """

    def __init__(self, name, state_machine):
        self.name = name
        self.state_machine = state_machine

    @abstractmethod
    def check_conditions(self) -> (str, None):
        """
        State transitions with their conditions should be implemented here
        :returns: name of the next state for transition, or None for no transition
        """
        pass

    def entry_actions(self):
        """ This method is called each time when the state is entered """
        pass

    def exit_actions(self):
        """ This method is called each time when the state is left """
        pass

    def events(self, *args, **kwargs) -> None:
        """ Implement state specific event handling here """
        pass

    def logic(self, *args, **kwargs) -> None:
        """ Implement state specific game logic here """
        pass

    def render(self, *args, **kwargs) -> None:
        """ Implement state specific rendering here """
        pass


class StateMachine(ABC):

    """ Base class for a state machine based game framework, which handles State objects """

    def __init__(self, initial: State) -> None:
        self.initial = initial.name
        self._states = {}
        self.add_state(initial)
        self._active = initial
        self._last = initial
        initial.entry_actions()

    def add_state(self, *states: State) -> None:
        """ Adds a new state to the state machine (call this in __init__ methods only) """
        for state in states:
            self._states[state.name] = state

    @property
    def current_state(self) -> str:
        """ returns: name of the current state """
        return self._active.name

    @property
    def last_state(self) -> State:
        """ returns: name of the current state """
        return self._last.name

    @current_state.setter
    def current_state(self, name: str) -> None:
        """ Executes proper change between states """
        self._active.exit_actions()
        self._last = self._active
        self._active = self._states[name]
        self._active.entry_actions()
        print(f"CURRENT STATE: {name}")

    def update_states(self) -> None:
        """ Method for handling state actions, and state transitions """
        if (new_state := self._active.check_conditions()) is not None:
            self.current_state = new_state

    def state_events(self, *args, **kwargs): self._active.events(*args, **kwargs)
    def state_logic(self, *args, **kwargs): self._active.logic(*args, **kwargs)
    def state_render(self, *args, **kwargs): self._active.render(*args, **kwargs)
