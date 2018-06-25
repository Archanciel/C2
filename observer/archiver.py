from observer.observer import Observer


class Archiver(Observer):
    def update(self, data):
        print(data)