from django.shortcuts import render, redirect
from .models import User, GeneratedAccountNumber, Transaction
from decimal import Decimal
from django.http import JsonResponse
from datetime import datetime, date
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.sessions.models import Session
import random, string
from decouple import config

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

sender_email = config('SENDER_EMAIL')
smtp_username = config('SMTP_USERNAME')
sender_password = config('SMTP_PASSWORD')
# recipient_email = 'recipient_email@example.com'

def send_otp_email(sender_email, sender_password, recipient_email, otp):
    smtp_server = config('SMTP_SERVER')  # Change this if using a different email provider
    smtp_port = config("SMTP_PORT")  # Change this if using a different email provider

    # Create a multipart message and set its attributes
    message = MIMEMultipart()
    message['From'] = sender_email
    message['To'] = recipient_email
    message['Subject'] = 'One-Time Password (OTP)'

    # Create the plain text part of the message
    text = f'Your OTP is: {otp}'

    # Attach the plain text message to the multipart message
    message.attach(MIMEText(text, 'plain'))

    # Try to establish a secure connection with the SMTP server
    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_username, sender_password)
        server.sendmail(sender_email, recipient_email, message.as_string())
        server.quit()
        print('OTP email sent successfully.')
        return True
    except Exception as e:
        print('Error sending OTP email:', str(e))
        return False

def generate_reference_id(length=8):
    characters = string.ascii_uppercase + string.ascii_lowercase + string.digits
    reference_id = ''.join(random.choice(characters) for _ in range(length))
    return reference_id

def generate_otp(length):
    digits = "0123456789"
    otp = ""
    for _ in range(length):
        otp += random.choice(digits)
    return otp

def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'
    #     return True
    # else:
    #     return False
current_date = date.today()

@login_required(login_url='login')
def Index(request):
    return render(request, "index.html")

@login_required(login_url='login')
def Home(request):
    transactions = Transaction.objects.filter(user=request.user).order_by("-pk")[:10]
    ctx = {
        "transfers": transactions
    }
    return render(request, "home.html", ctx)

@login_required(login_url='login')
def Profile(request):
    return render(request, "profile.html")

@login_required(login_url='login')
def AccountDetail(request):
    return render(request, "account.html")

@login_required(login_url='login')
def Transactions(request):
    transactions = Transaction.objects.filter(user=request.user).order_by("-pk")
    ctx = {
        "transfers": transactions
    }
    return render(request, "transactions.html", ctx)


@login_required(login_url='login')
def InterBank(request):
    user = request.user
    if is_ajax(request):
        action = request.POST['action']
        if action == "get_data":
            amount = request.POST['amount']
            rec_bank_name = request.POST['rec_bank_name']
            rec_name = request.POST['rec_name']
            rec_acc_number = request.POST['rec_acc_number']
            sender_email = request.user.email
            transfer_type = request.POST['transfer_type']
            description = request.POST['description']
            pin = request.POST['pin']
            amount = Decimal(amount)
            request.session['post_data'] = request.POST

            if pin != request.user.pin:
                msg = {"status": False, "message": "You have entered incorrect transfer pin. Please try again."}
                return JsonResponse(msg)
            if Decimal(amount) < Decimal("600000"):
                msg = {"status": False, "message": "You may not transfer below $600,000. Thank You."}
                return JsonResponse(msg)
            if Decimal(amount) > request.user.amount:
                msg = {"status": False, "message": "Insufficient Balance. You do not have the amount you just requested to transfer."}
                return JsonResponse(msg)
            if request.user.account_status == "Suspend":
                msg = {"status": False, "message": "Account has been suspended. Kindly use the Support Ticket to contact the administrator for the inconvenience."}
                return JsonResponse(msg)
            check_account_number = GeneratedAccountNumber.objects.filter(account_number=rec_acc_number).exists()
            if check_account_number == False:
                msg = {"status": False, "message": "Invalid account number specified."}
                return JsonResponse(msg)
            account = GeneratedAccountNumber.objects.filter(account_number=rec_acc_number).last()
            data = {
                "account_name": account.account_name,
                "account_number": account.account_number,
                "amount": f"{amount:,} USD"
            }
            user.otp = generate_otp(6)
            user.save()
            send_otp_email(sender_email, sender_password, user.email, user.otp)

            msg = {"status": True, "message": "Data fetched", "data": data}
            return JsonResponse(msg)
        elif action == "confirm_data":
            post_data = request.session['post_data']
            amount = Decimal(post_data['amount'])
            otp = request.POST['otp']
            if otp > request.user.otp:
                msg = {"status": False, "message": "You have entered invalid OTP. Please check and try again."}
                return JsonResponse(msg)
            if Decimal(amount) > request.user.amount:
                msg = {"status": False, "message": "Insufficient Balance. You do not have the amount you just requested to transfer."}
                return JsonResponse(msg)
            Transaction.objects.create(
                user=request.user,
                amount=Decimal(post_data['amount']),
                reference=f"EFC{generate_reference_id(12)}",
                status="success",
                transfer_type=post_data['transfer_type'],
                description=post_data['description'],
                sender_email=request.user.email,
                receiver_name=post_data['rec_name'],
                receiver_bank_name=post_data['rec_bank_name'],
                receiver_account_number=post_data['rec_acc_number'],
            )
            user = request.user
            user.amount -= Decimal(post_data['amount'])
            user.account_status = "Suspend"
            user.otp = ""
            user.save()
            msg = {"status": True, "message": f"${amount:,} was transferred successfully."}
            return JsonResponse(msg)

    ctx = {
        "current_date": current_date
    }
    return render(request, "inter.html", ctx)

