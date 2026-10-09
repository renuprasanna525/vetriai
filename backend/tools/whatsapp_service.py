import requests
from django.conf import settings


class WhatsAppService:
    """
    Service for sending WhatsApp messages.

    If Meta WhatsApp Cloud API credentials are configured,
    the message is sent through the real Meta API.

    If Meta credentials are not configured, the message is
    handled through a simulated/mock WhatsApp delivery so
    the notification workflow can still be tested locally.
    """

    def __init__(self):
        self.api_url = getattr(settings, "WHATSAPP_API_URL", "")
        self.access_token = getattr(
            settings,
            "WHATSAPP_ACCESS_TOKEN",
            "",
        )
        self.phone_number_id = getattr(
            settings,
            "WHATSAPP_PHONE_NUMBER_ID",
            "",
        )

    def send_message(self, recipient, message):
        """
        Send a WhatsApp text message.

        Uses the real Meta WhatsApp Cloud API when all
        required configuration is available.

        Otherwise, performs a simulated/mock delivery.

        Returns a controlled result dictionary instead of
        raising configuration or API errors to the notification flow.
        """

        if not recipient:
            return {
                "status": "error",
                "message": "WhatsApp recipient is required.",
            }

        if not message:
            return {
                "status": "error",
                "message": "WhatsApp message is required.",
            }

        # ---------------------------------------------------------
        # Mock / simulated WhatsApp delivery
        # ---------------------------------------------------------
        #
        # This allows the notification workflow to be tested
        # without Meta WhatsApp Cloud API credentials.
        #
        # The message is NOT sent to a real WhatsApp account.
        #
        if not self.api_url or not self.access_token or not self.phone_number_id:
            return {
                "status": "simulated",
                "provider": "Mock WhatsApp",
                "message": "WhatsApp notification simulated successfully.",
                "recipient": recipient,
                "notification_message": message,
            }

        # ---------------------------------------------------------
        # Real Meta WhatsApp Cloud API delivery
        # ---------------------------------------------------------

        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }

        payload = {
            "messaging_product": "whatsapp",
            "to": recipient,
            "type": "text",
            "text": {
                "body": message,
            },
        }

        try:
            response = requests.post(
                self.api_url,
                headers=headers,
                json=payload,
                timeout=10,
            )

            if response.ok:
                return {
                    "status": "success",
                    "provider": "Meta WhatsApp Cloud API",
                    "message": "WhatsApp message sent successfully.",
                    "recipient": recipient,
                }

            return {
                "status": "error",
                "provider": "Meta WhatsApp Cloud API",
                "message": (
                    "WhatsApp message failed. "
                    f"HTTP {response.status_code}: {response.text}"
                ),
                "recipient": recipient,
            }

        except requests.RequestException as e:
            return {
                "status": "error",
                "provider": "Meta WhatsApp Cloud API",
                "message": f"WhatsApp request failed: {str(e)}",
                "recipient": recipient,
            }
