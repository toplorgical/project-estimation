from rest_framework import viewsets, status
from rest_framework.response import Response
from django.http import JsonResponse
from datetime import datetime, timedelta
from rest_framework.views import APIView, exception_handler
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework import serializers, status
from django.contrib.auth.hashers import make_password, check_password
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import UntypedToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError


import hmac
import hashlib
import uuid
import json
from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views import View

from django.conf import settings
import json

from apps.user_auth.models import UserModel
from apps.user_auth.serializers import UserModelSerializer,LoginSerializer
from apps.user_auth.repository import UserRepository
from apps.utils.index import GenerateCode,DecodeToken,GenerateCode, SendMailVerification
from apps.user_auth.services import initialize_payment, verify_payment





class AuthViewSet(viewsets.ViewSet):
    """
    A viewset for managing Institution accounts with CRUD operations.
    Includes custom login and account creation with email verification.
    """
    @action(detail=False, methods=['GET'], url_path='account-info', url_name='account-info')
    @permission_classes([IsAuthenticated])
    def getUserDetails(self, request, pk=None):
        """
        Get auth details by ID

        """
        token = DecodeToken(request)

        pk = token.get("id", None)
        if pk is None:
            return Response(
                {"message": "user not found"},
                status=status.HTTP_400_BAD_REQUEST,
            )
    
        try:
            auth = UserRepository.get_institution_by_id(pk)
            if not auth:
                return Response(
                    {"error": "Institution not found"},
                    status=status.HTTP_404_NOT_FOUND
                )
                
            serializer = UserModelSerializer(auth)
            return Response(serializer.data)
            
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    @action(detail=False, methods=['PUT'], url_path='update-profile', url_name='update-profile')
    @permission_classes([IsAuthenticated])
    def profileUpdate(self, request, pk=None):
        """
        Update auth details
        """
        try:
            token = DecodeToken(request)
            pk = token.get("id", None)
            if not pk:
                return Response({"message": "User not found"}, status=status.HTTP_400_BAD_REQUEST)

            auth = UserRepository.get_institution_by_id(pk)
            if not auth:
                return Response({"error": "Institution not found"}, status=status.HTTP_404_NOT_FOUND)

            serializer = UserModelSerializer(instance=auth, data=request.data, partial=True)
            if serializer.is_valid():
                updated_institution = serializer.save()
                return Response(UserModelSerializer(updated_institution).data, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        

    @action(detail=False, methods=['post'], url_path='change-password', url_name='change-password')
    @permission_classes([IsAuthenticated])
    def change_password(self, request):
        old_password = request.data.get("old_password")
        new_password = request.data.get("new_password")
        token = DecodeToken(request)
        pk = token.get("id", None)
        if not pk:
            return Response({"message": "User not found"}, status=status.HTTP_400_BAD_REQUEST)

        auth = UserRepository.get_institution_by_id(pk)
        if not auth:
            return Response({"error": "Institution not found"}, status=status.HTTP_404_NOT_FOUND)
        try:
            UserModelSerializer.change_password(auth, old_password, new_password)
            return Response({"message": "Password changed successfully"}, status=status.HTTP_200_OK)
        except serializers.ValidationError as e:
            return Response({"error": "invalid password"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




    @action(detail=False, methods=['post'], url_path='forgot-password', url_name='forgot-password')
    def forgot_password(self, request):
        email = request.data.get('email')
        if not email:
            return Response({"message": "Email is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            auth = UserRepository.get_institution_by_email(email)
            if not auth:
                return Response({"message": "Institution not found"}, status=status.HTTP_404_NOT_FOUND)

            verification_code = GenerateCode()

            token = LoginSerializer.get_token(auth, code=verification_code)

            email_data = {
                "id": auth.id,
                "email": auth.email,
                "institution_name": auth.institution_name,
                "verification_code": verification_code
            }

            SendMailVerification(email_data)

            response_data = {
                "token": token,
                "message": "Verification code sent to email."
            }
            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


    @action(detail=False, methods=['post'], url_path='reset-password', url_name='reset-password')
    @permission_classes([IsAuthenticated])
    def ReSetPassword(self, request,*args, **kwargs):
        error = {"message": ""}
        try:
            token = DecodeToken(request)
            new_password = request.data.get("new_password")
            verification_code = token.get("verification_code", None)
            provided_code = request.data.get("verification_code")
            verification_code = str(verification_code)
            provided_code = str(provided_code)

            if not new_password:
                error["message"] = "new password is required"
                return Response(error, status=400)

            if not provided_code:
                error["message"] = "Verification code is required"
                return Response(error, status=400)

            if provided_code != verification_code:
                error["message"] = "Invalid verification code"
                return Response(error, status=400)
            id = token.get("id")
            if not id:
                error["message"] = "The requested auth could not be found"
                return Response(error, status=400)

            updated_institution = UserRepository.reset_password(id, new_password)
            serialized_data = UserModelSerializer(updated_institution).data

           
            return Response({"data": serialized_data}, status=status.HTTP_200_OK)

        except (InvalidToken, TokenError) as e:
            return Response(
                {"message": "Token is invalid or expired", "error": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )
    @action(detail=False, methods=['post'], url_path='email-verification', url_name='email-verification')
    @permission_classes([IsAuthenticated])
    def verificationEmail(self, request, *args, **kwargs):
            try:
                token = DecodeToken(request)

                verification_code = token.get("verification_code", None)
                if verification_code is None:
                    return Response(
                        {"message": "Verification code not found in the token"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                provided_code = request.data.get("verification_code")

                verification_code = str(verification_code)
                provided_code = str(provided_code)
                if provided_code == verification_code:
                    UserRepository.verify_email(token.get("id"))
                    return Response(
                        {"message": "Verification successful"}, status=status.HTTP_200_OK
                    )
                else:
                    return Response(
                        {"message": "Invalid verification code"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
            except (InvalidToken, TokenError) as e:
                return Response(
                    {"message": "Token is invalid or expired", "error": str(e)},
                    status=status.HTTP_400_BAD_REQUEST,
                )








class UserViewSet(viewsets.ViewSet):
    """
    A viewset for managing Authentication Institution accounts with CRUD operations.
    Includes custom login and account creation with email verification.
    """
    @action(detail=False, methods=['post'], url_path='signup', url_name='signup')
    def signup(self, request):
        """
        Create a new auth account with email verification.
        """
        serializer = UserModelSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                serializer.errors, 
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = serializer.save()

            verification_code = GenerateCode()
            token = LoginSerializer.get_token(user, verification_code)
            

            # Prepare email data
            email_data = {
                "id": user.id,
                "email": user.email,
                "institution_name": user.institution_name,
                "verification_code": verification_code
            }
            SendMailVerification(email_data)

            response_data = {
                "token": token,
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "institution_name": user.institution_name
                },
                "message": "Account created successfully. Verification email sent."
            }

            return Response(response_data, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        

    @action(detail=False, methods=['post'], url_path='signin', url_name='signin')
    def signin(self, request):
        """
        Authenticate an auth user
        """

        try:
            user = LoginSerializer.loginUser(request.data)
            if not user:
                return Response(
                    {"error": "Invalid credentials"},
                    status=status.HTTP_401_UNAUTHORIZED
                )
            
            token_data = LoginSerializer.get_token(user)
            return Response(token_data, status=status.HTTP_200_OK)

        except ValidationError as ve:
            return Response(ve.detail, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

 
    @action(detail=False, methods=['post'], url_path='email-verification', url_name='email-verification')
    @permission_classes([IsAuthenticated])
    def verificationEmail(self, request, *args, **kwargs):
            try:
                token = DecodeToken(request)

                verification_code = token.get("verification_code", None)
                if verification_code is None:
                    return Response(
                        {"message": "Verification code not found in the token"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                provided_code = request.data.get("verification_code")

                verification_code = str(verification_code)
                provided_code = str(provided_code)
                if provided_code == verification_code:
                    UserRepository.verify_email(token.get("id"))
                    return Response(
                        {"message": "Verification successful"}, status=status.HTTP_200_OK
                    )
                else:
                    return Response(
                        {"message": "Invalid verification code"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
            except (InvalidToken, TokenError) as e:
                return Response(
                    {"message": "Token is invalid or expired", "error": str(e)},
                    status=status.HTTP_400_BAD_REQUEST,
                )








class PaystackInitView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            token = DecodeToken(request)
            email = token.get("email", None)

            if not email:
                return Response(
                    {"message": "Email not found in the token"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            amount = 1000000 
            reference = str(uuid.uuid4())
            callback_url = "http://localhost:8000/api/paystack/callback/"

            response = initialize_payment(email, amount, reference, callback_url)

            if response.get("status") is True:
                return Response(response, status=status.HTTP_200_OK)
            else:
                return Response(
                    {
                        "message": "Payment initialization failed",
                        "details": response.get("message", "Unknown error"),
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

        except Exception as e:
            return Response(
                {"message": "An error occurred", "error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )



@csrf_exempt
def paystack_webhook(request):
    payload = request.body
    received_signature = request.headers.get("x-paystack-signature")

    if not received_signature:
        return HttpResponse("Missing signature", status=400)

   
    expected_signature = hmac.new(
        key=bytes(settings.PAYSTACK_SECRET_KEY, "utf-8"),
        msg=payload,
        digestmod=hashlib.sha512,
    ).hexdigest()


    if not hmac.compare_digest(received_signature, expected_signature):
        return HttpResponse("Invalid signature", status=401)

    try:
        event = json.loads(payload)
    except ValueError:
        return HttpResponse("Invalid JSON", status=400)

    
    if event.get("event") == "charge.success":
        data = event.get("data", {})
        reference = data.get("reference")
        email = data.get("customer", {}).get("email")
        amount = int(data.get("amount", 0)) / 100

        if not reference or not email:
            return HttpResponse("Missing reference or email", status=400)

        updated = UserRepository.update_subscription(email=email, reference=reference)

        if updated:
            print(f"Payment verified & subscription updated: {reference} | {email} | ₦{amount}")
        else:
            print(f"Subscription update failed for email: {email}")

    return HttpResponse(status=200)



#@shared_task
def run_daily_subscription_deactivation():
    """
    Celery task to deactivate expired institutions by calling the repository method.
    """
    count = UserRepository.deactivate_expired_institutions()
    return f"Deactivated {count} institutions with expired subscriptions"