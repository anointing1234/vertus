from django.shortcuts import render,get_object_or_404, redirect
from django.urls import reverse
# from .form import RegisterForm,LoginForm,SendresetcodeForm,PasswordResetForm,ReviewForm 
from django.http import JsonResponse
import requests 
from decimal import Decimal, InvalidOperation
import logging
import traceback
import json
from django.utils.timezone import now
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.shortcuts import redirect
from django.contrib.auth import logout as auth_logout,login,authenticate
from django.contrib.auth import get_user_model
from django.utils.crypto import get_random_string
from django.core.mail import EmailMessage
from django.contrib.auth import get_user_model
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal,InvalidOperation
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.conf.urls.static import static
from django.core.mail import EmailMultiAlternatives
import pytz
from datetime import datetime, timedelta
from pytz import timezone as pytz_timezone
import logging
from django.db import transaction
from django.db.models import F,Sum
from django.contrib.auth.decorators import login_required
import logging
from django.core.mail import send_mail
from django.views.decorators.http import require_POST
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
import random
from django.contrib.auth.hashers import make_password

logger = logging.getLogger(__name__)

User = get_user_model()





def contact_view(request):
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid payload.'}, status=400)

    name      = data.get('name', '').strip()
    email     = data.get('email', '').strip()
    check_in  = data.get('phone', '').strip()
    check_out = data.get('subject', '').strip()
    message   = data.get('textarea', '').strip()

    if not all([name, email, check_in, check_out, message]):
        return JsonResponse({'success': False, 'error': 'All fields are required.'})

    subject = f"[Vertus Hotel & Suite] Availability request from {name}"
    plain = (
        f"Name: {name}\n"
        f"Email: {email}\n"
        f"Check In: {check_in}\n"
        f"Check Out: {check_out}\n\n"
        f"Message:\n{message}"
    )
    html = f"""
    <html><body style="font-family:Arial,sans-serif;color:#333;">
      <div style="max-width:600px;margin:auto;padding:20px;border:1px solid #ddd;">
        <h2 style="color:#004e64;text-align:center;">
          New Availability Request
        </h2>
        <p><strong>Guest Name:</strong> {name}</p>
        <p><strong>Email:</strong> {email}</p>
        <p><strong>Check In:</strong> {check_in}</p>
        <p><strong>Check Out:</strong> {check_out}</p>
        <hr>
        <p>{message}</p>
        <p style="margin-top:30px;font-size:0.9em;color:#555;">
          Thank you for choosing <strong>Vertus Hotel & Suite</strong>.
        </p>
      </div>
    </body></html>
    """

    try:
        send_mail(
            subject,
            plain,
            settings.EMAIL_HOST_USER,
            [settings.DEFAULT_FROM_EMAIL],  # to your admin inbox
            html_message=html,
            fail_silently=False,
        )
    except Exception:
        logger.exception("Failed to send availability email")
        return JsonResponse({
            'success': False,
            'error': 'Unable to send your request right now. Please try again later.'
        }, status=500)

    return JsonResponse({
        'success': True,
        'message': 'Thank you! Your request has been sent to Vertus Hotel & Suite.'
    })





