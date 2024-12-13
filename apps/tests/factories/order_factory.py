import factory
from uuid import uuid4
from faker import Faker
from tests.factories.user_factory import fake_number

fake = Faker()


class OrderFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'order.Order'

    id = factory.LazyFunction(uuid4)
    user = factory.SubFactory('tests.factories.user_factory.UserFactory')
    payment_method = 'card'
    status = 'pending'
    address_line_1 = factory.LazyAttribute(lambda o: fake.address())
    address_line_2 = factory.LazyAttribute(lambda o: fake.address())
    city = factory.LazyAttribute(lambda o: fake.city())
    state_province_region = factory.LazyAttribute(lambda o: fake.state())
    postal_zip_code = factory.LazyAttribute(lambda o: fake.zipcode())
    country_region = factory.LazyAttribute(lambda o: fake.country())
    telephone_number = factory.LazyAttribute(lambda o: fake_number())


class OrderItemFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'order.OrderItem'

    id = factory.LazyFunction(uuid4)
    order = factory.SubFactory('tests.factories.order_factory.OrderFactory')
    product = factory.SubFactory('tests.factories.product_factory.ProductFactory')
    quantity = factory.Faker('pyint', min_value=1, max_value=10)
    price = factory.Faker(
        'pydecimal', left_digits=4, right_digits=2, positive=True, min_value=1
    )
