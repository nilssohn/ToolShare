"""

    @author Nils Sohn

"""
from class_fixtures.models import Fixture
from registration.models import ShareZone, User

# Create Class Fixtures for User and Share Zone
user_l = Fixture(User)
zones = Fixture(ShareZone)

# Add an instance of a Share Zone to the Fixture
# Add the Share Zone into the User Fixture with other details
zones.add(1, zone = "14623")
user_l.add(
        1,
        first_name="Tall",
        last_name="Paul",
        email="Tall@Paul.com",
        password="12345678",
        zipcode="14623",
        pick_up="My house",
        my_zone=zones.fk(1),
        question1="What is your mother's maiden name?",
        answer1="I'm adopted",
        question2="Where did your parents meet?",
        answer2="My dad was a sperm doner"
    )