def contacts_view(request):
    if request.method != "POST":
        return JsonResponse({'success': False, 'error': 'Invalid HTTP method.'}, status=405)

    # 1. Parse JSON
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON payload.'}, status=400)

    # 2. Extract & strip all six fields
    name      = data.get('name', '').strip()
    email     = data.get('email', '').strip()
    check_in  = data.get('check_in', '').strip()
    check_out = data.get('check_out', '').strip()
    guests    = data.get('guests', '').strip()
    room      = data.get('room', '').strip()      # ← matches <select name="room">

    # 3. Validate
    if not all([name, email, check_in, check_out, guests, room]):
        return JsonResponse({
            'success': False,
            'error': 'All fields (name, email, check-in, check-out, guests, room) are required.'
        }, status=400)

    # 4. Build subject & bodies (now including room)
    subject = f"[Vertus Hotel & Suite] Booking Request from {name}"
    plain = (
        f"Dear Admin,\n\n"
        f"You have received a new booking request from {name}.\n\n"
        f"Guest Information:\n"
        f"  Name:       {name}\n"
        f"  Email:      {email}\n"
        f"  Room:  {room}\n"
        f"  Check-In:   {check_in}\n"
        f"  Check-Out:  {check_out}\n"
        f"  Guests:     {guests}\n\n"
        f"Please take action on this request as soon as possible.\n\n"
        f"Vertus Hotel & Suite"
    )
    html = f"""
    <html><body style="font-family:Arial,sans-serif;color:#333;">
      <div style="max-width:600px;margin:auto;padding:20px;border:1px solid #ddd;">
        <h2 style="color:#004e64;text-align:center;">New Booking Request</h2>
        <p><strong>Guest Name:</strong> {name}</p>
        <p><strong>Email:</strong> {email}</p>
        <p><strong>Room:</strong> {room}</p>
        <p><strong>Check-In Date:</strong> {check_in}</p>
        <p><strong>Check-Out Date:</strong> {check_out}</p>
        <p><strong>Number of Guests:</strong> {guests}</p>
        <hr>
        <p style="margin-top:30px;font-size:0.9em;color:#555;">
          Thank you for choosing <strong>Vertus Hotel & Suite</strong>. We look forward to welcoming you!
        </p>
      </div>
    </body></html>
    """

    # 5. Send emails
    try:
        # Admin email address – define in settings.py:
        #   ADMIN_EMAIL = 'reservations@vertushotel.online'
        admin_email = getattr(settings, 'ADMIN_EMAIL', settings.EMAIL_HOST_USER)

        send_mail(
            subject=subject,
            message=plain,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[admin_email],
            html_message=html,
            fail_silently=False,
        )

        # Confirmation to guest
        subject_user = "Booking Confirmation from Vertus Hotel & Suite"
        plain_user = (
            f"Dear {name},\n\n"
            f"Thank you for your booking request at Vertus Hotel & Suite.\n\n"
            f"Your request details:\n"
            f"  Room :  {room}\n"
            f"  Check-In:   {check_in}\n"
            f"  Check-Out:  {check_out}\n"
            f"  Guests:     {guests}\n\n"
            f"We will reach out shortly to confirm availability and rates.\n\n"
            f"Best regards,\n"
            f"Vertus Hotel & Suite Team"
        )
        html_user = f"""
        <html><body style="font-family:Arial,sans-serif;color:#333;">
          <div style="max-width:600px;margin:auto;padding:20px;border:1px solid #ddd;">
            <h2 style="color:#004e64;text-align:center;">Booking Confirmation</h2>
            <p><strong>Guest Name:</strong> {name}</p>
            <p><strong>Room:</strong> {room}</p>
            <p><strong>Check-In Date:</strong> {check_in}</p>
            <p><strong>Check-Out Date:</strong> {check_out}</p>
            <p><strong>Number of Guests:</strong> {guests}</p>
            <hr>
            <p style="margin-top:30px;font-size:0.9em;color:#555;">
              We’ll be in touch soon to finalize your booking. Thanks for choosing us!
            </p>
          </div>
        </body></html>
        """
        send_mail(
            subject=subject_user,
            message=plain_user,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            html_message=html_user,
            fail_silently=False,
        )

    except Exception:
        logger.exception("Failed to send emails")
        return JsonResponse({
            'success': False,
            'error': 'Unable to process your request right now. Please try again later.'
        }, status=500)

    return JsonResponse({
        'success': True,
        'message': 'Thank you! Your booking request has been sent, and a confirmation email is on its way.'
    })





