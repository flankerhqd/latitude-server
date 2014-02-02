from django.db import models
from django.dispatch import receiver
import time
from django.contrib.auth.models import User
from django.db.models import signals
from django.core.exceptions import ObjectDoesNotExist
# Create your models here.
class Location(models.Model):
    owner = models.ForeignKey('auth.User',related_name="locations")
    lat = models.FloatField()
    lon = models.FloatField()
    prec = models.FloatField()
    ts = models.DateTimeField(db_index=True)

    class Meta:
        ordering = ['-ts']

    def __unicode__(self):
        return u'%s, %f, %f, %f, %s' % (
            self.owner.username,
            self.lat,
            self.lon,
            self.prec,
            str(self.ts),
        )
    def convert_to_epoc(self):
        return int(time.mktime(self.ts.timetuple())*1000)

class FriendShip(models.Model):
    from_friend = models.ForeignKey(User, related_name='friend_set')
    to_friend = models.ForeignKey(User, related_name='to_friend_set')

    def __unicode__(self):
        return u'%s, %s' % (
        self.from_friend.username,
        self.to_friend.username
        )
    class Meta:
        unique_together = (('to_friend', 'from_friend'), )

    @staticmethod
    def isFriend(lhs, rhs):
        try:
            FriendShip.objects.get(from_friend=lhs, to_friend=rhs)
            return True
        except ObjectDoesNotExist,e:
            return False

class CurrentLocation(models.Model):
    loc = models.ForeignKey(Location, related_name='current_location')
    owner = models.ForeignKey(User, related_name='owner', unique=True)

    def __unicode__(self):
        return u'%s, %s' % (
        self.owner.username,
        self.loc
        )

from django.dispatch import receiver
from rest_framework.authtoken.models import Token

@receiver(signals.post_save, sender=User)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)

@receiver(signals.post_save,sender = Location)
def do_current_location(sender, instance=None, created=False, **kwargs):
    if created:
        try:
            curLoc= CurrentLocation.objects.get(
                owner = instance.owner,
            )
        except ObjectDoesNotExist,e:
            curLoc = CurrentLocation(owner = instance.owner)
        finally:
            curLoc.loc = instance
            curLoc.save()

@receiver(signals.post_save,sender=FriendShip)
def create_reverse_friend(sender, instance=None, created=False, **kwargs):
    if created:
        relation, flag = FriendShip.objects.get_or_create(
            to_friend = instance.from_friend,
            from_friend = instance.to_friend,
        )
        relation.save()

