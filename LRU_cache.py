from collections import OrderedDict


class LRUCache:
    def __init__(self, capacity: int):
        self.stack = OrderedDict()
        self.capacity = capacity

    def get(self, key):
        if key in self.stack:
            self.stack.move_to_end(key)
            return self.stack[key]
        else:
            return None

    def put(self, key, value) -> None:
        if key in self.stack:
            self.stack[key] = value
            self.stack.move_to_end(key)
        else:
            self.stack[key] = value
        if len(self.stack) > self.capacity:
            self.stack.popitem(last=False)

    def delete(self, key):
        self.stack.pop(key)

    def clear(self):
        self.stack.clear()

    def __contains__(self, key):
        return key in self.stack


if __name__ == '__main__':
    cache = LRUCache(3)

    cache.put('0', 1)
    cache.put('1', 1)
    cache.put('2', 1)
    cache.clear()
    print(cache.stack)
