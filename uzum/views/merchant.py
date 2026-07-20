from uzum.views.base import BaseUzumWebHookAPIView


class UzumWebHookAPIView(BaseUzumWebHookAPIView):
    """
    Override these methods to handle Uzum payment events.
    """

    def handle_check(self, params, result, *args, **kwargs):
        print(f"Uzum check: {params}")

    def handle_created_payment(self, params, result, *args, **kwargs):
        print(f"Uzum transaction created: {params}")

    def handle_successfully_payment(self, params, result, *args, **kwargs):
        print(f"Uzum payment confirmed: {params}")

    def handle_cancelled_payment(self, params, result, *args, **kwargs):
        print(f"Uzum payment reversed: {params}")
