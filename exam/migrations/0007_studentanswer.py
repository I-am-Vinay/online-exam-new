import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('exam', '0006_question_max_words_question_question_type_and_more'),
        ('student', '0003_alter_student_id'),
        ('teacher', '0003_alter_teacher_id'),
    ]

    operations = [
        migrations.CreateModel(
            name='StudentAnswer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('answer_text', models.TextField()),
                ('marks_obtained', models.PositiveIntegerField(blank=True, null=True)),
                ('is_graded', models.BooleanField(default=False)),
                ('graded_at', models.DateTimeField(blank=True, null=True)),
                ('feedback', models.TextField(blank=True, null=True)),
                ('graded_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='teacher.teacher')),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='exam.question')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='student.student')),
            ],
        ),
    ]