def submit_comment(request):
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON.'}, status=400)

    name    = data.get('name', '').strip()
    email   = data.get('email', '').strip()
    phone   = data.get('phone', '').strip()
    message = data.get('message', '').strip()

    if not all([name, email, phone, message]):
        return JsonResponse({'success': False, 'error': 'All fields are required.'}, status=400)

    # --- Prepare Admin Email ---
    admin_subject = f"[Vertus Hotel & Suites] New Comment from {name}"
    admin_plain = (
        f"Name: {name}\n"
        f"Email: {email}\n"
        f"Phone: {phone}\n\n"
        f"Comment:\n{message}"
    )
    admin_html = f"""
    <html>
    <body style="margin:0;padding:0;font-family:Arial,sans-serif;background:#f4f4f4;">
      <table width="100%" cellpadding="0" cellspacing="0">
        <tr><td align="center">
          <table width="600" cellpadding="0" cellspacing="0" style="background:#ffffff;border-radius:8px;overflow:hidden;">
            <tr>
              <td style="background:#004e64;padding:20px;text-align:center;">
                <h1 style="color:#ffffff;margin:0;font-size:24px;">New Comment Received</h1>
              </td>
            </tr>
            <tr>
              <td style="padding:20px;color:#333333;">
                <p><strong>From:</strong> {name} &lt;{email}&gt;</p>
                <p><strong>Phone:</strong> {phone or 'N/A'}</p>
                <hr style="border:none;border-top:1px solid #dddddd;margin:20px 0;">
                <p style="line-height:1.5em;">{message}</p>
              </td>
            </tr>
            <tr>
              <td style="background:#f9f9f9;padding:15px;text-align:center;color:#777777;font-size:12px;">
                Vertus Hotel & Suites — Benin City<br>
                <a href="mailto:{settings.DEFAULT_FROM_EMAIL}" style="color:#004e64;text-decoration:none;">{settings.DEFAULT_FROM_EMAIL}</a>
              </td>
            </tr>
          </table>
        </td></tr>
      </table>
    </body>
    </html>
    """

    # --- Prepare User Confirmation Email ---
    user_subject = "Thank you for your comment – Vertus Hotel & Suites"
    user_plain = (
        f"Dear {name},\n\n"
        "Thank you for leaving your comment with us. We appreciate your feedback and will review it shortly.\n\n"
        "Warm regards,\n"
        "Vertus Hotel & Suites Team"
    )
    user_html = f"""
    <html>
    <body style="margin:0;padding:0;font-family:Arial,sans-serif;background:#f4f4f4;">
      <table width="100%" cellpadding="0" cellspacing="0">
        <tr><td align="center">
          <table width="600" cellpadding="0" cellspacing="0" style="background:#ffffff;border-radius:8px;overflow:hidden;">
            <tr>
              <td style="background:#004e64;padding:20px;text-align:center;">
                <h1 style="color:#ffffff;margin:0;font-size:24px;">Thank You, {name}!</h1>
              </td>
            </tr>
            <tr>
              <td style="padding:20px;color:#333333;">
                <p>We have received your comment:</p>
                <blockquote style="border-left:4px solid #FFD700;padding-left:15px;color:#555555;">
                  {message}
                </blockquote>
                <p>We appreciate your feedback and will get back to you if needed.</p>
                <p style="margin-top:20px;">Best regards,<br><strong>Vertus Hotel & Suites Team</strong></p>
              </td>
            </tr>
            <tr>
              <td style="background:#f9f9f9;padding:15px;text-align:center;color:#777777;font-size:12px;">
                <a href="https://vertushotelsuite.com" style="color:#004e64;text-decoration:none;">Visit our website</a>
              </td>
            </tr>
          </table>
        </td></tr>
      </table>
    </body>
    </html>
    """

    try:
        # Send to admin
        send_mail(
            admin_subject,
            admin_plain,
            settings.EMAIL_HOST_USER,
            [settings.DEFAULT_FROM_EMAIL],
            html_message=admin_html,
            fail_silently=False,
        )

        # Send confirmation to user
        user_email = EmailMultiAlternatives(
            subject=user_subject,
            body=user_plain,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[email],
        )
        user_email.attach_alternative(user_html, "text/html")
        user_email.send()

    except Exception:
        logger.exception("Comment email failed")
        return JsonResponse({
            'success': False,
            'error': 'Could not send comment at this time. Please try again later.'
        }, status=500)

    return JsonResponse({
        'success': True,
        'message': 'Thank you! Your comment has been submitted.'
    })


