from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone


User = get_user_model()


class TargetPopulation(models.Model):
    population = models.CharField(max_length=255)


class Poll(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    source = models.CharField(max_length=255)
    question = models.CharField(max_length=255)
    image_url = models.URLField(null=True, blank=True)
    created_date = models.DateTimeField(default=timezone.now)
    expire_date = models.DateTimeField()
    approved = models.BooleanField(default=False)
    multiselect = models.BooleanField(default=False)
    user_comment = models.CharField(max_length=255, null=True, blank=True)
    admin_comment = models.CharField(max_length=255, null=True, blank=True)
    target_populations = models.ManyToManyField(TargetPopulation)


class PollOption(models.Model):
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE)
    choice = models.CharField(max_length=255)


class PollVote(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE)
    poll_options = models.ManyToManyField(PollOption)
    created_date = models.DateTimeField(default=timezone.now)
