# Generated by Django 2.2.2 on 2019-06-17 09:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0011_auto_20190615_1928'),
    ]

    operations = [
        migrations.AlterField(
            model_name='purchaseorder',
            name='creation_date',
            field=models.DateField(blank=True, null=True),
        ),
    ]
