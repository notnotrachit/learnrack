from django.db import models

# Create your models here.
class Course(models.Model):
    id = models.AutoField(primary_key=True)
    url=models.URLField(max_length=200, default='https://www.youtube.com/playlist?list=PLu0W_9lII9agwh1XjRt242xIpHhPT2llg')
    playlist_id=models.CharField(max_length=100, default='PLu0W_9lII9agwh1XjRt242xIpHhPT2llg')
    user=models.ForeignKey('auth.User', on_delete=models.CASCADE)
    tag=models.CharField(max_length=100, default='')
    notes=models.TextField(default="")
    title=models.CharField(max_length=100)
    description=models.TextField(blank=True,null=True)
    channel_name=models.CharField(max_length=100, default='')
    thumbnail_url=models.URLField(max_length=200, default='')
    video_ids=models.JSONField(default=list)
    created_at=models.DateTimeField(auto_now_add=True)
    watched_videos=models.JSONField(default=list)
    updated_at=models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.title

