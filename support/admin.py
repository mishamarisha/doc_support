from django.contrib import admin

from .models import Project, Release, Update, ProjectSection, Team, Tag

admin.site.register(Project)
admin.site.register(Release)
admin.site.register(Update)
admin.site.register(ProjectSection)
admin.site.register(Team)
admin.site.register(Tag)
