from app.modules import Display



class Vue:
    _events_queue: set[str] = set()
    _binded_events: dict = {}

    def _logic_loop(self) -> None:
        """
        Put vue logic here. Runs every app tick.
        """
        pass

    def _listen_events(self) -> None:
        """
        Listen to event queue and trigger actions
        """
        for event in self._events_queue:
            actions = self._binded_events.get(event, [])
            for a in actions:
                a()

        self._events_queue.clear()

    def bind(self, event: str, action: "Callable") -> None:
        """
        Bind an action on event

        Args:
            event (str): Event to listen
            action (Callable): Function to call on trigger
        """
        try:
            self._binded_events[event].append(action)
        except KeyError:
            self._binded_events[event] = [action]
    
    def dispatch(self, event: str) -> None:
        """
        Dispatch an event

        Args:
            event (str): Event to dispatch
        """
        self._events_queue.add(event)

    def update(self) -> None:
        """
        Update the vue content
        """
        self._listen_events()
        self._logic_loop()

    def load(self, display: Display) -> None:
        """
        Init / load vue
        """
        raise NotADirectoryError("'Vue.load' method should implemented to specify how to init the vue.")


