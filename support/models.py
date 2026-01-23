from django.db import models

from django.contrib.auth import get_user_model


User = get_user_model()


class Project(models.Model):
    name = models.CharField(
        verbose_name='Название проекта'
        )
    description = models.TextField(
        verbose_name='Описание'
    )
    author = models.ForeignKey(
        'User',
        on_delete=models.SET_NULL
    )


class Release(models.Model):
    project = models.ForeignKey(
        'Project',
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
        verbose_name='Планируемая дата выхода'
        )
    author = models.ForeignKey(
        'User',
        on_delete=models.SET_NULL
    )
    description = models.TextField(
        verbose_name='Описание'
    )


class Update(models.Model):
    release = models.ForeignKey(
        'Release',
        related_name='updates'
    )
    author = models.ForeignKey(
        'User',
        on_delete=models.SET_NULL
    )
    task_number = models.CharField()
    title = models.CharField()
    description = models.TextField(
        verbose_name='Описание'
    )
    # status
    # comment
    # instructions


class Tag(models.Model):
    author = models.ForeignKey(
        'User',
        on_delete=models.SET_NULL
    )
    # text


class ProjectSection(models.Model):
    author = models.ForeignKey(
        'User',
        on_delete=models.SET_NULL
    )
    # project
    # name
    # description


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
        related_name='team'
    )
    user = models.ForeignKey(
        'User',
        related_name='projects'
    )
    role = models.CharField(
        choices=ROLE_CHOICES,
        default=MEMBER,
        verbose_name='Роль'

    )


class TagUpdate(models.Model):
    # tag
    # update
    pass
