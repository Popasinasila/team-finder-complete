from django.conf import settings
from django.db import models

TITLE_MAX_LENGTH = 200
STATUS_MAX_LENGTH = 20

STATUS_OPEN = "open"
STATUS_IN_PROGRESS = "in_progress"
STATUS_COMPLETED = "completed"

STATUS_CHOICES = [
    (STATUS_OPEN, "Открыт"),
    (STATUS_IN_PROGRESS, "В работе"),
    (STATUS_COMPLETED, "Завершён"),
]


class Project(models.Model):
    title = models.CharField(max_length=TITLE_MAX_LENGTH)
    description = models.TextField(blank=True)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="projects",
    )
    status = models.CharField(
        max_length=STATUS_MAX_LENGTH,
        choices=STATUS_CHOICES,
        default=STATUS_OPEN,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name="joined_projects",
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


class FavoriteProject(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="favorites",
    )
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="favorited_by",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        unique_together = ("user", "project")

    def __str__(self):
        return f"{self.user} → {self.project}"
