from django.db import models
from django.utils import timezone

from django.contrib.auth import get_user_model


User = get_user_model()


class Project(models.Model):
    name = models.CharField(
        max_length=200,
        verbose_name='Название проекта'
        )
    description = models.TextField(
        verbose_name='Описание',
        blank=True
    )
    author = models.ForeignKey(
        User,
        null=True,
        on_delete=models.SET_NULL
    )

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Проекты'


class Release(models.Model):
    project = models.ForeignKey(
        Project,
        null=True,
        on_delete=models.SET_NULL
    )
    number = models.IntegerField(
        verbose_name='Номер релиза'
        )
    is_published = models.BooleanField(
        verbose_name='Вышел или нет'
        )
    planned_release_date = models.DateField(
        verbose_name='Планируемая дата выхода'
        )
    real_release_date = models.DateField(
        verbose_name='Фактическая дата выхода'
        )
    author = models.ForeignKey(
        User,
        null=True,
        on_delete=models.SET_NULL
    )
    description = models.TextField(
        verbose_name='Описание'
    )

    def __str__(self):
        return self.number

    class Meta:
        ordering = ['number']
        verbose_name_plural = 'Релизы'


class Update(models.Model):
    release = models.ForeignKey(
        Release,
        on_delete=models.CASCADE,
        related_name='updates'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True
    )
    task_number = models.CharField(max_length=30)
    title = models.CharField(max_length=30)
    description = models.TextField(
        verbose_name='Описание'
    )
    tags = models.ManyToManyField(
        'Tag',
        related_name='updates',
        blank=True)
    # status
    # comment
    # instructions

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['title']
        verbose_name_plural = 'Обновления'


class Tag(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True
    )
    text = models.CharField(max_length=30)

    def __str__(self):
        return self.text

    class Meta:
        ordering = ['text']
        verbose_name_plural = 'Теги'


class ProjectSection(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    project = models.ForeignKey(
        'Project',
        on_delete=models.CASCADE,
        null=True,
    )
    title = models.CharField(max_length=30)
    description = models.TextField(
        verbose_name='Описание',
        blank=True,
        null=True,
    )

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = 'Разделы'


class Team(models.Model):
    MEMBER = 'member'
    DIRECTOR = 'director'
    ADMIN = 'admin'
    ROLE_CHOICES = [
        (MEMBER, 'исполнитель'),
        (DIRECTOR, 'руководитель'),
        (ADMIN, 'администратор'),
        ]

    project = models.ForeignKey(
        'Project',
        on_delete=models.CASCADE,
        related_name='team'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='projects'
    )
    role = models.CharField(
        choices=ROLE_CHOICES,
        default=MEMBER,
        verbose_name='Роль'

    )

    def __str__(self):
        return self.project.name

    class Meta:
        ordering = ['project']
        verbose_name_plural = 'Команды'


class ImportedChange(models.Model):
    SOURCE_CHOICES = [
        ('prod', 'Production'),
        ('dev', 'Development'),
    ]
    source = models.CharField(
        max_length=4,
        choices=SOURCE_CHOICES,
        db_index=True
        )
    date = models.DateField()
    text = models.TextField()
    hash = models.CharField(max_length=64, unique=True)
    imported_at = models.DateTimeField(default=timezone.now)
    is_processed = models.BooleanField(default=False)

    class Meta:
        ordering = ['-date', 'source']
        verbose_name = 'Импортированное изменение'
        verbose_name_plural = 'Импортированные изменения'

    def __str__(self):
        return f"[{self.source}] {self.date} - {self.text[:50]}"
