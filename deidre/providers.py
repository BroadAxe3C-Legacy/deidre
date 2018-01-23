import random
import string
from collections import defaultdict

from faker.providers.address.en_US import Provider as AddressProvider
from faker.providers.company import Provider as CompanyProvider
from faker.providers.date_time import Provider as DateTimeProvider
from faker.providers.internet import Provider as InternetProvider
from faker.providers.lorem.la import Provider as LoremProvider
from faker.providers.person.en import Provider as PersonProvider
from faker.providers.phone_number import Provider as PhoneProvider


class keydefaultdict(defaultdict):
    def __missing__(self, key):
        if self.default_factory is None:
            raise KeyError(key)
        else:
            ret = self[key] = self.default_factory(key)
            return ret


class RedoxPersonProvider(PersonProvider):
    letters = tuple(string.ascii_lowercase)

    _first_names = defaultdict(list)
    for name in PersonProvider.first_names:
        _first_names[name[0].lower()].append(name)

    _last_names = defaultdict(list)
    for name in PersonProvider.last_names:
        _last_names[name[0].lower()].append(name)

    # add these to the PersonProvider defaults because that list has no
    # last names starting with I or X
    for name in ['Ibrahimovic', 'Iceman', 'Ignaczak',
                 'Xanthopoulos', 'Ximenez', 'Xiao']:
        _last_names[name[0].lower()].append(name)

    first_name_dict = defaultdict(lambda: random.choice(
        RedoxPersonProvider._first_names[
            random.choice(RedoxPersonProvider.letters)]))

    last_name_dict = keydefaultdict(lambda k: random.choice(
        RedoxPersonProvider._last_names[k[0]]))

    def alliterative_first_name(self, name):
        if name is not None:
            return self.first_name_dict[name.lower()]
        return None

    def alliterative_middle_initial(self, _, first_name):
        if first_name is not None:
            return self.last_name_dict[first_name.lower()][0]
        return None

    def alliterative_last_name(self, _, first_name):
        if first_name is not None:
            return self.last_name_dict[first_name.lower()]
        return None


class RedoxRandomProvider(DateTimeProvider,
                          InternetProvider):
    seed = random.random()

    race_options = ('American Indian or Alaska Native', 'Asian',
                    'Black or African American',
                    'Native Hawaiian or Other Pacific Islander',
                    'White')

    def race(self, orig):
        if orig is None or orig == '' or orig == '""':
            return orig
        else:
            return random.choice(self.race_options)

    sex_options = ('Male', 'Female', 'Other')

    def sex(self):
        return random.choice(self.sex_options)

    marital_status_options = ('Married', 'Single', 'Divorced', 'Widowed')

    def marital_status(self):
        return random.choice(self.marital_status_options)

    def bool_or_null(self, chance_of_getting_true=50,
                     chance_of_getting_null=10):
        rand = self.generator.random.randint(1, 100)
        if rand < chance_of_getting_true:
            return True
        elif rand > 100 - chance_of_getting_null:
            return None
        else:
            return False

    def dob(self):
        return self.date_between(start_date="-89y",
                                 end_date="-18y").isoformat()

    # or can use .astimezone().isoformat('T', 'microseconds')
    def event_datetime_last_year(self):
        return self.date_time_between(start_date="-1y").isoformat() + '.000Z'

    def event_datetime_future(self):
        return self.date_time_between(start_date="+1y",
                                      end_date='+5y').isoformat() + '.000Z'

    def identity(self, val):
        if any((isinstance(val, t) for t in
                [str, int, float, bool, type(None)])):
            return val
        raise ValueError(f'identity not allowed on {type(val)} => {val}')

    def none(self):
        return None

    def true(self):
        return True

    def false(self):
        return False

    def number(self):
        return ((990_000 + random.randint(0, 9999)) * 100) + 99

    def integer(self):
        return self.number()

    def id(self, orig):
        if orig is None or orig == '' or orig == '""':
            return orig
        else:
            random.seed(f'{self.seed}{orig}')
            return str(self.number())

    def mrn(self, orig):
        return self.id(orig)


class RedoxPhoneProvider(PhoneProvider):
    def phone(self, orig):
        return self.phone_number() if orig is not None else None


class RedoxAddressProvider(AddressProvider):
    def street_address_or_null(self, orig):
        if orig is None or orig == '' or orig == '""':
            return orig
        else:
            return f'{self.building_number()} {self.street_name()}:' \
                   f'{self.secondary_address()}'

    def city_or_null(self, orig):
        if orig is None or orig == '' or orig == '""':
            return orig
        else:
            return self.city()

    def state_or_null(self, orig):
        if orig is None or orig == '' or orig == '""':
            return orig
        else:
            return self.state()

    def zip_or_null(self, orig):
        if orig is None or orig == '' or orig == '""':
            return orig
        else:
            return self.postalcode()


class RedoxCompanyProvider(CompanyProvider):
    def company_or_null(self, orig):
        return self.company() if orig is not None else None


class RedoxLoremProvider(LoremProvider):
    def lorem(self, orig):
        return self.text(len(orig)) if orig is not None else None

    def lorem_short(self):
        return self.text()
