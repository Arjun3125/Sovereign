class DoctrineRegistry:
    def __init__(self):
        self._doctrines = {}

    def register(self, doctrine_view):
        self._doctrines[doctrine_view.doctrine_id] = doctrine_view

    def get(self, doctrine_id):
        return self._doctrines.get(doctrine_id)

    def list_all(self):
        return list(self._doctrines.keys())
