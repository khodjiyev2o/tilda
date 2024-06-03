import requests

from django.db import models
from django.utils.translation import gettext_lazy as _


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created at"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated at"))

    class Meta:
        abstract = True


class TildaRequestResponseLog(BaseModel):
    request_body = models.TextField(verbose_name=_("Request"))
    request_headers = models.TextField(verbose_name=_("Headers"))
    type = models.CharField(max_length=255, verbose_name=_("Type"))
    response_headers = models.TextField(verbose_name=_("Response Headers"))
    status_code = models.IntegerField(verbose_name=_("Response Status Code"))
    response_body = models.TextField(verbose_name=_("Response"))

    class Meta:
        verbose_name = _("Tilda Request Response Log")
        verbose_name_plural = _("Tilda Request Response Logs")


class Tilda(BaseModel):
    project_id = models.IntegerField(verbose_name=_("Project ID"))
    group_id = models.IntegerField(verbose_name=_("Group ID"))
    cookie = models.TextField(verbose_name=_("Cookie"))

    class Meta:
        verbose_name = _("Tilda")
        verbose_name_plural = _("Tilda")

    def __str__(self):
        return self.cookie

    def get_tilda_disabled_group_member(self, email):
        url = 'https://members.tilda.cc/api/getmembers/'
        headers = {
            'accept': '*/*',
            'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7,uz;q=0.6',
            'content-type': 'text/plain;charset=UTF-8',
            'cookie': self.cookie,
            'origin': 'https://members.tilda.cc',
            'referer': f'https://members.tilda.cc/{self.project_id}/',
            'sec-ch-ua': '"Google Chrome";v="123", "Not:A-Brand";v="8", "Chromium";v="123"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
        }
        data = {
            "groupId": self.group_id,
            "pageSize": 10,
            "status": "disabled",
            "page": 1,
            "sort": "nameAsc",
            "projectId": self.project_id
        }

        response = requests.post(url, headers=headers, json=data)
        TildaRequestResponseLog.objects.create(
            request_body=data,
            request_headers=headers,
            type='getmembers',
            response_headers=response.headers,
            status_code=response.status_code,
            response_body=response.json()
        )
        for member in response.json()['data']['members']:
            if member['login'] == email:
                return member['id']
        return None


class PaymentMerchantRequestLog(BaseModel):
    provider = models.CharField(max_length=63, verbose_name=_("Provider"))
    header = models.TextField(verbose_name=_("Header"))
    body = models.TextField(verbose_name=_("Body"))
    method = models.CharField(verbose_name=_("Method"), max_length=32)
    response = models.TextField(null=True, blank=True)
    response_status_code = models.IntegerField(null=True, blank=True)
    type = models.CharField(max_length=32)

    class Meta:
        verbose_name = _("Payment Merchant Request Log")
        verbose_name_plural = _("Payment Merchant Request Logs")


class PaidTildaUser(BaseModel):
    user_email = models.EmailField(verbose_name=_("User email"))
    transaction_id = models.CharField(verbose_name=_("Transaction ID"), max_length=255)
    amount = models.DecimalField(verbose_name=_("Amount"), max_digits=10, decimal_places=2)
    course_name = models.CharField(verbose_name=_("Course name"), max_length=255)
    tilda_toggled = models.BooleanField(verbose_name=_("Tilda toggled"))
    tilda_id = models.IntegerField(verbose_name=_("Tilda ID"), null=True, blank=True)
    paid_at = models.DateTimeField(verbose_name=_("Paid at"), auto_now_add=True)

    class Meta:
        verbose_name = _("Paid Tilda User")
        verbose_name_plural = _("Paid Tilda Users")

    def add_member_to_group(self, cookie, project_id, group_id, member_id):
        url = 'https://members.tilda.cc/api/addmembertogroup/'
        headers = {
            'accept': '*/*',
            'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7,uz;q=0.6',
            'content-type': 'text/plain;charset=UTF-8',
            'cookie': cookie,
            'origin': 'https://members.tilda.cc',
            'referer': f'https://members.tilda.cc/{project_id}/',
            'sec-ch-ua': '"Google Chrome";v="123", "Not:A-Brand";v="8", "Chromium";v="123"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
        }
        data = {
            "groupId": group_id,
            "memberId": member_id,
            "projectId": project_id
        }
        response = requests.post(url, headers=headers, json=data)
        TildaRequestResponseLog.objects.create(
            request_body=data,
            request_headers=headers,
            type='add_member',
            response_headers=response.headers,
            status_code=response.status_code,
            response_body=response.json()
        )
        return response.json()

