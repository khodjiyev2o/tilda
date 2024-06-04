from django.contrib import admin
from . import models


@admin.register(models.PaymentMerchantRequestLog)
class PaymentMerchantRequestLogAdmin(admin.ModelAdmin):
    list_display = ["id", "provider", "type", "response_status_code", "created_at"]
    search_fields = ["id", "body", "header", "response", "method"]
    list_filter = ["provider"]


@admin.register(models.PaidTildaUser)
class PaidTildaUserAdmin(admin.ModelAdmin):
    list_display = ["id", "user_email", "amount", "course_name", "tilda_toggled", "paid_at"]
    search_fields = ["id", "user_email", "course_name"]
    list_filter = ["tilda_toggled", "paid_at"]


@admin.register(models.Tilda)
class TildaAdmin(admin.ModelAdmin):
    list_display = ["id", "project_id", "group_id", "cookie"]
    search_fields = ["id", "cookie"]
    list_filter = ["project_id", "group_id"]


@admin.register(models.TildaRequestResponseLog)
class TildaRequestResponseLogAdmin(admin.ModelAdmin):
    list_display = ["id", "request_body", "type", "status_code", "created_at"]
    search_fields = ["id", "request_body", "response_body"]
    list_filter = ["status_code"]
