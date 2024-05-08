import csv
from django.conf import settings
from recipes.models import Ingredient
from django.core.management import BaseCommand


class Command(BaseCommand):
    help = 'Загрузка данных из csv'

    def handle(self, *args, **kwargs):
        with open(
            f'{settings.BASE_DIR}/data/ingredients.csv',
            'r', encoding='utf-8'
        ) as file:
            Ingredient.objects.bulk_create(
                Ingredient(**data) for data in csv.DictReader(file)
            )
        self.stdout.write(self.style.SUCCESS('Данные загружены!'))
