from django.core.management.base import BaseCommand, CommandError
from django.utils.module_loading import import_string
from io import TextIOWrapper

def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]

class Command(BaseCommand):
    help = 'Import csv for model'

    def add_arguments(self, parser):
        parser.add_argument('importer_class', type=str)
        parser.add_argument('csv_file', type=str)
        parser.add_argument('--skip', action='store_true', default=False)
        parser.add_argument('--new', action='store_true', default=False)

    def handle(self, *args, **options):
        importer_class = import_string(options['importer_class'])
        csv_file = options['csv_file']

        importer = importer_class()
        rows = importer.get_rows_from_file(csv_file)

        if not options["new"]:
            result = importer.import_rows(rows, skip_all=options["skip"])
        else:
            for subset in chunks(rows, 1000):
                importer.import_rows(subset,  new_all=True, commit=True)





        #raise CommandError('Poll "%s" does not exist' % poll_id)
        #self.stdout.write(self.style.SUCCESS('Successfully closed poll "%s"' % poll_id))
