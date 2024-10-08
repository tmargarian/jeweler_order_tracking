from django.core.management.base import BaseCommand
from django.apps import apps
import csv


class Command(BaseCommand):
    help = "Bulk upload a CSV file into a model (mainly for ZIP codes)"

    def add_arguments(self, parser):
        parser.add_argument("--path", type=str, help="file path")
        parser.add_argument("--model_name", type=str, help="model name")
        parser.add_argument(
            "--app_name",
            type=str,
            help="django app name that the model is connected to",
        )

    def handle(self, *args, **options):
        file_path = options["path"]
        _model = apps.get_model(options["app_name"], options["model_name"])
        with open(file_path, "r", encoding="utf-8-sig") as csv_file:
            reader = csv.reader(csv_file, delimiter=",", quotechar="|")
            header = next(reader)

            for row in reader:
                _object_dict = {key: value for key, value in zip(header, row)}
                _model.objects.update_or_create(**_object_dict)
