from starlette.authentication import BaseUser


class User(BaseUser):
    def __init__(self, username: str, name: str) -> None:
        self.username = username
        self.name = name

    @property
    def is_authenticated(self) -> bool:
        return True

    @property
    def display_username(self) -> str:
        return self.username

    @property
    def display_fullname(self) -> str:
        return self.name