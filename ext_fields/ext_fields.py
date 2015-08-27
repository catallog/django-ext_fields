# -*- coding: utf-8 -*-
from __future__ import unicode_literals

## \author Jean Marcel D Schmidt <jean.schmidt@humantech.com>
"""
@package ext_fields
This package provides the dynamic fields functionality for django models.

This package provides a class decorator named ExFieldsDecorator that includes
in a django model a easy way to create dynamic fields on a defined model.
"""

from datetime import datetime
from django.db import models


#  _____                    _   _
# | ____|_  _____ ___ _ __ | |_(_) ___  _ __  ___
# |  _| \ \/ / __/ _ \ '_ \| __| |/ _ \| '_ \/ __|
# | |___ >  < (_|  __/ |_) | |_| | (_) | | | \__ \
# |_____/_/\_\___\___| .__/ \__|_|\___/|_| |_|___/
#                    |_|

## \public
class ExFieldException(Exception):
    """
    General base class for this module exceptions.
    """
    pass

## \public
class ExFieldInvalidTypeSet(ExFieldException):
    """
    Invalid type given on function call.
    """
    pass

## \public
class ExFieldUnableSaveFieldType(ExFieldException):
    """
    The data given for extended fields cannot be saved/selected as
    its not supported.
    """
    pass

## \public
class ExFieldExceptionCannotSet(ExFieldException):
    """
    ext_fields_manager cannot be set.
    """
    pass

## \public
class ExFieldExceptionCannotDel(ExFieldException):
    """
    ext_fields_manager cannot be deleted.
    """
    pass

#  _____      _____ _      _     _     ____                      _
# | ____|_  _|  ___(_) ___| | __| |___|  _ \ __ _ _ __ ___ _ __ | |_
# |  _| \ \/ / |_  | |/ _ \ |/ _` / __| |_) / _` | '__/ _ \ '_ \| __|
# | |___ >  <|  _| | |  __/ | (_| \__ \  __/ (_| | | |  __/ | | | |_
# |_____/_/\_\_|   |_|\___|_|\__,_|___/_|   \__,_|_|  \___|_| |_|\__|

## \protected
def create_ex_fields_parent(cls):
    class ExtendedFieldsParent(models.Model):
        """
        Parent class for the hidden tables containing the extended
        fields in EAV formatt.
        """
        fk = models.ForeignKey(cls, null=False)
        field = models.CharField(max_length=128, null=False)

        class Meta:
            abstract = True
            unique_together = (('field', 'fk',),)
            index_together = ('field', 'fk',)

    return ExtendedFieldsParent

#  _____                 _         __  __      _
# | ____|_ __ ___  _ __ | |_ _   _|  \/  | ___| |_ __ _
# |  _| | '_ ` _ \| '_ \| __| | | | |\/| |/ _ \ __/ _` |
# | |___| | | | | | |_) | |_| |_| | |  | |  __/ || (_| |
# |_____|_| |_| |_| .__/ \__|\__, |_|  |_|\___|\__\__,_|
#                 |_|        |___/

## \protected
class EmptyMeta:
    """
    Empty default meta, in the case of the parent class dont define any
    """
    pass

#  ___       _                        _ _____ _ _     _ __  __
# |_ _|_ __ | |_ ___ _ __ _ __   __ _| |  ___(_) | __| |  \/  | __ _ _ __
#  | || '_ \| __/ _ \ '__| '_ \ / _` | | |_  | | |/ _` | |\/| |/ _` | '__|
#  | || | | | ||  __/ |  | | | | (_| | |  _| | | | (_| | |  | | (_| | |
# |___|_| |_|\__\___|_|  |_| |_|\__,_|_|_|   |_|_|\__,_|_|  |_|\__, |_|
#                                                              |___/