@login_required(login_url='login')
def OtherBank(request):
    if is_ajax(request):
        action = request.POST['action']
        if action == "get_data":
            amount = request.POST['amount']
            rec_bank_name = request.POST['rec_bank_name']
            rec_name = request.POST['rec_name']
            rec_acc_number = request.POST['rec_acc_number']
            sender_email = request.user.email
            transfer_type = request.POST['transfer_type']
            description = request.POST['description']
            pin = request.POST['pin']
            amount = Decimal(amount)
            request.session['post_data'] = request.POST

            if pin != request.user.pin:
                msg = {"status": False, "message": "You have entered incorrect transfer pin. Please try again."}
                return JsonResponse(msg)
            if Decimal(amount) < Decimal("600000"):
                msg = {"status": False, "message": "You may not transfer below $600,000. Thank You."}
                return JsonResponse(msg)
            if Decimal(amount) > request.user.amount:
                msg = {"status": False, "message": "Insufficient Balance. You do not have the amount you just requested to transfer."}
                return JsonResponse(msg)
            if request.user.account_status == "Suspend":
                msg = {"status": False, "message": "Account has been suspended. Kindly use the Support Ticket to contact the administrator for the inconvenience."}
                return JsonResponse(msg)
            check_account_number = GeneratedAccountNumber.objects.filter(account_number=rec_acc_number).exists()
            if check_account_number == False:
                msg = {"status": False, "message": "Invalid account number specified."}
                return JsonResponse(msg)
            account = GeneratedAccountNumber.objects.filter(account_number=rec_acc_number).last()
            data = {
                "account_name": account.account_name,
                "account_number": account.account_number,
                "amount": f"{amount:,} USD"
            }
            user.otp = generate_otp(6)
            user.save()
            send_otp_email(sender_email, sender_password, user.email, user.otp)

            msg = {"status": True, "message": "Data fetched", "data": data}
            return JsonResponse(msg)
        elif action == "confirm_data":
            post_data = request.session['post_data']
            amount = Decimal(post_data['amount'])
            otp = request.POST['otp']
            if otp > request.user.otp:
                msg = {"status": False, "message": "You have entered invalid OTP. Please check and try again."}
                return JsonResponse(msg)
            if Decimal(amount) > request.user.amount:
                msg = {"status": False, "message": "Insufficient Balance. You do not have the amount you just requested to transfer."}
                return JsonResponse(msg)
            Transaction.objects.create(
                user=request.user,
                amount=Decimal(post_data['amount']),
                reference=f"EFC{generate_reference_id(12)}",
                status="success",
                transfer_type=post_data['transfer_type'],
                description=post_data['description'],
                sender_email=request.user.email,
                receiver_name=post_data['rec_name'],
                receiver_bank_name=post_data['rec_bank_name'],
                bank_branch_code = post_data['swift'],
                receiver_account_number=post_data['rec_acc_number'],
            )
            user = request.user
            user.amount -= Decimal(post_data['amount'])
            user.account_status = "Suspend"
            user.otp = ""
            user.save()
            msg = {"status": True, "message": f"${amount:,} was transferred successfully."}
            return JsonResponse(msg)
    ctx = {
        "current_date": current_date
    }
    return render(request, "other.html", ctx)

