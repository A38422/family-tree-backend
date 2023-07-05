from rest_framework import serializers
from .models import ContributionLevel, Sponsor, Income, ExpenseCategory, Expense


class ContributionLevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContributionLevel
        fields = '__all__'


class SponsorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sponsor
        fields = '__all__'


class IncomeSerializer(serializers.ModelSerializer):
    contributor = serializers.SerializerMethodField()
    sponsor = serializers.SerializerMethodField()
    member = serializers.SerializerMethodField()

    def get_contributor(self, obj):
        if obj.contributor:
            return {
                'id': obj.contributor.id,
                'year': obj.contributor.year,
                'amount': obj.contributor.amount,
                'note': obj.contributor.note,
            }
        return None

    def get_sponsor(self, obj):
        if obj.sponsor:
            return {
                'id': obj.sponsor.id,
                'name': obj.sponsor.name,
                'amount': obj.sponsor.amount,
                'start_date': obj.sponsor.start_date,
            }
        return None

    def get_member(self, obj):
        if obj.member:
            return {
                'id': obj.member.id,
                'name': obj.member.name,
                'img': obj.member.img,
            }
        return None

    class Meta:
        model = Income
        fields = '__all__'


class ExpenseCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ExpenseCategory
        fields = '__all__'


class ExpenseSerializer(serializers.ModelSerializer):
    category = serializers.SerializerMethodField()

    def get_category(self, obj):
        if obj.category:
            return {
                'id': obj.category.id,
                'name': obj.category.name,
            }
        return None

    class Meta:
        model = Expense
        fields = '__all__'