## \protected
class _InternalExFieldsManager:
    """
    Returned by _ExFieldsManager Descriptor providing work functions.
    """
    ## \public
    # \param[in] owner the class owner, or model base class.
    def __init__(self, owner, fields_tables, fields_models):
        """
        Class Constructor
        """
        self._owner = owner
        self._fields_tables = fields_tables
        self.__ex_fields_class = fields_models

    ## \protected
    # \return a new queryset
    def _get_new_queryset(self):
        """
        creates a new queryset
        """
        return self._owner.objects

    ## \protected
    # \param[in] argv the arguments dict to process and build query filters.
    # \throws ExFieldUnableSaveFieldType 'Cannot select based on given type!'
    # \return a model.Q for a given filter options.
    def _get_filtering(self, argv):
        """
        Contruct filtering options based on argv in a similar way of django.
        """
        qoptions = (
            'exact',
            'iexact',
            'contains',
            'icontains',
            'in',
            'gt',
            'gte',
            'lt',
            'lte',
            'startswith',
            'istartswith',
            'endswith',
            'iendswith',
            'range',
            'year',
            'month',
            'day',
            'week_day',
            'hour',
            'minute',
            'second',
            'isnull',
            'search',
            'regex',
            'iregex',
            'have',
        )

        p = None
        for fname, fopt in argv.items():
            q = None

            opt = 'exact'
            opts_path = fname.split('__')[-1]
            if opts_path in qoptions:
                opt = opts_path
                fname = fname[:len(fname)-len(opt)-2]

            if opt == 'have':
                for tname, ttype in self._fields_tables.items():
                    x = models.Q(((tname+'__field').lower(), fname,))
                    if fopt:
                        q = (q | x) if q else x
                    else:
                        q = (q & (~x)) if q else ~x
            else:
                for tname, ttype in self._fields_tables.items():
                    if type(fopt) is ttype[0]:
                        q = models.Q(((tname+'__value').lower()+'__'+opt, fopt,)) \
                            & models.Q(((tname+'__field').lower(), fname,))
                        break
                else:
                    raise ExFieldUnableSaveFieldType('Cannot select based on given type!')

            if not p:
                p = q
            else:
                p = p & q

        return p

    ## \public
    # \param[in] queryset The queryset for a given query.
    # \return a django queryset
    def filter(self, queryset=None, **argv):
        """
        Analog to django.models.Model.objects.filter(), but it dont accept
        django.models.Q parametters.
        """
        if not queryset:
            queryset = self._get_new_queryset()
        return queryset.filter(self._get_filtering(argv)).distinct()

    ## \public
    # \param[in] queryset The queryset for a given query.
    # \return a django queryset
    def exclude(self, queryset=None, **argv):
        """
        Analog to django.models.Model.objects.exclude(), but it dont accept
        django.models.Q parametters.
        """
        if not queryset:
            queryset = self._get_new_queryset()
        return queryset.exclude(self._get_filtering(argv)).distinct()

    # ## \plublic
    # # \return a list o unique fields
    def distinct_fields(self, queryset=None):
        """
        Get a list with all ext_fields that are linked with a given model
        """
        ret = list()

        if not queryset:
            queryset = self._get_new_queryset()

        columns = map(lambda x: (x+'__field').lower(), self._fields_tables.keys())
        fields = queryset.values(*columns).distinct()

        for entry in fields:
            for value in entry.values():
                if value is not None and value not in ret:
                    ret.append(value)

        return ret

#  _____      _   _____ _ _     _ __  __
# | ____|_  _| |_|  ___(_) | __| |  \/  | __ _ _ __
# |  _| \ \/ / __| |_  | | |/ _` | |\/| |/ _` | '__|
# | |___ >  <| |_|  _| | | | (_| | |  | | (_| | |
# |_____/_/\_\\__|_|   |_|_|\__,_|_|  |_|\__, |_|
#                                        |___/

## \protected
class _ExFieldsManager(object):
    """
    Manager Descriptor to allow access of some other options that cannot be
    provided directly by _ExFieldsDescriptors.
    """
    ## \public
    def __init__(self, fields_tables, fields_models):
        self._fields_tables = fields_tables
        self.__ex_fields_class = fields_models

    ## \public
    def __get__(self, instance, owner):
        """
        returns interface class.
        """
        return _InternalExFieldsManager(owner, self._fields_tables,
            self.__ex_fields_class)

    ## \public
    # \throws ExFieldExceptionCannotSet 'Cannot set ext_fields_manager property'.
    def __set__(self, instance, value):
        """
        should not be set.
        """
        raise ExFieldExceptionCannotSet('Cannot set ext_fields_manager property')

    ## \public
    # \throws ExFieldExceptionCannotDel 'Cannot del ext_fields_manager property'.
    def __del__(self, instance):
        """
        should not be deleted.
        """
        raise ExFieldExceptionCannotDel('Cannot del ext_fields_manager property')

#  _____      _   _____ _ _     _ ____
# | ____|_  _| |_|  ___(_) | __| |  _ \  ___  ___  ___ _ __
# |  _| \ \/ / __| |_  | | |/ _` | | | |/ _ \/ __|/ __| '__|
# | |___ >  <| |_|  _| | | | (_| | |_| |  __/\__ \ (__| |
# |_____/_/\_\\__|_|   |_|_|\__,_|____/ \___||___/\___|_|

