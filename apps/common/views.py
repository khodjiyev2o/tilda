from django.db import transaction
from rest_framework.views import APIView
from rest_framework.response import Response
from apps.common.models import PaymentMerchantRequestLog, PaidTildaUser, Tilda


class PaymentView(APIView):
    TYPE: str = ""
    PROVIDER: str = ""

    @transaction.non_atomic_requests
    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        PaymentMerchantRequestLog.objects.create(
            header=self.request.headers,
            body=self.request.data,
            method=self.request.method,
            type=self.TYPE,
            response=response.data,
            response_status_code=response.status_code,
            provider=self.PROVIDER,
        )
        return response


class PaylovSuccessView(PaymentView):

    def post(self, request):
        if request.data['method'] == 'transaction.check':
            self.TYPE = 'transaction.check'
            self.PROVIDER = 'paylov'

            return Response({
                      "jsonrpc": "2.0",
                      "id": request.data['id'],
                      "result": {
                        "status": "0",
                        "statusText": "OK"
                      }
                    })
        elif request.data['method'] == 'transaction.perform':
            self.TYPE = 'transaction.perform'
            self.PROVIDER = 'paylov'
            paid_tilda_user = PaidTildaUser.objects.create(
                user_email=request.data['params']['account']['email'],
                transaction_id=request.data['params']['transaction_id'],
                amount=request.data['params']['amount'],
                course_name=request.data['params']['account']['slug'],
                tilda_toggled=False
            )
            tilda = Tilda.objects.first()
            group_member_tilda_id = tilda.get_tilda_disabled_group_member(
                email=request.data['params']['account']['email'])
            if group_member_tilda_id is None:
                return None
            paid_tilda_user.add_member_to_group(cookie=tilda.cookie, project_id=tilda.project_id,
                                                group_id=tilda.group_id, member_id=group_member_tilda_id)

            paid_tilda_user.tilda_toggled = True
            paid_tilda_user.tilda_id = group_member_tilda_id
            paid_tilda_user.save(update_fields=['tilda_toggled', 'tilda_id'])

            return Response({
                "jsonrpc": "2.0",
                "id": request.data['id'],
                "result": {
                    "status": "0",
                    "statusText": "OK"
                }
            })