def send_message(request):
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON.'}, status=400)

    name    = data.get('name', '').strip()
    email   = data.get('email', '').strip()
    subject = data.get('subject', '').strip()
    phone   = data.get('phone', '').strip()
    message = data.get('message', '').strip()

    if not all([name, email, subject, message]):
        return JsonResponse({
            'success': False,
            'error': 'Name, email, subject, and message are required.'
        }, status=400)

    # --- Email to Admin ---
    admin_subject = f"[Vertus Hotel & Suites] New Inquiry: {subject}"
    admin_plain = (
        f"Name: {name}\nEmail: {email}\nPhone: {phone}\n\nMessage:\n{message}"
    )
    admin_html = f"""
    <html>
    <body style="margin:0;padding:0;font-family:Arial,sans-serif;background:#f4f4f4;">
      <table width="100%" cellpadding="0" cellspacing="0">
        <tr><td align="center">
          <table width="600" cellpadding="0" cellspacing="0" style="background:#ffffff;border-radius:8px;overflow:hidden;">
            <tr>
              <td style="background:#004e64;padding:20px;text-align:center;">
                <h1 style="color:#ffffff;margin:0;font-size:24px;">New Contact Inquiry</h1>
              </td>
            </tr>
            <tr>
              <td style="padding:20px;color:#333333;">
                <p><strong>Subject:</strong> {subject}</p>
                <p><strong>From:</strong> {name} &lt;{email}&gt;</p>
                <p><strong>Phone:</strong> {phone or 'N/A'}</p>
                <hr style="border:none;border-top:1px solid #dddddd;margin:20px 0;">
                <p style="line-height:1.5em;">{message}</p>
              </td>
            </tr>
            <tr>
              <td style="background:#f9f9f9;padding:15px;text-align:center;color:#777777;font-size:12px;">
                Vertus Hotel & Suites — Benin City<br>
                <a href="mailto:{settings.DEFAULT_FROM_EMAIL}" style="color:#004e64;text-decoration:none;">{settings.DEFAULT_FROM_EMAIL}</a>
              </td>
            </tr>
          </table>
        </td></tr>
      </table>
    </body>
    </html>
    """

    # --- Confirmation Email to User ---
    user_subject = "Thank you for contacting Vertus Hotel & Suites"
    user_plain = (
        f"Dear {name},\n\n"
        "Thank you for your message. We have received your inquiry and will be in touch soon.\n\n"
        "Best regards,\nVertus Hotel & Suites Team"
    )
    user_html = f"""
    <html>
    <body style="margin:0;padding:0;font-family:Arial,sans-serif;background:#f4f4f4;">
      <table width="100%" cellpadding="0" cellspacing="0">
        <tr><td align="center">
          <table width="600" cellpadding="0" cellspacing="0" style="background:#ffffff;border-radius:8px;overflow:hidden;">
            <tr>
              <td style="background:#004e64;padding:20px;text-align:center;">
                <h1 style="color:#ffffff;margin:0;font-size:24px;">Thank You, {name}!</h1>
              </td>
            </tr>
            <tr>
              <td style="padding:20px;color:#333333;">
                <p>We have received your message:</p>
                <blockquote style="border-left:4px solid #FFD700;padding-left:15px;color:#555555;">
                  {message}
                </blockquote>
                <p>Our team will get back to you at <strong>{email}</strong> shortly.</p>
                <p style="margin-top:20px;">Warm regards,<br><strong>Vertus Hotel & Suites Team</strong></p>
              </td>
            </tr>
            <tr>
              <td style="background:#f9f9f9;padding:15px;text-align:center;color:#777777;font-size:12px;">
                <a href="https://vertushotelsuite.com" style="color:#004e64;text-decoration:none;">Visit our website</a>
              </td>
            </tr>
          </table>
        </td></tr>
      </table>
    </body>
    </html>
    """

    try:
        # Send admin email
        send_mail(
            admin_subject,
            admin_plain,
            settings.EMAIL_HOST_USER,
            [settings.DEFAULT_FROM_EMAIL],
            html_message=admin_html,
            fail_silently=False,
        )

        # Send user confirmation
        user_email = EmailMultiAlternatives(
            subject=user_subject,
            body=user_plain,
            from_email=settings.EMAIL_HOST_USER,
            to=[email],
        )
        user_email.attach_alternative(user_html, "text/html")
        user_email.send()

    except Exception:
        logger.exception("Failed to send contact form emails")
        return JsonResponse({
            'success': False,
            'error': 'Failed to send message. Please try again later.'
        }, status=500)

    return JsonResponse({
        'success': True,
        'message': 'Your message has been sent successfully!'
    })


def book_views(request):
    return render(request,'home/book.html')    