## \public
class _ExFieldsDescriptors(object):
    """
    Descriptor to provide access to extended fields.
    """
    ## \public
    def __init__(self, fields_tables, fields_models):
        self._fields_tables = fields_tables
        self.__ex_fields_class = fields_models

    ## \protected
    # \return a new queryset
    def _get_new_queryset(self, owner, instance):
        """
        creates a new queryset
        """
        return owner.objects.filter(pk=instance.pk)

    ## \public
    def __get__(self, instance, owner):
        """
        returns a dict containing ext_fields data
        """
        if '__extendedFieldsCache' not in instance.__dict__:
            instance.__extendedFieldsCache = dict()

            queryset = self._get_new_queryset(owner, instance)
            columns_fields = map(lambda x: (x+'__field').lower(), self._fields_tables.keys())
            columns_values = map(lambda x: (x+'__value').lower(), self._fields_tables.keys())
            columns = columns_fields + columns_values
            fields = queryset.values(*columns).distinct()

            for row in fields:
                vl = {}
                for k, v in row.items():
                    if v != None:
                        ftname = k[:-5]
                        ttname = k[-5:]

                        vl[ftname] = vl[ftname] if ftname in vl else {}
                        vl[ftname][ttname] = v

                for k, v in vl.items():
                    instance.__extendedFieldsCache[v['field']] = v['value']

        return instance.__extendedFieldsCache

    ## \public
    # \param[in] instance the python give-me the instance that i'm accessing.
    #
    # \param[in] value thi can be a dict, a single 2 item tuple like ('key', 'value',)
    #                  or a list of tuples, like in dict.items().
    #
    # \throws ExFieldInvalidTypeSet 'Whrong parameter given to value'.
    #
    # \throws ExFieldUnableSaveFieldType 'for now only str, int, float and datetime
    # can be used as extended fields'.
    #
    def __set__(self, instance, value):
        """
        Sets the fields according with theirs types; Fields marked with None
        will be deleted.
        """
        #cleans cache
        self.__delete__(instance)

        if (type(value) is tuple):
            if len(value) is not 2:
                raise ExFieldInvalidTypeSet('on setting ext_fields: Invalid lenght'
                    +' for tuple, len(value) must be 2, first item with key, second'
                    +' the holder value')
            if type(value[0]) not in (str, unicode,):
                raise ExFieldInvalidTypeSet('on setting ext_fields, first field on '
                    +'property tuple must be str with field name')

            if value[1] is None:
                return self._delete_field(instance, value[0])

            for tname, ttype in self._fields_tables.items():
                if ttype[0] is type(value[1]):
                    self._set_field(tname, instance, value[0], value[1])
                    break
            else:
                raise ExFieldUnableSaveFieldType('for now only str, int, float and datetime'
                    +'can be used as extended fields')

        elif type(value) is list:
            [ self.__set__(instance, v) for v in value ]
        elif type(value) is dict:
            self.__set__(instance, value.items())
        else:
            raise ExFieldInvalidTypeSet('To set a extended field, give a tuple with key'
                +' value, a list with KV tuples OR a dict')

        return value

    ## \protected
    # \param[in] instance The instance where field will be deleted.
    # \param[in] field fieldname to be deleted from this instance.
    def _delete_field(self, instance, field):
        """
        Delete a field.

        As I dont know the type of the field nor django give me information
        about the number of deleted elements, I have to try to delete in all
        possible tables, quite slow....
        """
        for tname, ttype in self._fields_tables.items():
            self.__ex_fields_class[tname].objects \
                .filter(fk=instance, field=field).delete()

    ## \protected
    # \param[in] tname table name identifying the type.
    # \param[in] instance The instance with we're gonna set field.
    # \param[in] field Name for the field being overrided/created.
    # \param[in] value The new value for the field.
    def _set_field(self, tname, instance, field, value):
        """
        override/create a field.
        """
        t = None
        try:
            t = self.__ex_fields_class[tname].objects.get(fk=instance, field=field)
        except self.__ex_fields_class[tname].DoesNotExist:
            t = self.__ex_fields_class[tname]()
            t.field = field
            t.fk = instance
        except:
            raise

        t.value = value
        t.save()

    ## \public
    def __delete__(self, instance):
        """
        frees the cache, just that, it does not delete anything on database
        """
        if '__extendedFieldsCache' in instance.__dict__:
            del instance.__dict__.__extendedFieldsCache

## \public
#  \note helper method to encode ext fields in dict format
#  \param[in] override Should ext override django models fields
def as_dict(self, override=False):
    def __get_ext_fields_dicts__(ovr):
        model_fields = { k:v for k,v in self.__dict__.items() if not k.startswith('_') }
        if ovr:
            return model_fields, self.ext_fields
        return self.ext_fields, model_fields
    base, ext = __get_ext_fields_dicts__(override)
    base.update(ext)
    return base

## \public
#  \note This is the main decorator, you should use like this:
# @ExFieldsDecorator
# class MyModel(models.Model):
#     pass
def ExFieldsDecorator(cls):
    """
    This class decorator is used to decorate a django.models.Model
    with the goal of provide aditional arbitrary fields for that
    model
    """

    defaults_common = {'__module__': cls.__module__}
    defaults_common['Meta'] = cls.Meta if hasattr(cls, 'Meta') else EmptyMeta

    name_base = cls.__name__ + 'ExtendedFields'
    fields_tables = {
        name_base+'String':  (unicode,  models.CharField, {'null':False, 'max_length':256},),
        name_base+'Integer': (int,      models.IntegerField, {'null':False},),
        name_base+'Float':   (float,    models.FloatField, {'null':False},),
        name_base+'Date':    (datetime, models.DateTimeField, {'null':False},)
    }
    fields_models = dict()
    for k, v in fields_tables.items():
        prop = {'value': v[1](**(v[2]))}
        prop.update(defaults_common)
        fields_models[k] = type(str(k), (create_ex_fields_parent(cls),), prop)

    cls.ext_fields = _ExFieldsDescriptors(fields_tables, fields_models)
    cls.ext_fields_manager = _ExFieldsManager(fields_tables, fields_models)
    cls.__ex_fields_class = fields_models
    setattr(cls, 'as_dict', as_dict )

    return cls
