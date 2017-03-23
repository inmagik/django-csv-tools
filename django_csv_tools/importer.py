import csv
from django.db import transaction
from django import forms
from io import TextIOWrapper


class Importer(object):
    """
    """

    natural_keys = []

    def get_rows_from_file(self, path):
        out = []
        with open(path, "r") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                out.append(row)
        return out

    def get_rows_from_stream(self, stream):
        out = []
        reader = csv.DictReader(stream)
        for row in reader:
            out.append(row)
        return out

    def check_rows(self, rows):
        pass

    def skip_rows(self, rows_to_skip):
        return rows

    @transaction.atomic
    def import_rows(self, rows=[], fixed_values={}, commit=False, hints={}):
        out = {
            "rows" : rows,
            "rows_status" : {
                "new" : [],
                "errors" : [],
                "updated" : [],
                "exiting" : [],
            }
        }

        sid = transaction.savepoint()

        for i, row in enumerate(rows):
            model_args = {}
            row_errors = {}

            for x in self.fields_map:
                try:
                    arg = self.get_field_value(row, self.fields_map[x])
                    model_args[x] = arg
                except Exception as e:
                    if commit:
                        raise e
                    row_errors[x] = e

            model_args.update(fixed_values)

            if row_errors.keys():
                out["rows_status"]["errors"].append([i, row, row_errors, False])
                continue

            try:
                hint = hints.get(i)
                if hint == False:
                    continue

                if self.natural_keys:
                    lookup_args = {x:model_args[x] for x in self.natural_keys}
                    existing_instances = self.model.objects.filter(**lookup_args)
                    if existing_instances.exists():
                        out["rows_status"]["exiting"].append([i, row, existing_instances])

                if hint == None:
                    instance = self.model(**model_args)
                    instance.save()
                    out["rows_status"]["new"].append(i)
                else:
                    instance = self.model.get(pk=hint)
                    for attr in model_args:
                        setattr(instance, attr, model_args[attr])
                    instance.save()
                    out["rows_status"]["updated"].append(i)


            except Exception as e:
                out["rows_status"]["errors"].append([i, row, e, True])
                if commit:
                    raise e

        if commit:
            transaction.savepoint_commit(sid)
        else:
            transaction.savepoint_rollback(sid)

        return out


    def get_field_value(self, row, mapped_field):
        if type(mapped_field) == str:
            return row[mapped_field]

        elif type(mapped_field) == RelatedImport:
            return mapped_field.get_object(row)

        raise TypeError("Wrong mapping...")


    def import_csv(self, path, fixed_values={}, commit=False, hints=None):
        rows = self.get_rows_from_file(path)
        return self.import_rows(rows=rows, fixed_values=fixed_values, commit=commit, hints=hints)

    def import_stream(self, stream, fixed_values={}, commit=False, hints=None):
        rows = self.get_rows_from_stream(stream)
        return self.import_rows(rows=rows, fixed_values=fixed_values, commit=commit, hints=hints)


class RelatedImport(object):

    def __init__(self, model=None,  lookup_args={}, lookup_fn=None):
        self.model = model
        self.lookup_args = lookup_args
        self.lookup_fn = lookup_fn

    def get_filter_args(self, row):
        filter_args = { x: row[self.lookup_args[x]] for x in self.lookup_args }
        return filter_args

    def get_object(self, row):
        filter_args = self.get_filter_args(row)
        if self.lookup_fn:
            return self.lookup_fn(self.model, filter_args)
        return self.model.objects.get(**filter_args)