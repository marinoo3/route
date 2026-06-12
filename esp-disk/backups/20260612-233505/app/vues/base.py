from app.models import Event

TYPE_CHECKING = False
if TYPE_CHECKING:
    from app.modules import Display



class EventHandler:
    def __init__(self, action: "Callable", once: bool) -> None:
        self.action = action
        self.once = once

class Vue:
    _events_queue: list[Event] = []
    _binded_events: dict[str, EventHandler] = {}

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
            handler = self._binded_events.get(event.name)
            if not handler:
                continue

            handler.action(**event.data)
            if handler.once:
                self._binded_events.pop(event.name)

        self._events_queue.clear()

    def bind(
            self, 
            event: str, 
            action: "Callable", 
            once: bool = False
        ) -> None:
        """
        Bind an action on event

        Args:
            event (str): Event to listen
            action (Callable): Function to call on trigger
            once (bool): Remove event from binded list after being triggered
        """
        self._binded_events[event] = EventHandler(action=action, once=once)
    
    def dispatch(self, event: Event) -> None:
        """
        Dispatch an event

        Args:
            event (str): Event to dispatch
        """
        self._events_queue.append(event)

    def update(self) -> None:
        """
        Update the vue content
        """
        self._listen_events()
        self._logic_loop()

    def load(self, display: "Display") -> None:
        """
        Init / load vue
        """
        raise NotImplementedError("'Vue.load' method should implemented to specify how to init the vue.")


