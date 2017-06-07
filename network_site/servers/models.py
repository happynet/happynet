from django.db import models


class Server(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=255)
    notes = models.TextField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Router(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=255)
    notes = models.TextField(blank=True, default='')
    content = models.TextField(blank=True, default='')
    is_active = models.BooleanField(default=True)
    order = models.IntegerField(default=0)
    server = models.ForeignKey(Server)

    class Meta:
        ordering = ['order',]

    def __str__(self):
        return self.name
