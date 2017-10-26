from __future__ import absolute_import, unicode_literals
import time

from django.core.management import CommandError
from django_elasticsearch_dsl import Index
from django_elasticsearch_dsl.management.commands.search_index import Command as SearchIndexCommand
from django_elasticsearch_dsl.registries import registry
from elasticsearch_dsl.connections import connections

connection = connections.get_connection()


class Command(SearchIndexCommand):
    # Just reuse the Django Elasticsearch DSL command for now,
    # pending rewrite.

    def add_arguments(self, parser):
        parser.add_argument(
            '--models',
            metavar='app[.model]',
            type=str,
            nargs='*',
            help="Specify the model or app to be updated in elasticsearch"
        )
        parser.add_argument(
            '--create',
            action='store_const',
            dest='action',
            const='create',
            help="Create the indices in elasticsearch"
        )
        parser.add_argument(
            '--populate',
            action='store_const',
            dest='action',
            const='populate',
            help="Populate elasticsearch indices with models data"
        )
        parser.add_argument(
            '--delete',
            action='store_const',
            dest='action',
            const='delete',
            help="Delete the indices in elasticsearch"
        )
        parser.add_argument(
            '--rebuild',
            action='store_const',
            dest='action',
            const='rebuild',
            help="Delete the indices and then recreate and populate them"
        )
        parser.add_argument(
            '-f',
            action='store_true',
            dest='force',
            help="Force operations without asking"
        )
        parser.add_argument(
            '--using',
            default='default',
            help='Which Elasticsearch connection should be used (default: default)'
        )

    def _get_models(self, args):
        """
        Get Models from registry that match the --models args
        """
        if args:
            models = []
            for arg in args:
                arg = arg.lower()
                match_found = False

                for model in registry.get_models():
                    if model._meta.app_label == arg:
                        models.append(model)
                        match_found = True
                    elif '{}.{}'.format(
                        model._meta.app_label.lower(),
                        model._meta.model_name.lower()
                    ) == arg:
                        models.append(model)
                        match_found = True

                if not match_found:
                    raise CommandError("No model or app named {}".format(arg))
        else:
            models = registry.get_models()

        return set(models)

    def _create(self, models, options, connection):
        for index in registry.get_indices(models):
            index_name = '%s.%s' % (str(index), int(time.time()))
            self.stdout.write("Creating index '{}'".format(index))
            connection.indices.create(index=index_name, body=index.to_dict())

            if not connection.indices.exists_alias(name=str(index)):
                connection.indices.put_alias(index=index_name, name=str(index))

    def _populate(self, models, options, connection):
        for doc in registry.get_documents(models):
            qs = doc().get_queryset()
            self.stdout.write("Indexing {} '{}' objects".format(
                qs.count(), doc._doc_type.model.__name__)
            )
            doc().update(qs)

    def _delete(self, models, options, connection):
        index_names = [str(index) for index in registry.get_indices(models)]

        if not options['force']:
            response = input(
                "Are you sure you want to delete "
                "the '{}' indexes? [n/Y]: ".format(", ".join(index_names)))
            if response.lower() != 'y':
                self.stdout.write('Aborted')
                return False

        for index in registry.get_indices(models):
            self.stdout.write("Deleting index '{}'".format(index))
            index.delete(ignore=404)
        return True

    def _rebuild(self, models, options, connection):
        index_names = [str(index) for index in registry.get_indices(models)]

        if not options['force']:
            answer = input("Are you sure you want to delete the '{}' indexes? [n/Y]: ".format(", ".join(index_names)))
            if answer.lower() != 'y':
                self.stdout.write('Aborted')
                return False

        real_indices = {}

        # Create the new indices.
        for index in registry.get_indices(models):
            index_name = '%s.%s' % (str(index), int(time.time()))
            self.stdout.write("Creating index '{}'".format(index_name))
            connection.indices.create(index=index_name, body=index.to_dict())

            real_indices[str(index)] = index_name

        # Populate the new indices.
        for doc in registry.get_documents(models):
            qs = doc().get_queryset()
            real_index = real_indices[doc._doc_type.index]
            doc._doc_type.index = real_indices[doc._doc_type.index]
            self.stdout.write("Indexing {} '{}' objects to {}".format(
                qs.count(), doc._doc_type.model.__name__, real_index)
            )
            doc().update(qs)

        # Update the aliases.
        for alias, real_index in real_indices.iteritems():
            self.stdout.write("Pointing alias {} to '{}'".format(alias, real_index))
            connection.indices.put_alias(index=real_index, name=alias)

        # Delete the old indexes.
        for alias, real_index in real_indices.iteritems():
            old_indices = [idx for idx in connection.indices.get('{}.*'.format(alias)).keys() if idx != real_index]

            self.stdout.write("Deleting old indices: {}".format(', '.join(old_indices)))

            for old_index in old_indices:
                Index(old_index).delete()

    def handle(self, *args, **options):
        if not options['action']:
            raise CommandError(
                "No action specified. Must be one of"
                " '--create','--populate', '--delete' or '--rebuild' ."
            )

        action = options['action']
        models = self._get_models(options['models'])

        connection = connections.get_connection(options['using'])

        if action == 'create':
            self._create(models, options, connection)
        elif action == 'populate':
            self._populate(models, options, connection)
        elif action == 'delete':
            self._delete(models, options, connection)
        elif action == 'rebuild':
            self._rebuild(models, options, connection)
        else:
            raise CommandError(
                "Invalid action. Must be one of"
                " '--create','--populate', '--delete' or '--rebuild' ."
            )
