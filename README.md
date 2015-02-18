# Ext_Fields

## WTF?
This is a decorator to allow django models have arbitrary data fields.

## But what is your motivation?
Well, sometimes you are developing something, its not your fault, but things
change, and requisites come from everywhere... And you are tired on running really
slow migrations on clients databases.

Ok, so you decide that its time to allow the client at least decide their own
model fields. Such: what information should a client contain? Residential number?
Cellphone number? Security number?

And you want to do it completely dynamically, so you don't need to worry anymore.

To make things easy we created a decorator that you put in your django models
to allow them have any additional arbitrary fields using a simple EAV approach.
I is simple, fast, and you don't need to worry about it. I is NOT the final ultimate
solution for the problem, but a really handy one, that can be used in virtually
any existing project.

## Ok, show me more
So this is your current code:

    class Client(models.Model):
        name = models.CharField('null'=False, 'max_length'=150)
        email = models.CharField('null'=False, 'max_length'=100)

        account = models.ForeignKey(MyAccount)

you could do something like that:

    @ExFieldsDecorator
    class Client(models.Model):
        #this we're going to keep, we need this to be FAST
        name = models.CharField('null'=False, 'mas_length'=150)

        account = models.ForeignKey(MyAccount)

and now we could do something like:

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

## And, what are the current limitations?

Well there is some, first of all, you cannot change the type of a field without
deleting it before. This may cause some errors and will make both values be stored
on the database. I made it this way, because forcing a delete when you don't need to
is unnecessary, and I simply don't want to store a metadata about the field to increase
speed and simplicity. So:

    #this is fine
    c.ext_fields = {'cellphone': '+1 5737 9144'}
    c.ext_fields = {'cellphone': '+1 5737 9154'}
    c.ext_fields = {'cellphone': 'I Love My Mother'}

    #this is NOT
    c.ext_fields = {'cellphone': '+1 5737 9144'}
    c.ext_fields = {'cellphone': 11}
    c.ext_fields = {'cellphone': 2.7}

    #do THIS instead
    c.ext_fields = {'cellphone': '+1 5737 9144'}
    c.ext_fields = {'cellphone': None} #delete this field first
    c.ext_fields = {'cellphone': 11}
    c.ext_fields = {'cellphone': None} #delete this field first
    c.ext_fields = {'cellphone': 2.7}

Queries are cached, so, if you changed the properties of your object in the
database this may not reflect in your already loaded object, to clean the cache
you simply do:

    #cleans the local cache
    del c.ext_fields

And actually there is no way to currently make a batch update in these fields. So
if you want to update all instances of a given model, you can only rely on for-loops
or a custom made SQL.

## I have some awesome idea, can I help?

Of couse! That's why it is on github, feel free to make forks and pool requests!

## I don't have any idea, but I want to help you...

Ok there are some open todos...
* Make it work on Python 3
* Make tests cover 100% of the code, and make them cover 100% of the functionality
* Fix some small documenting issues with doxygen