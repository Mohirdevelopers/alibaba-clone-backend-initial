import factory
from product.models import Product
from faker import Faker

fake = Faker()


class ProductFactory(factory.django.DjangoModelFactory):
    """This class will create fake data for Product"""

    class Meta:
        model = Product

    id = factory.Faker('uuid4')
    seller = factory.SubFactory('tests.factories.user_factory.UserFactory')
    category = factory.SubFactory('tests.factories.category_factory.CategoryFactory')
    title = factory.LazyAttribute(lambda o: fake.word())
    description = factory.LazyAttribute(lambda o: fake.text(max_nb_chars=100))
    price = factory.Faker(
        'pydecimal', left_digits=4, right_digits=2, positive=True, min_value=1
    )
    quantity = factory.Faker('pyint', min_value=1, max_value=10)
    created_at = factory.Faker('date_time_this_decade', tzinfo=None)
