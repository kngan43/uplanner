# Generated by Django 2.0.2 on 2018-03-29 13:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('schedule', '0009_auto_20180327_1826'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='schedulecourse',
            name='category',
        ),
        migrations.RemoveField(
            model_name='user',
            name='password',
        ),
        migrations.AlterField(
            model_name='section',
            name='component',
            field=models.CharField(choices=[('lec', 'Lecture'), ('dis', 'Discussion'), ('lab', 'Laboratory'), ('col', 'Colloquium'), ('the', 'Dissertation / Thesis'), ('stu', 'Individualized Study'), ('pra', 'Practicum'), ('sem', 'Seminar'), ('ski', 'Studio / Skills')], max_length=3),
        ),
    ]
