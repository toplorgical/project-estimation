# call the utils here
from rest_framework.pagination import PageNumberPagination
import random
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response


from rest_framework_simplejwt.tokens import UntypedToken
from ipware import get_client_ip
from django.http import JsonResponse
import requests
import httpagentparser
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
from django.conf import settings
import os
from django.conf import settings
from rest_framework_simplejwt.tokens import UntypedToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError



#environment = settings.ENVIRONMENT




configuration = sib_api_v3_sdk.Configuration()
configuration.api_key["api-key"] = settings.EMAIL_API_KEY

verification_template_path = os.path.join("apps", "templates", "verification.html")
transaction_confirmation_template_path = os.path.join("Outocsat", "templates", "confirmation.html")


def SendMailVerification(email_details):
    try:
        with open(verification_template_path, "r") as file:
            html_content = file.read()
        html_content = html_content.replace("{{ name }}", email_details["institution_name"])
        html_content = html_content.replace("{{ code }}", str(email_details['verification_code']))
        api_instance = sib_api_v3_sdk.TransactionalEmailsApi(
            sib_api_v3_sdk.ApiClient(configuration)
        )
        send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
            to=[{"email": email_details["email"]}],
            sender={"name": "TopLorgical", "email": "dev.team@toplorgical.com"},
            subject="Verification Code",
            html_content=html_content,
        )
        try:
            response = api_instance.send_transac_email(send_smtp_email)
            print(response)
            return response
        except ApiException as e:
            print(f"Exception when sending email: {e}")
            return None
    except FileNotFoundError:
        print(f"Template file not found: {verification_template_path}")
        return None







# ip, is_routable = get_client_ip(request)
def get_user_location(request):
    ip = "41.203.78.171"
    #if environment == "production":
    ip, is_routable = get_client_ip(request)
    user_agent = request.META.get("HTTP_USER_AGENT", "")
    device_info = httpagentparser.detect(user_agent)
    if ip is None:
        return JsonResponse({"error": "Unable to get the client's IP address"})
    try:
        response = requests.get(f"https://ipinfo.io/{ip}/json")
        location = response.json()
        location["user_agent"] = user_agent
        location["platform"] = device_info.get("platform", {"name": "N/A"})
        location["browser"] = device_info.get("browser", {"name": "N/A"})

    except requests.RequestException as e:
        return JsonResponse({"error": str(e)})

    return location


class CustomPageNumberPagination(PageNumberPagination):
    page_size_query_param = "limit"
    max_page_size = 100

    def get_page_size(self, request):
        limit = request.query_params.get("limit")
        if limit:
            try:
                return min(int(limit), self.max_page_size)
            except ValueError:
                pass
        return super().get_page_size(request)


def GenerateCode():
    return random.randint(100000, 999999)



def DecodeToken(request):
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token_str = auth_header.split(" ")[1]
        try:
            token = UntypedToken(token_str)
            return token.payload  # important: return payload, not token object
        except (InvalidToken, TokenError) as e:
            print("Token error:", str(e))
            return None
    return None


