from django.contrib import admin
from .models import User, GeneratedAccountNumber, Transaction
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .forms import UserAdminCreationForm, UserAdminChangeForm, VirtualAccountForm

# Remove Group Model from admin. We're not using it.
admin.site.unregister(Group)

class UserAdmin(BaseUserAdmin):
    # The forms to add and change user instances
    form = UserAdminChangeForm
    add_form = UserAdminCreationForm

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = ['email', 'username', 'first_name', 'last_name']
    list_filter = ['email']
    fieldsets = (
        ('Login Details', {'fields': ('username', 'email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'mobile', 'gender', 'amount', 'account_name', 'account_number', 'bank_branch_code', 'account_type', 'account_status')}),
        ('Extra Information', {'fields': ('address', 'city', 'state', 'zip_code', 'country', 'photo', 'pin')}),
    )
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = (
        ("Login Details", {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password', 'password_2')}
        ),
        ('Personal info', {'fields': ('first_name', 'last_name', 'mobile', 'gender', 'amount', 'account_name', 'account_number', 'bank_branch_code', 'account_type', 'account_status')}),
        ('Extra Information', {'fields': ('address', 'city', 'state', 'zip_code', 'country', 'photo', 'pin')}),
    )
    search_fields = ['email']
    ordering = ['email']
    filter_horizontal = ()


admin.site.register(User, UserAdmin)
admin.site.register(Transaction)


@admin.register(GeneratedAccountNumber)
class VirtualAccountAdmin(admin.ModelAdmin):
    form = VirtualAccountForm

