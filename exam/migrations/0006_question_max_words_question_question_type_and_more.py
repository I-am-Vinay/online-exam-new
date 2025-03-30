from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('exam', '0005_auto_20201209_2125'),
    ]

    operations = [
        migrations.AddField(
            model_name='question',
            name='max_words',
            field=models.PositiveIntegerField(blank=True, help_text='Maximum words for SAQ answers', null=True),
        ),
        migrations.AddField(
            model_name='question',
            name='question_type',
            field=models.CharField(choices=[('MCQ', 'Multiple Choice'), ('SAQ', 'Short Answer')], default='MCQ', max_length=20),
        ),
        migrations.AlterField(
            model_name='course',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='question',
            name='answer',
            field=models.CharField(max_length=1000),
        ),
        migrations.AlterField(
            model_name='question',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='question',
            name='option1',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='question',
            name='option2',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='question',
            name='option3',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='question',
            name='option4',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='result',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]
