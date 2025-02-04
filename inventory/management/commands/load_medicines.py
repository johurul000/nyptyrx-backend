import csv
from django.core.management.base import BaseCommand
from inventory.models import CentralMedicine

class Command(BaseCommand):
    help = 'Load medicines data from CSV file into the database'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Path to the CSV file')

    def handle(self, *args, **kwargs):
        csv_file = kwargs['csv_file']
        try:
            with open(csv_file, newline='', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                medicines = []
                for row in reader:
                    medicines.append(
                        CentralMedicine(
                            name=row['name'],
                            price=row['price'],
                            is_discontinued=row['is_discontinued'].lower() == 'true',
                            manufacturer_name=row['manufacturer_name'],
                            medicine_type=row['medicine_type'],
                            pack_size_label=row['pack_size_label'],
                            short_composition1=row.get('short_composition1', ''),
                            short_composition2=row.get('short_composition2', '')
                        )
                    )
                CentralMedicine.objects.bulk_create(medicines)
                self.stdout.write(self.style.SUCCESS(f'Successfully loaded {len(medicines)} medicines into the database.'))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f'Error loading medicines: {str(e)}'))