@login_required(login_url='login')
def MakeTransfer(request):
    if is_ajax(request):
        action = request.POST['action']
        if action == "get_data":
            amount = request.POST['amount']
            rec_bank_name = request.POST['rec_bank_name']
            rec_name = request.POST['rec_name']
            rec_acc_number = request.POST['rec_acc_number']
            sender_email = request.user.email
            transfer_type = request.POST['transfer_type']
            description = request.POST['description']
            pin = request.POST['pin']
            amount = Decimal(amount)
            request.session['post_data'] = request.POST

            if pin != request.user.pin:
                msg = {"status": False, "message": "You have entered incorrect transfer pin. Please try again."}
                return JsonResponse(msg)
            if Decimal(amount) < Decimal("600000"):
                msg = {"status": False, "message": "You may not transfer below $600,000. Thank You."}
                return JsonResponse(msg)
            if Decimal(amount) > request.user.amount:
                msg = {"status": False, "message": "Insufficient Balance. You do not have the amount you just requested to transfer."}
                return JsonResponse(msg)
            if request.user.account_status == "Suspend":
                msg = {"status": False, "message": "Account has been suspended. Kindly use the Support Ticket to contact the administrator for the inconvenience."}
                return JsonResponse(msg)
            check_account_number = GeneratedAccountNumber.objects.filter(account_number=rec_acc_number).exists()
            if check_account_number == False:
                msg = {"status": False, "message": "Invalid account number specified."}
                return JsonResponse(msg)
            account = GeneratedAccountNumber.objects.filter(account_number=rec_acc_number).last()
            data = {
                "account_name": account.account_name,
                "account_number": account.account_number,
                "amount": f"{amount:,} USD"
            }
            user.otp = generate_otp(6)
            user.save()
            send_otp_email(sender_email, sender_password, user.email, user.otp)

            msg = {"status": True, "message": "Data fetched", "data": data}
            return JsonResponse(msg)
        elif action == "confirm_data":
            post_data = request.session['post_data']
            amount = Decimal(post_data['amount'])
            otp = request.POST['otp']
            if otp > request.user.otp:
                msg = {"status": False, "message": "You have entered invalid OTP. Please check and try again."}
                return JsonResponse(msg)
            if Decimal(amount) > request.user.amount:
                msg = {"status": False, "message": "Insufficient Balance. You do not have the amount you just requested to transfer."}
                return JsonResponse(msg)
            Transaction.objects.create(
                user=request.user,
                amount=Decimal(post_data['amount']),
                reference=f"EFC{generate_reference_id(12)}",
                status="success",
                transfer_type=post_data['transfer_type'],
                description=post_data['description'],
                sender_email=request.user.email,
                receiver_name=post_data['rec_name'],
                receiver_bank_name=post_data['rec_bank_name'],
                routine_number = post_data['swift'],
                country = post_data['country'],
                receiver_account_number=post_data['rec_acc_number'],
            )
            user = request.user
            user.amount -= Decimal(post_data['amount'])
            user.account_status = "Suspend"
            user.otp = ""
            user.save()
            msg = {"status": True, "message": f"${amount:,} was transferred successfully."}
            return JsonResponse(msg)
    ctx = {
        "current_date": current_date
    }
    return render(request, "transfer.html", ctx)

@login_required(login_url='login')
def Withdrawal(request):
    return render(request, "withdrawal.html")

@login_required(login_url='login')
def Deposit(request):
    return render(request, "deposit.html")

@login_required(login_url='login')
def Loan(request):
    return render(request, "loan.html")


def Register(request):
    return render(request, "register.html")

def Login(request):
    if request.user.is_authenticated:
        return redirect("home")
    if is_ajax(request):
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            msg = {"status": True, "message": "Login was successfully. Click OK to continue."}
            return JsonResponse(msg)
        else:
            msg = {"status": False, "message": "Invalid login details supplied. Please try again."}
            return JsonResponse(msg)
    return render(request, "login.html")

def Logout(request):
    logout(request)
    return redirect("index")
