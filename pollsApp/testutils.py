import faker
from django.contrib.auth import get_user_model

User = get_user_model()


class BaseFaker(faker.Faker):
    def user(self, username: str = None, password: str = None, email: str = None, save=True):
        user = User(
            username=username or self.user_name(),
            email=email or self.email()
        )
        user.set_password(password or "userpass")
        if save:
            user.save()
        return user

    def user_bulk(self, n: int):
        users = [self.user(save=False) for _ in range(n)]
        return User.objects.bulk_create(users)


f = BaseFaker()
