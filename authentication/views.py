from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
from syslogin import settings
from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
from django.utils.encoding import force_bytes,force_str
from .tokens import generate_token
from django.core.mail import EmailMessage,send_mail

# Create your views here.
def home(request):
    return (render(request,"authentication/index.html"))
def signin(request):
    var=0
    if request.method=='POST':
        username=request.POST['username']
        pass1=request.POST['pass1']
        user=authenticate(username=username,password=pass1)
        
        if user is not None:
            login(request,user)
            fname=user.first_name
            var=1
            d={"fname":fname,
            "var":var}
            return render(request,"authentication/index.html",context=d)
        else:
            messages.error(request,"Bad Credentials!")
            return redirect('home')

    return(render(request,"authentication/signin.html",{"var":var}))
def signup(request):

    if request.method=="POST":
        username=request.POST['username']
        fname=request.POST['fname']
        lname=request.POST['lname']
        email=request.POST['email']
        pass1=request.POST['pass1']
        pass1_=request.POST['pass1_']
        if pass1==pass1_:
            '''
            if User.objects.filter(username=username).exists():
                messages.info(request,'Username already Exists. Kindly provide another User Name')
                return redirect('signup')
        
            elif User.objects.filter(email=email).exists():
                
                messages.info(request,'Email already Exists. Kindly provide another Email')
                return redirect('signup')
            '''
        else:
            messages.info(request,'Passwords not matching. Kindly check and re-enter')
            return redirect('signup')
        myuser=User.objects.create_user(username,email,pass1)
        myuser.first_name=fname
        myuser.last_name=lname
        myuser.is_active=False
        myuser.save()
        messages.success(request,"Your Account has been successfully created. We have sent you a conformation  Email. Please confirm your Email to activate your account")
        sub="Welcome to Login System!!"
        mes="Hello"+myuser.first_name+"!!\n"+"Thank You for visiting  our website \"System Login\" We have sent you a conformation mail. Please confirm your Email in order to activate your account on System Login \n\n Thank You \n "+myuser.first_name
        from_email=settings.EMAIL_HOST_USER
        to_list=[myuser.email]
        send_mail(sub,mes,from_email,to_list,fail_silently=True)

        current_site=get_current_site(request)
        email_subject="Confirm your email @ Login System"
        message2=render_to_string('authentication/email_conf.html',{
            'name':myuser.first_name,
            'domain':current_site.domain,
            'uid':urlsafe_base64_encode(force_bytes(myuser.pk)),
            'token':generate_token.make_token(myuser)} )
        email=EmailMessage(
            email_subject,message2,settings.EMAIL_HOST_USER,[myuser.email])
        email.fail_silently=True
        email.send() 
        return redirect("signin")
    return render(request,"authentication/signup.html")
def signout(request):
    logout(request)
    messages.success(request,"signed out successfully")
    return redirect('home')
def activate(request,uidb64,token):
    try:
        uid=force_str(urlsafe_base64_decode(uidb64))
        myuser=User.objects.get(pk=uid)
    except(TypeError,ValueError,OverflowError,User.DoesNotExist):
        myuser=None
    if myuser:
        myuser.is_active=True
        myuser.save()
        login(request,myuser)
        return redirect('home')
    else:
        return render(request,'authentication/activation_failed.html')