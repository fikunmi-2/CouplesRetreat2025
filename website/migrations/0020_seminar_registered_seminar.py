# Generated by Django 5.1.3 on 2025-05-24 00:45

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0019_registered_labourer_note'),
    ]

    operations = [
        migrations.CreateModel(
            name='Seminar',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('description', models.TextField()),
                ('code_name', models.CharField(max_length=20, unique=True)),
                ('max_capacity', models.PositiveIntegerField()),
            ],
        ),
        migrations.AddField(
            model_name='registered',
            name='seminar',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='registered_set', to='website.seminar'),
        ),
    ]
