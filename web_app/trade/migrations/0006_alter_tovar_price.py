# Generated by Django 4.0.4 on 2022-05-07 23:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('trade', '0005_alter_tovar_price'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tovar',
            name='price',
            field=models.IntegerField(),
        ),
    ]
