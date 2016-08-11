# ExtFields
A Django decorator to allow arbitrary data storing in models.

[![Build Status](https://travis-ci.org/collabo-br/django-ext_fields.svg?branch=master)](https://travis-ci.org/collabo-br/django-ext_fields)

## Motivation
We work with a very heterogeneous product catalog. It ranges from structural pieces like pipes and electrical switches to furnitures and clothes.
Guess what? The informations related to those products are heterogeneous too. They range in quantity as well as in format. It has very precise data from mechanical products like its diameter, weight and pressure to some subjective descriptions or fancy color names like "fuchsia".
So, we decided to use an EAV like approach to store and retrieve those data.

## Ok, show me more
So this is your current code:

```python
class Client(models.Model):
    name = models.CharField(null=False, max_length=150)
    email = models.CharField(null=False, max_length=100)

    account = models.ForeignKey(MyAccount)
```

you could do something like that:

```python
from ext_fields import ExFieldsDecorator

@ExFieldsDecorator
class Client(models.Model):
    #this we're going to keep, we need this to be FAST
    name = models.CharField(null=False, max_length=150)

    account = models.ForeignKey(MyAccount)
```

and now we could do something like:

```python
#create client with email and cellphone in it.....
c = Client.objects.create(name='Chuck', account=acc)
c.ext_fields = {'email': 'chuck@world.com', 'cellphone': '+1 5737 9144'}

#query what clients have similar emails...
c = Client.ext_fields_manager.filter(email_endswith='@world.com').all()

#query using mixed approach...
k = SimpleModel.ext_fields_manager.filter(
    queryset=Client.objects.filter(account=acc),
    email_endswith='@world.com'
).all()

#get fields associated with a instance....
for fname, fval in k.ext_fields.items():
    print fname, fval

#delete some fields....
k.ext_fields = {'cellphone':None}
```

## Access ExtFields Django Model

At background ExtFields will create a Django Model pointing at your base model.
It is possible to access this model through the property __ext_model_class__ of the base model.

```python
Client.ext_model_class.objects.filter(field="name", lang='en-us').first()

```
The ExtModel fields are described bellow:

|Field|Description|
|-|-|
|__fk__|A Foreign Key to Django base model|
|__field__|A field name|
|__value__|A field value |
|__lang__|The value language (when language support is enabled) |
> Obs.: The __value__ actually is a helper property in model instance.
> It returns the value of fields regardless of its store type



## It also has support to translation

It's not enabled by default so you have to configure that adding the key "EXTFIELDS_TRANSLATE=True" to your project's settings

This settings tells ext_fields to consider the django current language in its queries.
Then, you can use use like that:

```python

from django.utils import translation

...
c = SimpleModel.objects.create(name='C3po', planet='Tatooine')
d = SimpleModel.objects.create(name='Durge')

translation.activate('en-us')
c.ext_fields = { 'race': 'Droid' }
d.ext_fields = { 'race': "Gen'Dai"}

#Translating C3po race to Brazilian portuguese
translation.activate('pt-br')
c.ext_fields = { 'race': 'Andróide' }

#Querying races in other language
translation.activate('en-us')
c.ext_fields.get('race') #RESULT: Droid

#As the active language changes the result permutes accordingly
translation.activate('pt-br')
c.ext_fields.get('race') #RESULT: Andróide

...
```

Fallback to default language can be enabled with the config "EXTFIELDS_FALLBACK_TRANSLATE=True". The default language is defined by the Django setting "LANGUAGE_CODE". That way, when a field has no translation in the active language the value of the default language will be returned.

In the previous example we are missing Durge's race translation. In that case, callings from Brazilian portugues(pt-br) will return the values of fallback language entry ie.: LANGUAGE_CODE=en-us
```python
d = SimpleModel.objects.filter(name='Durge')
translation.activate('pt-br')
d.ext_fields.get('rage') #RESULT: Gen'Dai
```

## I have some awesome idea, can I help?

Of couse! That's why it is on github, feel free to make forks and pull requests!

## I don't have any idea, but I want to help you...

Ok there are some open todos...
* Make it work on Python 3
