from django.db import models

from django.contrib.auth.models import User
from django.db.models import Q
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.exceptions import ValidationError

from .validators import phone_regex


class FamilyTree(models.Model):
    id = models.AutoField(primary_key=True)
    mid = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='children',
                            db_index=True)
    fid = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='spouses',
                            db_index=True)
    pids = models.ManyToManyField('self', blank=True, related_name='parents')
    gender = models.CharField(max_length=10)
    name = models.CharField(max_length=255)
    img = models.TextField(null=True, blank=True)
    bdate = models.DateField()
    ddate = models.DateField(null=True, blank=True)
    phone = models.CharField(max_length=11, validators=[phone_regex], blank=True, null=True)
    email = models.EmailField(max_length=50, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    family_info = models.TextField(blank=True, null=True)
    generation = models.PositiveIntegerField(default=1)
    user = models.OneToOneField(User, on_delete=models.CASCADE, blank=True, null=True)
    is_admin = models.BooleanField(default=False, blank=True, null=True)
    EDUCATION_CHOICES = (
        ('none', 'Không có'),
        ('elementary', 'Tiểu học'),
        ('middle_school', 'Trung học cơ sở'),
        ('high_school', 'Trung học phổ thông'),
        ('college', 'Cao đẳng'),
        ('university', 'Đại học'),
        ('engineer', 'Kỹ sư'),
        ('doctorate', 'Tiến sĩ'),
        ('master', 'Thạc sĩ'),
    )
    education = models.CharField(max_length=20, choices=EDUCATION_CHOICES, default='none', blank=True, null=True)
    achievement = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        # self.save_base(*args, **kwargs)

        if not self.id:
            self.id = FamilyTree.objects.order_by('-id').first().id + 1

        if self.mid or self.fid:
            max_generation = \
                FamilyTree.objects.filter(id__in=[self.mid.id, self.fid.id]).aggregate(
                    max_generation=models.Max('generation'))[
                    'max_generation']
            self.generation = max_generation + 1 if max_generation is not None else 1
        elif self.pids and self.pids.count() == 1:
            for pid in self.pids.all():
                if pid.mid or pid.fid:
                    max_generation = \
                        FamilyTree.objects.filter(id__in=[pid.mid.id, pid.fid.id]).aggregate(
                            max_generation=models.Max('generation'))[
                            'max_generation']
                    self.generation = max_generation + 1 if max_generation is not None else 1
                else:
                    self.generation = 1

        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # Kiểm tra xem đối tượng này có được liên kết làm fid hoặc mid cho đối tượng khác không
        if FamilyTree.objects.filter(Q(fid=self) | Q(mid=self)).exists():
            # Nếu có, không cho phép xóa đối tượng
            raise ValidationError(
                "Không được xóa đối tượng này")
        else:
            super().delete(*args, **kwargs)

    def __str__(self):
        return self.name


# @receiver(post_save, sender=FamilyTree)
# def create_user_and_assign_role(sender, instance, created, **kwargs):
#     if created:
#         username = f"user{instance.id}"
#         # password = User.objects.make_random_password()
#         password = 'Ab@123456'
#
#         if instance.is_admin:
#             user = User.objects.create_superuser(username=username, password=password)
#         else:
#             user = User.objects.create_user(username=username, password=password)
#
#         instance.user = user
#         instance.save()
#

@receiver(post_delete, sender=FamilyTree)
def delete_user(sender, instance, **kwargs):
    if instance.user:
        instance.user.delete()

