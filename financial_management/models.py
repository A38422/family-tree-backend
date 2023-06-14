from django.db import models

from family_tree_manager.models import FamilyTree


class ContributionLevel(models.Model):
    year = models.PositiveIntegerField(unique=True)
    amount = models.BigIntegerField()
    note = models.TextField(null=True, blank=True)

    def __str__(self):
        return str(self.year)


class Sponsor(models.Model):
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    start_date = models.DateField()
    amount = models.BigIntegerField()

    def __str__(self):
        return self.name


class Income(models.Model):
    date = models.DateField()
    contributor = models.ForeignKey(ContributionLevel, on_delete=models.SET_NULL, blank=True, null=True)
    sponsor = models.ForeignKey(Sponsor, on_delete=models.SET_NULL, blank=True, null=True)
    member = models.ForeignKey(FamilyTree, on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return f'{self.date}'


class ExpenseCategory(models.Model):
    name = models.CharField(max_length=255)
    note = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name


class Expense(models.Model):
    amount = models.BigIntegerField()
    date = models.DateField()
    category = models.ForeignKey(ExpenseCategory, on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return f'{self.amount} - {self.date}'

