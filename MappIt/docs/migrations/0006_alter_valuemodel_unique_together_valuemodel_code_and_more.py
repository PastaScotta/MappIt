# Generated by Django 4.2.2 on 2023-07-13 10:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('docs', '0005_valuemodel'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='valuemodel',
            unique_together=set(),
        ),
        migrations.AddField(
            model_name='valuemodel',
            name='code',
            field=models.CharField(default=0, max_length=255, unique=True, verbose_name='Mapping code'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='valuemodel',
            name='name',
            field=models.CharField(max_length=255, verbose_name='Field name'),
        ),
        migrations.AlterUniqueTogether(
            name='valuemodel',
            unique_together={('dynamic_model', 'name', 'code')},
        ),
    ]
