from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Post(models.Model):
    text = models.CharField(max_length=200)
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    creation_time = models.DateTimeField()

    def __str__(self):
        return "Posted by " + str(self.user.first_name) + " " + str(self.user.last_name) + " - " + self.text + " - " + str(self.creation_time)

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.PROTECT)
    bio = models.CharField(max_length=200)
    picture = models.FileField(blank=True)
    content_type = models.CharField(max_length=50)
    following = models.ManyToManyField(User, related_name='followers')

    def __str__(self):
        return str(self.user.first_name) + " " + str(self.user.last_name) + " " + self.bio + " " + str(self.picture) + " " + self.content_type + str(self.following)

class Comment(models.Model):
    text = models.CharField(max_length=200)
    creator = models.ForeignKey(User, on_delete=models.PROTECT)
    creation_time = models.DateTimeField()
    post = models.ForeignKey(Post, on_delete=models.PROTECT)