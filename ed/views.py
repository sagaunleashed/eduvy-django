import re
from django.core import paginator
from django.shortcuts import render,redirect
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import  auth
from django.contrib.auth.decorators import login_required, user_passes_test
from users.models import NewUser
from ed. models import College,collegeBranch,collegeCourse, courseType,otherFeeStructure
from ed.models import Institution,Branch, Students,SupportingDoc,Course, feeStructure,introBanner,instituteBanner,planBanner,Staff,instituteBranch,institutionCourse
from django.contrib import messages
from django.core.mail import send_mail
import pymongo,json
from django.http import JsonResponse,HttpResponse
from django.conf import settings
import datetime,os
from django.core.paginator import EmptyPage, InvalidPage, Paginator
from django.core import serializers
from django.contrib.auth.models import Group,Permission
# import pandas as pd
import csv

from django import template

# Create your views here.
@login_required(login_url="login")
def index(request):
    
    request.session['title'] = "Best ERP System"
    if request.user.email:
        return redirect("dashboard")
    else:
        return login(request)


@csrf_exempt
def login(request):
    try:
        if request.method == "POST":
            username = request.POST["username"]
            password = request.POST["password"]
            user = auth.authenticate(username=username, password=password)
            request.session['defaultinstitute'] = 1
            request.session['defaultcollege'] = 0
            if user is not None:
                auth.login(request, user)
                return redirect("dashboard")
            else:
                messages.info(request, "Invalid Credentials")
                return redirect("login")
        else:

            return render(request, "index.html")
    except:
        return render(request, "index.html")


def logout(request):
    auth.logout(request)
    return redirect("/")


@login_required(login_url="login")
def dashboard(request):
    users  = Institution.objects.all()
    user = [[1,'All Institutions']]
    try:
        for i in users:
            z = []
            z.append(i.user.id)
            z.append(i.name)
            user.append(z)
        print(z)
    except Exception as e:
        print(str(e))
    request.session['institution'] = user
    request.session['title'] = "Dashboard"
    # request.session['title'] = users
    print(user)
    return render(request, "dashboard.html")

def institution_dropdown(request):
    users  = Institution.objects.all()
    user = [[1,'All Institutions']]
    try:
        for i in users:
            z = []
            z.append(i.user.id)
            z.append(i.name)
            user.append(z)
    except Exception as e:
        print(str(e))
    request.session['institution'] = user
    return request.session['institution']

@csrf_exempt
def change_institution(request):
    if request.method == "POST":
        institution = request.POST['institution'] 
        print(institution) 
        del request.session['defaultinstitute']  
        request.session['defaultinstitute']  = 1 
        request.session['defaultinstitute'] = institution 
        print(request.session['defaultinstitute']  )
        print('------------------------------------')
        print(request.session['defaultinstitute'])
        return HttpResponse("sucess")
        
    

def send_email(subject, body, email):
    try:
        email_msg = EmailMessage(subject, body, settings.EMAIL_HOST_USER, [settings.EMAIL_HOST_USER], reply_to=[email])
        email_msg.send()
        return "Message sent :)"
    except:
        return redirect('dashboard')


@login_required(login_url="login")
def institution(request):
    request.session['title'] = "Institution"
    try:
        if request.method == "POST":
            name = request.POST['institution_name']
            institution_code = request.POST['institution_code']
            state = request.POST['state']
            city = request.POST['city']
            address = request.POST['address']
            chairman_name = request.POST['chairman_name']
            contact_person_name = request.POST['contact_person_name']
            contact_person_email = request.POST['contact_person_email']
            contact_person_phone = request.POST['contact_person_phone']
            ct = request.POST['course_type']
            institution_image = request.FILES['institution_image']
            status = request.POST['status']
            
            randompass = NewUser.objects.make_random_password()
            print(randompass)
            userreg = NewUser(email = contact_person_email,is_institute = True,is_active =True) 
            userreg.set_password(123)     
            print("user set")
            InstituteSave = Institution(user = userreg, institutionCode = institution_code,courseType = ct, name = name, chairmanName = chairman_name, contactPersonEmail = contact_person_email, contactPersonName = contact_person_name, contactPersonPhone = contact_person_phone, address = address, image = institution_image , Status = status, cityId = city, stateID = state,)
            print(InstituteSave)
            try:
                group = request.POST['group']
                print(group)
                print(type(group))
                if int(group) == 1:
                    InstituteSave.is_group = True
                else:
                    pass
            except:
                pass
            userreg.save()
            InstituteSave.save()
            messages.success(request, "Institute added successfully!")
            subject = 'welcome to Eduvy'
            message = f'Hi, thank you for registering in Eduvy.Your Password is {randompass}'
            email_from = settings.EMAIL_HOST_USER
            recipient_list = [contact_person_email, ]
            send_mail( subject, message, email_from, recipient_list )
            institution_dropdown(request)
            return redirect(institution)
    except Exception :
        institutes = Institution.objects.all().order_by('id')
        paginator = Paginator(institutes,10)
        try:
            page = int(request.GET.get('page','1'))
        except:
            page = 1
        try:
            institute = paginator.page(page)
        except(EmptyPage,InvalidPage):
            institute = paginator.page(paginator.num_pages) 
        return render(request,'institutions.html',{'institute':institute})
    if request.user.is_superuser:
        institutes = Institution.objects.all().order_by('id')
        paginator = Paginator(institutes,10)
        try:
            page = int(request.GET.get('page','1'))
        except:
            page = 1
        try:
            institute = paginator.page(page)
        except(EmptyPage,InvalidPage):
            institute = paginator.page(paginator.num_pages) 
        institution_dropdown(request)
        ct = courseType.objects.all()
        return render(request,'institutions.html',{'institute':institute,'ct':ct})

@csrf_exempt
def statecity(request):
    if request.method == "POST":
        state_id = request.POST['state_id']
        client = pymongo.MongoClient("mongodb://localhost:27017/")
        # Database Name
        db = client["eduvytest"]
        
        # Collection Name
        con = db["cities"]
        myquery = { "stateId": state_id }
        x = con.find(myquery)
        city= []
        for data in x:
            cityid  = data['id']
            cityName = data['city']
            c = {"id" : cityid,"city" : cityName}
            city.append(c)
        print(city)
        data = json.dumps(city)
        return HttpResponse(data)
    return redirect('institution')

@login_required(login_url="login")
@csrf_exempt
def branch(request):
    request.session['title'] = "Branch"
    if request.method == "POST":
        BranchCode = request.POST["branch_code"]
        Branchname = request.POST["branch_name"]
        Image = request.FILES["branch_image"]
        print(Image)
        Status = request.POST["status"]
        BranchSave = Branch(BranchCode=BranchCode, BranchName=Branchname, Status=Status)
        BranchSave.save()
        BranchSave.Image = Image
        BranchSave.save()
        messages.success(request, "Branch added successfully!")
        return redirect('branch')
        
    bran = Branch.objects.all().order_by('DateofJoin', 'id')
    paginator = Paginator(bran,10)
    try:
        page = int(request.GET.get('page','1'))
    except:
        page = 1
    try:
        branch = paginator.page(page)
    except(EmptyPage,InvalidPage):
        branch = paginator.page(paginator.num_pages)
    return render(request, "branch.html", {"branches": branch})


@login_required(login_url="login")
@csrf_exempt
def course(request):
    request.session['title'] = "Course"
    try:
        if request.method == "POST":
            BranchID = request.POST['branch_id']
            CourseCode = request.POST["course_code"]
            Coursename = request.POST["course_name"]
            Coursetype = request.POST["course_type"]
            Duration = request.POST['duration']
            Descrip = request.POST['description']
            Image = request.FILES["course_image"]
            Status = request.POST["status"]
            print("hello")
            Doc = request.POST.getlist("documents[]")
            print(Doc)
            branch = Branch.objects.get(id = BranchID)
            document = ""
            for i in Doc:
                document = document + i
                print(document)            
                document = document + ","

            CourseSave = Course(
                Branch=branch, CourseCode=CourseCode, CourseName=Coursename, CourseType=Coursetype,CourseDuration=Duration, CourseDescription = Descrip, SupDoc = document, CourseImage = Image, Status = Status
            )
            CourseSave.save()
            messages.success(request, "Course added successfully!")
            
            return redirect("course")
    except Exception as e:
        messages.warning(request, 'Your account expires in three days.')
        print("Oops!", e.__class__, "occurred.")
    courses = Course.objects.all().order_by('id')
    paginator = Paginator(courses,10)
    try:
        page = int(request.GET.get('page',1))
    except:
        page = 1
    try:
        course = paginator.page(page)
    except(EmptyPage,InvalidPage):
        course = paginator.page(paginator.num_pages)
    # print(course)
    branch = Branch.objects.all()
    sup = SupportingDoc.objects.all()
    ct = courseType.objects.all()
    context = {"course" : course,"branch" : branch,"sup" : sup,'ct':ct}
    return render(request, "course.html", context)

@csrf_exempt
def delete_branch(request):
    if request.method == "POST":
        id = request.POST["id"]
        instance = Branch.objects.get(id=id)
        if len(instance.Image) > 0:
            os.remove(instance.Image.path)
        instance.delete()
        messages.warning(request, "Branch deleted successfully!")
        # return redirect(branch)
        data = {
        'is_taken': "deleted"
        }
        
        return JsonResponse(data)
    return redirect(branch)


@csrf_exempt
def delete_insitute_course(request):
    if request.method == "POST":
        id = request.POST["id"]
        instance = institutionCourse.objects.get(id=id)
        instance.delete()
        messages.warning(request, "Institute course deleted successfully!")
        # return redirect(branch)
        data = {
        'is_taken': "deleted"
        }
        
        return JsonResponse(data)
    return redirect(institutecourse)

@csrf_exempt
def delete_institutebranch(request):
    if request.method == "POST":
        id = request.POST["id"]
        instance = instituteBranch.objects.filter(id=id)
        instance.delete()
        messages.warning(request, "Institute branch deleted successfully!")
        # return redirect(branch)
        data = {
        'is_taken': "deleted"
        }
        
        return JsonResponse(data)
    return redirect(instituteBranch)

@csrf_exempt
def delete_institutebanner(request):
    if request.method == "POST":
        id = request.POST["id"]
        instance = instituteBanner.objects.get(id=id)
        if len(instance.Image) > 0:
            os.remove(instance.Image.path)
        instance.delete()
        messages.warning(request, "Institute Banner deleted successfully!")
        # return redirect(branch)
        data = {
        'is_taken': "deleted"
        }
        
        return JsonResponse(data)
    return redirect(institutebanner)


@csrf_exempt
def delete_introbanner(request):
    if request.method == "POST":
        id = request.POST["id"]
        instance = introBanner.objects.get(id=id)
        if len(instance.Image) > 0:
            os.remove(instance.Image.path)
        instance.delete()
        messages.warning(request, "Intro Banner deleted successfully!")
        # return redirect(branch)
        data = {
        'is_taken': "deleted"
        }
        
        return JsonResponse(data)
    return redirect(introbanner)


@csrf_exempt
def delete_institute(request):
    if request.method == "POST":
        id = request.POST["id"]
        instance = Institution.objects.get(id=id)
        try:
            if len(instance.image) > 0:
                os.remove(instance.image.path)
        except:
            pass
        # instance.delete()
        userDelete = NewUser.objects.get(id = instance.user.id) 
        userDelete.delete()
        messages.warning(request, "Institute deleted successfully!")
        print(institution_dropdown())
        # return redirect(branch)
        data = {
        'is_taken': "deleted"
        }
        
        institution_dropdown(request)
        return redirect(institution)

@csrf_exempt
def delete_course(request):
    if request.method == "POST":
        id = request.POST["id"]
        print(id)
        instance = Course.objects.get(id=id)
        if len(instance.CourseImage) > 0:
            os.remove(instance.CourseImage.path)
        instance.delete()
        messages.warning(request, "Course deleted successfully!")
        return redirect(branch)
        # data = true
        # return JsonResponse(data)
    return redirect(branch)


@csrf_exempt
def list_branch(request):
    if request.method == "POST":
        id = request.POST['id']
        instance = Branch.objects.filter(id=id).values()
        Code = instance[0]['BranchCode']
        Name = instance[0]['BranchName']
        Image = instance[0]['Image']
        Status = instance[0]['Status']
        ID = instance[0]['id']
        print(Code)
        context = [ID,Code,Name,Image,Status]
        data = json.dumps(context)
        return HttpResponse(data)

@csrf_exempt
def list_staff(request):
    if request.method == "POST":
        id = request.POST['id']
        instance = Staff.objects.filter(id=id).values()
        Name = instance[0]['name']
        fatehrName = instance[0]['fatehrName']
        email = instance[0]['email']
        phone = instance[0]['phone']
        dob = instance[0]['DOB']
        gender = instance[0]['gender']
        marital = instance[0]['maritalStatus']
        nationality = instance[0]['nationality']
        anuual_salary = instance[0]['annualSalary']
        designation = instance[0]['designation']
        branch = instance[0]['branchId']
        aadhaarNumber = instance[0]['aadhaarNumber']
        panNumber = instance[0]['panNumber']
        DateofJoin = instance[0]['DateofJoin']
        id = instance[0]['id']
        Image = instance[0]['image']        
        Status = instance[0]['Status']
        context = [Name,fatehrName,email,phone,dob,gender,marital,nationality,anuual_salary,designation,branch,aadhaarNumber,panNumber,DateofJoin,id,Image,Status]
        print(context)
        def myconverter(o):
            if isinstance(o, datetime.datetime):
                return o.__str__()
        data = json.dumps(context,default = myconverter)
        return HttpResponse(data)

@csrf_exempt
def list_institute(request):
    if request.method == "POST":
        id = request.POST['id']
        instance = Institution.objects.filter(id=id).values()
        Name = instance[0]['name']
        State = instance[0]['stateID']
        City = instance[0]['cityId']
        Address = instance[0]['address']
        Chairman = instance[0]['chairmanName']
        Chairperson = instance[0]['contactPersonName']
        email = instance[0]['contactPersonEmail']
        phone = instance[0]['contactPersonPhone']
        image = instance[0]['image']
        Status = instance[0]['Status']
        ID = instance[0]['id']
        institutionCode = instance[0]['institutionCode']
        ct = instance[0]['courseType']
        group = instance[0]['is_group']
        print(ct)
        context = [ID,Name,State,City,Address,Chairman,Chairperson,email,phone,image,Status,institutionCode,group,ct]
        data = json.dumps(context)
        return HttpResponse(data)


@csrf_exempt
def list_course(request):
    if request.method == "POST":
        id = request.POST['id']
        instance = Course.objects.filter(id=id).values()
        print(instance)
        Code = instance[0]['CourseCode']
        Name = instance[0]['CourseName']
        branch_id = instance[0]['Branch_id']
        duration = instance[0]['CourseDuration']
        document = instance[0]['SupDoc']
        ct = instance[0]['CourseType']
        desc = instance[0]['CourseDescription']
        Image = instance[0]['CourseImage']
        Status = instance[0]['Status']
        ID = instance[0]['id']
        context = [ID,Code,Name,branch_id,duration,desc,Image,Status,document,ct]
        print(context)
        data = json.dumps(context)
        return HttpResponse(data)
    return HttpResponse("hello")


@csrf_exempt
def list_doc(request):
    if request.method == "POST":
        id = request.POST['id']
        instance = SupportingDoc.objects.filter(id=id).values()
        Name = instance[0]['DocumentName']
        Status = instance[0]['Status']
        ID = instance[0]['id']
        context = [Name,Status,ID]
        print(context)
        data = json.dumps(context)
        return HttpResponse(data)
    return HttpResponse("hello")

@csrf_exempt
def list_planbanner(request):
    if request.method == "POST":
        id = request.POST['id']
        instance = planBanner.objects.filter(id=id).values()
        Image = instance[0]['Image']
        Title = instance[0]['Title']
        Description = instance[0]['Description']
        Status = instance[0]['Status']
        ID = instance[0]['id']
        context = [ID,Image,Title,Description,Status]
        print(context)
        data = json.dumps(context)
        return HttpResponse(data)
    return HttpResponse("hello")

@csrf_exempt
def list_introbanner(request):
    if request.method == "POST":
        id = request.POST['id']
        instance = introBanner.objects.filter(id=id).values()
        Image = instance[0]['Image']
        Title = instance[0]['Title']
        Description = instance[0]['Description']
        Status = instance[0]['Status']
        ID = instance[0]['id']
        context = [ID,Image,Title,Description,Status]
        print(context)
        data = json.dumps(context)
        return HttpResponse(data)
    return HttpResponse("hello")

@csrf_exempt
def list_institutebanner(request):
    if request.method == "POST":
        id = request.POST['id']
        instance = instituteBanner.objects.filter(id=id).values()
        Image = instance[0]['Image']
        Title = instance[0]['Title']
        Status = instance[0]['Status']
        ID = instance[0]['id']
        context = [ID,Image,Title,Status]
        print(context)
        data = json.dumps(context)
        return HttpResponse(data)
    return HttpResponse("hello")


@csrf_exempt 
def update_branch(request):

    if request.method == "POST":
        ID = request.POST['_id']
        code = request.POST['branch_code']
        Name = request.POST['branch_name']
        branch = Branch.objects.get(id = ID)
        status = request.POST['status']
        if len(request.FILES) != 0:
            if len(branch.Image) > 0:
                os.remove(branch.Image.path)
            branch.Image = request.FILES['branch_image_up']
        branch.BranchName = Name
        branch.BranchCode = code
        branch.Status = status
        branch.save()
        messages.warning(request, "Branch updated successfully!")

    return redirect('branch')

@csrf_exempt 
def update_institute(request):

    if request.method == "POST":
        ID = request.POST['_id']
        branch = Institution.objects.get(id = ID)
        name = request.POST['institution_name']
        code = request.POST['institution_code']
        state = request.POST['state']
        city = request.POST['city']
        address = request.POST['address']
        chairman_name = request.POST['chairman_name']
        contact_person_name = request.POST['contact_person_name']
        contact_person_email = request.POST['contact_person_email']
        contact_person_phone = request.POST['contact_person_phone']
        
        ct = request.POST.getlist("course_type[]")
        print(ct)
        course_types = ""
        for i in ct:
            course_types = course_types + i
            print(course_types)            
        if len(request.FILES) != 0:
            if len(branch.image) > 0:
                os.remove(branch.image.path)
            branch.image = request.FILES['institution_image']
        status = request.POST['status']
        branch.institutionCode  = code
        branch.contactPersonEmail  = contact_person_email
        branch.name = name
        branch.stateID = state
        branch.cityId = city
        branch.address = address
        branch.chairmanName = chairman_name
        branch.contactPersonName = contact_person_name
        branch.contactPersonPhone = contact_person_phone
        branch.Status = status
        branch.courseType = course_types
        try:
            group = request.POST['group']
            if int(group) == 1:
                branch.is_group = True
            else:
                branch.is_group = False
        except:
            pass
        
        branch.save()
        messages.warning(request, "Institute updated successfully!")
        # new = NewUser.objects.filter(email = contact_person_email)
    return redirect('institution')


@csrf_exempt     
def update_course(request):

    if request.method == "POST":
        ID = request.POST['id']
        ID = int(ID)
        branchid = request.POST['branch_id']
        branch = Course.objects.get(id = ID)
        b = Branch.objects.get(id = branchid)
        code = request.POST['course_code']
        Name = request.POST['course_name']
        Duruation = request.POST['duration']
        ct = request.POST['course_type']
        description = request.POST['description']
        Doc = request.POST.getlist("documents[]")
        print(Doc)
        document = ""
        for i in Doc:
            document = document + i
            print(document)            
            document = document + ","
        print(document)
        if len(request.FILES) != 0:
            try:
                if len(branch.CourseImage) > 0:
                    os.remove(branch.CourseImage.path)
            except:
                pass
            branch.CourseImage = request.FILES['course_image']
        status = request.POST['status']
        branch.CourseName = Name
        branch.Branch = b
        branch.CourseDuration = Duruation
        branch.CourseDescription = description
        branch.SupDoc = document
        branch.CourseCode = code
        branch.CourseType = ct
        branch.Status = status
        branch.save()
        messages.warning(request, "Course updated successfully!")

    return redirect('course')

@csrf_exempt 
def update_doc(request):

    if request.method == "POST":
        ID = request.POST['_id']
        
        Name = request.POST['name']
        status = request.POST['status']
        doc = SupportingDoc.objects.get(id = ID)
        doc.DocumentName = Name
        doc.Status = status
        doc.save()
        messages.warning(request, "Supporting document updated successfully!")

    return redirect('supporting_documents')


@login_required(login_url="login")
@csrf_exempt 
def supporting_documents(request):
    
    request.session['title'] = "Supporting Documents"
    if request.method == "POST":
        DocName = request.POST['name']
        Status = request.POST['status']
        sup_doc = SupportingDoc(DocumentName = DocName, Status = Status)
        sup_doc.save()
        return redirect(supporting_documents)
    sup_document = SupportingDoc.objects.all().order_by('id')
    paginator = Paginator(sup_document,10)
    try:
        page = int(request.GET.get('page','1'))
    except:
        page = 1
    try:
        sup_doc = paginator.page(page)
    except(EmptyPage,InvalidPage):
        sup_doc = paginator.page(paginator.num_pages)
    return render(request,"supporting-document.html",{'sup_doc': sup_doc})

@csrf_exempt
def delete_supporting_doc(request):
    if request.method == "POST":
        id = request.POST["id"]
        instance = SupportingDoc.objects.filter(id=id)
        instance.delete()
        messages.warning(request, "supporting document deleted successfully!")
        # return redirect(branch)
        data = {
        'is_taken': "deleted"
        }
        
        return JsonResponse(data)
    return redirect(supporting_documents)

@login_required(login_url="login")
@csrf_exempt
def introbanner(request):    
    request.session['title'] = "Intro Banner"
    if request.method == "POST":
        Image = request.FILES['intro_banner_image']
        Title = request.POST['title']
        Desc = request.POST['description']
        status = request.POST['status']
        introsave = introBanner(Title = Title, Description = Desc, Status = status, Image = Image)
        introsave.save()
        return redirect(introbanner)
    
    intr  = introBanner.objects.all().order_by('id')
    paginator = Paginator(intr,8)
    try:
        page = int(request.GET.get('page','1'))
    except:
        page = 1
    try:
        intro = paginator.page(page)
    except(EmptyPage,InvalidPage):
        intro = paginator.page(paginator.num_pages)
    return render(request,"intro-banner.html",{'intro': intro})


@login_required(login_url="login")
@csrf_exempt
def planbanner(request):
    request.session['title'] = "Plan Banner"
    if request.method == "POST":
        Image = request.FILES['intro_banner_image']
        Title = request.POST['title']
        Desc = request.POST['description']
        status = request.POST['status']
        plansave = planBanner(Title = Title, Description = Desc, Status = status, Image = Image)
        plansave.save()
        return redirect(planbanner)
    
    pla  = planBanner.objects.all().order_by('id')
    paginator = Paginator(pla,8)
    try:
        page = int(request.GET.get('page','1'))
    except:
        page = 1
    try:
        plan = paginator.page(page)
    except(EmptyPage,InvalidPage):
        plan = paginator.page(paginator.num_pages)
    return render(request,"plan-banner.html",{'plan': plan})

@login_required(login_url="login")
@csrf_exempt
def institutebanner(request):
    request.session['title'] = "Institute Banner"
    if request.method == "POST":
        if request.user.is_superuser:
            userid = request.session['defaultinstitute']
            userid = int(userid)
            Image = request.FILES['banner_image']
            Title = request.POST['title']
            status = request.POST['status']
            institutesave = instituteBanner(user = userid, Title = Title,Status = status, Image = Image)
            institutesave.save()
            return redirect(institutebanner)
        elif request.user.is_institute:
            userid = request.user.id
            insti = Institution.objects.get( user = userid)
            Image = request.FILES['banner_image']
            Title = request.POST['title']
            status = request.POST['status']
            institutesave = instituteBanner(user = insti.id, Title = Title,Status = status, Image = Image)
            institutesave.save()
            return redirect(institutebanner)
        else:
            return HttpResponse('You dont have enough permission')
    if request.user.is_superuser:
        userid = request.session['defaultinstitute']
        userid = int(userid)
        if userid == 1:
            insti = instituteBanner.objects.all().order_by('id')
        else:
            insti = instituteBanner.objects.filter(user = userid)
        paginator = Paginator(insti,8)
        try:
            page = int(request.GET.get('page','1'))
        except:
            page = 1
        try:
            institute = paginator.page(page)
        except(EmptyPage,InvalidPage):
            institute = paginator.page(paginator.num_pages)
        return render(request,"institute-banner.html",{'institute': institute})
    elif request.user.is_institute:
        insti  = instituteBanner.objects.filter(user=request.user.id)
        paginator = Paginator(insti,8)
        try:
            page = int(request.GET.get('page','1'))
        except:
            page = 1
        try:
            institute = paginator.page(page)
        except(EmptyPage,InvalidPage):
            institute = paginator.page(paginator.num_pages)
        return render(request,"institute-banner.html",{'institute': institute})
    else:
        return HttpResponse('You dont have enough permission')


@csrf_exempt
def delete_planbanner(request):
    if request.method == "POST":
        id = request.POST["id"]
        instance = planBanner.objects.get(id=id)
        if len(instance.Image) > 0:
            os.remove(instance.Image.path)
        instance.delete()
        messages.warning(request, "Plan banner deleted successfully!")
        # return redirect(branch)
        data = {
        'is_taken': "deleted"
        }
        
        return JsonResponse(data)
    return redirect(planbanner)


@csrf_exempt
def delete_staff(request):
    if request.method == "POST":
        id = request.POST["id"]
        instance = Staff.objects.get(id=id)
        if len(instance.image) > 0:
            os.remove(instance.image.path)
        users = NewUser.objects.get(id = instance.email)
        # return redirect(branch)
        data = {
        'is_taken': "deleted"
        }
        messages.warning(request, "Staff deleted successfully!")
        return JsonResponse(data)
    return redirect(planbanner)

@login_required(login_url="login")
@csrf_exempt
def profile(request):
    if request.method == "POST":
        ID = request.POST['_id']
        name = request.POST['name']
        address = request.POST['address']
        chairman_name = request.POST['chairman_name']
        contact_person_name = request.POST['contact_person_name']
        contact_person_email = request.POST['contact_person_email']
        contact_person_phone = request.POST['contact_person_phone']
        description = request.POST['description']
        print(ID)
        branch = Institution.objects.get(id = ID)
        # if len(request.FILES['brochure']) != 0:
        #     brochures = request.FILES['brochure']
        #     if len(branch.brochure) > 0:
        #         os.remove(branch.brochure.path)
        #     branch.brochure = brochures
        # if len(request.FILES['institution_logo']) != 0:
        #     logos = request.FILES['institution_logo']
        #     if len(branch.logo) > 0:
        #         os.remove(branch.logo.path)
        #     branch.logo = logos
        status = request.POST['status']
        branch.contactPersonEmail  = contact_person_email
        branch.name = name
        branch.address = address
        branch.chairmanName = chairman_name
        branch.contactPersonName = contact_person_name
        branch.contactPersonPhone = contact_person_phone
        # branch.image = institution_image
        branch.Status = status
        branch.description = description
        # branch.brochure = brochure
        branch.save()
        return redirect('profile')
    if request.user.is_superuser:
        print(type(request.session['defaultinstitute']))
        if request.session['defaultinstitute'] == 1 :
            user = ""
            context = {'user' : user}
            return render(request,'profile.html',context)
        else:
            print(type(request.session['defaultinstitute']))
            user = Institution.objects.get(user = request.session['defaultinstitute'])
            context = {'user' : user}
            return render(request,'profile.html',context)
    elif request.user.is_institute:        
        user = Institution.objects.get(user = request.user.id)
        context = {'user' : user}
        return render(request,'profile.html',context)
    elif request.user.is_institute_staff:        
        user = Staff.objects.get(user = request.user.id)
        context = {'user' : user}
        return render(request,'profile.html',context)
    elif request.user.is_student:        
        user = Students.objects.get(user = request.user.id)
        context = {'user' : user}
        return render(request,'profile.html',context)

@csrf_exempt
def update_planbanner(request):
    if request.method == "POST":
        ID = request.POST['id']
        ID = request.POST['id']
        Title = request.POST['title']
        Description = request.POST['description']
        status = request.POST['status']
        branch = planBanner.objects.get(id = ID)
        if len(request.FILES) != 0:
            Image = request.FILES['intro_banner_image']
            if len(branch.Image) > 0:
                os.remove(branch.Image.path)
            branch.Image = Image
        branch.Title= Title
        branch.Description = Description
        branch.Status = status
        branch.save()
        messages.warning(request, "Plan banner updated successfully!")
        return redirect(planbanner)
    return redirect(planbanner)

@csrf_exempt
def update_introbanner(request):
    if request.method == "POST":
        ID = request.POST['id']
        Title = request.POST['title']
        Description = request.POST['description']
        status = request.POST['status']
        branch = introBanner.objects.get(id = ID)
        if len(request.FILES) != 0:
            Image = request.FILES['intro_banner_image']
            if len(branch.Image) > 0:
                os.remove(branch.Image.path)
            branch.Image = Image
        branch.Title= Title
        branch.Description = Description
        branch.Status = status
        branch.save()
        messages.warning(request, "Intro banner updated successfully!")
        return redirect(introbanner)
    return redirect(introbanner)
    
@csrf_exempt
def update_institutebanner(request):
    if request.method == "POST":
        ID = request.POST['id']
        Title = request.POST['title']
        status = request.POST['status']
        branch = instituteBanner.objects.get(id = ID)
        if len(request.FILES) != 0:
            Image = request.FILES['banner_image']
            if len(branch.Image) > 0:
                os.remove(branch.Image.path)
            branch.Image = Image
        branch.Title= Title
        branch.Status = status
        branch.save()
        messages.warning(request, "Institute banner updated successfully!")
        return redirect(institutebanner)
    return redirect(institutebanner)

@login_required(login_url="login")
@csrf_exempt
def college(request):
    request.session['title'] = "Colleges"
    if request.method == "POST":
        try:
            userid = int(request.session['defaultinstitute'])
            user = NewUser.objects.get(id = userid)
            institute = Institution.objects.get(user = user)
            name = request.POST['institution_name']
            institution_code = request.POST['institution_code']
            state = request.POST['state']
            city = request.POST['city']
            address = request.POST['address']
            chairman_name = request.POST['chairman_name']
            contact_person_name = request.POST['contact_person_name']
            contact_person_email = request.POST['contact_person_email']
            contact_person_phone = request.POST['contact_person_phone']
            institution_image = request.FILES['institution_image']
            status = request.POST['status']
            
            randompass = NewUser.objects.make_random_password()
            print(randompass)
            userreg = NewUser(email = contact_person_email,is_college = True,is_active =True) 
            userreg.set_password(123)     
            InstituteSave = College(user = userreg,institution = institute, code = institution_code, name = name, chairmanName = chairman_name, contactPersonEmail = contact_person_email, contactPersonName = contact_person_name, contactPersonPhone = contact_person_phone, address = address, image = institution_image , Status = status, cityId = city, stateID = state,)
            userreg.save()
            print('user created')
            print(InstituteSave)
            InstituteSave.save()
            messages.success(request, "Institute added successfully!")
            subject = 'welcome to Eduvy'
            message = f'Hi, thank you for registering in Eduvy.Your Password is {randompass}'
            email_from = settings.EMAIL_HOST_USER
            recipient_list = [contact_person_email, ]
            send_mail( subject, message, email_from, recipient_list )
            return redirect('college')
        except:
            return HttpResponse('Eroor')
        
        
    if request.user.is_superuser:  
        if int(request.session['defaultinstitute']) > 1:      
            userids= int(request.session['defaultinstitute'])
            user = NewUser.objects.get(id = userids)
            institute = Institution.objects.get(user = user)
            if institute.is_group == True:
                
                college = College.objects.filter(institution = institute)
                return render(request,'college.html',{'college':college})
            else:                
                messages.warning(request, "This Institute is not a Group")
                return redirect('dashboard')
        else:
            messages.warning(request, "Change to Institution")
            return redirect('dashboard')
            
    if request.user.is_institute:
        user = NewUser.objects.get(id = request.user.id)
        institute = Institution.objects.get(user = user)
        if institute.is_group == True:
            return render(request,'college.html')
        
        else:
            return HttpResponse("not a Group")


@login_required(login_url="login")
@csrf_exempt
def staff(request):    
    request.session['title'] = "Staff"
    try:
        if request.method == "POST":
            if request.user.is_superuser:
                image = request.FILES['staff_image']
                name = request.POST['name']
                father_name = request.POST['father_name']
                email = request.POST['email']
                phone = request.POST['phone']
                dob = request.POST['dob']
                gender = request.POST['gender']
                marital_status = request.POST['marital_status']
                nationality = request.POST['nationality']
                annual_salary = request.POST['annual_salary']
                designation = request.POST['designation']
                branch = request.POST['branch']
                aadhaar_number = request.POST['aadhaar_number']
                pan_number = request.POST['pan_number']
                join_date = request.POST['join_date']
                status = request.POST['status']        
                randompass = NewUser.objects.make_random_password()
                print(randompass)
                userreg = NewUser(email = email,is_institute_staff = True,is_active =True) 
                userreg.set_password(randompass)     
                userreg.save()
                userids= int(request.session['defaultinstitute'])
                insti = Institution.objects.get( user = userids)       
                print("-----------------")           
                staffSave = Staff(
                    institutionID = insti,
                    image = image,
                    name = name,
                    fatehrName = father_name,
                    nationality= nationality,
                    email = email,
                    phone = phone,
                    DOB= dob,
                    gender = gender,
                    maritalStatus = marital_status,
                    annualSalary = annual_salary, 
                    designation = designation, 
                    branchId = branch, 
                    aadhaarNumber = aadhaar_number, 
                    panNumber = pan_number,
                    DateofJoin = join_date,
                    Status = status)
                staffSave.save()
                subject = 'welcome to Eduvy'
                message = f'Hi, thank you for registering in Eduvy.Your Password is {randompass}'
                email_from = settings.EMAIL_HOST_USER
                recipient_list = [email, ]
                send_mail( subject, message, email_from, recipient_list )
                return redirect('staff')
            elif request.user.is_institute:
                image = request.FILES['staff_image']
                name = request.POST['name']
                father_name = request.POST['father_name']
                email = request.POST['email']
                phone = request.POST['phone']
                dob = request.POST['dob']
                gender = request.POST['gender']
                marital_status = request.POST['marital_status']
                nationality = request.POST['nationality']
                annual_salary = request.POST['annual_salary']
                designation = request.POST['designation']
                branch = request.POST['branch']
                aadhaar_number = request.POST['aadhaar_number']
                pan_number = request.POST['pan_number']
                join_date = request.POST['join_date']
                status = request.POST['status']        
                randompass = NewUser.objects.make_random_password()
                print(randompass)
                userreg = NewUser(email = email,is_institute_staff = True,is_active =True) 
                userreg.set_password(randompass)     
                userreg.save()                
                insti = Institution.objects.get( user = request.user.id)  
                subject = 'welcome to Eduvy'
                message = f'Hi, thank you for registering in Eduvy.Your Password is {randompass}'
                email_from = settings.EMAIL_HOST_USER
                recipient_list = [email, ]
                send_mail( subject, message, email_from, recipient_list )
                staffSave = Staff(
                    institutionID = insti,
                    image = image,
                    name = name,
                    fatehrName = father_name,
                    nationality= nationality,
                    email = email,
                    phone = phone,
                    DOB= dob,
                    gender = gender,
                    maritalStatus = marital_status,
                    annualSalary = annual_salary, 
                    designation = designation, 
                    branchId = branch, 
                    aadhaarNumber = aadhaar_number, 
                    panNumber = pan_number,
                    DateofJoin = join_date,
                    Status = status)
                staffSave.save()
                return redirect('staff')
            else:
                return HttpResponse('Not have enough permission')
    except Exception as e:
        messages.warning(request, 'Some Error Occured')
        print("Oops!", e.__class__, "occurred.")
    if request.user.is_superuser:
        user = request.session['defaultinstitute']
        userid = int(user)
        if userid == 1:
            staff = Staff.objects.all()
            branch = Branch.objects.all()
            context = {'staff':staff,'branch':branch}
        elif userid > 1:
            insti = Institution.objects.get( user = userid)  
            staff = Staff.objects.filter(institutionID = insti.id)
            instibranch = instituteBranch.objects.filter(institutionId_id = insti.id)
            branch = Branch.objects.all()
            context = {'staff':staff,'branch':branch,'instibranch':instibranch}
        return render(request,'staff.html',context)
    elif request.user.is_institute:
        staff = Staff.objects.filter( institutionID = request.user.id)
        print(staff)
        branch = Branch.objects.all()
        context = {
            'staff':staff,
            # 'branch':branch
            }
        return render(request,'staff.html',context)
    else:
        return HttpResponse('Not have enough permission')

@login_required(login_url="login")
@csrf_exempt
def institute_branch(request):
    if request.method == 'POST':
        if request.user.is_superuser:                
            id_b = request.POST['id']
            id_b = json.loads(id_b)
            print(type(id_b))
            print(id_b)
            id = request.session['defaultinstitute']
            if int(id) > 1:
                instiid = Institution.objects.get(user = int(id))
                instibran = instituteBranch.objects.filter(institutionId = instiid.id) 
                instibranid = []
                for i in instibran:
                    idb = i.branchId.id
                    instibranid.append(idb)
                                
            for i in id_b:
                if i in instibranid:
                    pass
                else:
                    bran = Branch.objects.get(id = i)
                    instiid = Institution.objects.get( user = id)   
                    instbranch = instituteBranch(institutionId = instiid,branchCode = bran.BranchCode,branchId = bran,Status=bran.Status)
                    instbranch.save()
            print("saved")
            return redirect(institute_branch)
        
        elif request.user.is_institute:      
            id_b = request.POST['id']
            id_b = json.loads(id_b)
            print(type(id_b))
            print(id_b)
            id = request.user.id
            instiid = Institution.objects.get( user = id)   
            for i in id_b:
                bran = Branch.objects.get(id = i)
                instbranch = instituteBranch(institutionId = instiid,branchCode = bran.BranchCode,branchId = bran,Status=bran.Status)
                instbranch.save()
            return redirect('institute_branch')
        else:
            return HttpResponse("You have No Permission")
        
        
    if request.user.is_superuser:
        id = request.session['defaultinstitute']
        id = int(id)
        if int(id) == 1:
            instibran = instituteBranch.objects.all()
        elif int(id) > 1: 
            userid = NewUser.objects.get(id = id)   
            instiid = Institution.objects.get( user = userid) 
            print(instiid)
            instibran = instituteBranch.objects.filter(institutionId = instiid.id) 
            print(instibran)
        paginator = Paginator(instibran,10)
        try:
            page = int(request.GET.get('page','1'))
        except:
            page = 1
        try:
            instibranch = paginator.page(page)
        except(EmptyPage,InvalidPage):
            instibranch = paginator.page(paginator.num_pages)   
        branch = Branch.objects.all()
        instibranid = []
        for i in instibran:
            insid = i.branchId.id
            instibranid.append(insid)
        print(instibranid)            
        context = {'branch':branch,'insti':instibranch,'instibranch':instibranid}
        return render(request,'institute-branch.html',context)
    elif request.user.is_institute:        
        userid =  request.user.id
        instiid = Institution.objects.get( user = userid) 
        instibranch = instituteBranch.objects.filter(institutionId = instiid.id) 
        branch = Branch.objects.all()
        context = {'branch':branch,'insti':instibranch}
        return render(request,'institute-branch.html',context)
    else:
        return HttpResponse("You have No Permission")

@csrf_exempt
def list_institute_branch(request):
    if request.method == 'POST':
        id  = request.POST['id']
        instance = instituteBranch.objects.get(id = id)
        # instiID = instance[0]['institutionId']
        Code = instance.branchCode
        Branch = instance.branchId_id
        print(instance.branchId_id)
        # Branch = "hello"
        Status = instance.Status
        ID = instance.id
        # print(Image)
        context = [ID,Code,Branch,Status]
        print(context)
        data = json.dumps(context)
        return HttpResponse(data)


@csrf_exempt
def list_institute_course(request):
    if request.method == "POST":
        id = request.POST['id']
        courses = institutionCourse.objects.get(id = id)
        code = courses.courseCode
        branch = courses.branchId_id
        course = courses.courseId_id
        fee = 1
        ID = courses.id
        status = courses.Status
        print(status)
        context = [code,branch,course,fee,ID,status]
        print(context)
        data = json.dumps(context)
        return HttpResponse(data)

@csrf_exempt
def update_institutebranch(request):
    if request.method == "POST":
        ID = request.POST['id'] 
        ID = int(ID)
        code = request.POST['branch_code']
        branch = request.POST['branch']
        branch = int(branch)
        print("-------------------------------------------")
        print(branch)
        print("-------------------------------------------")
        bran = Branch.objects.get(id = branch)
        print(bran)
        status = request.POST['status']
        branch = instituteBranch.objects.get(id = ID)
        branch.branchId = bran
        branch.branchCode = code
        branch.Status = status
        branch.save()
        messages.warning(request, "Institute branch updated successfully!")

    return redirect(institute_branch)

@csrf_exempt
def update_institute_course(request):
    if request.method == "POST":
        ID = request.POST['id']
        ID = int(ID)
        code = request.POST['course_code']
        branch = request.POST['branch']
        course = request.POST['course']
        fee = request.POST['fee']
        status = request.POST['status']
        insitute_course = institutionCourse.objects.get(id = ID)
        insitute_course.courseCode = code
        insitute_course.branchId = branch
        insitute_course.courseId = course
        insitute_course.courseFee = fee
        insitute_course.Status = status
        insitute_course.save()
        messages.warning(request, "Institute course updated successfully!")

    return redirect(institutecourse)

@login_required(login_url="login")
@csrf_exempt
def institutecourse(request):
    try:
        if request.method == 'POST':
            if request.user.is_superuser:
                id_b = request.POST['id']
                id_b = json.loads(id_b)
                print(type(id_b))
                print(id_b)
                id = request.session['defaultinstitute']
                if int(id) > 1:
                    instiid = Institution.objects.get(user = int(id))
                    instibran = institutionCourse.objects.filter(institutionId = instiid.id) 
                    instibranid = []
                    for i in instibran:
                        idb = i.courseId.id
                        instibranid.append(idb)
                print('------------------------')
                                    
                for i in id_b:
                    if i in instibranid:
                        pass
                    else:
                        course = Course.objects.get(id = i)
                        bran = Branch.objects.get(id = course.Branch.id)
                        instiid = Institution.objects.get( user = id)   
                        instbranch = institutionCourse.objects.create(institutionId = instiid ,courseCode = course.CourseCode,branchId = bran, courseId = course, Status = course.Status)
                        instbranch.save()
                print("saved")
            elif request.user.is_institute:
                code = request.POST['course_code']
                branch = request.POST['branch']
                course = request.POST['course']
                fee = request.POST['fee']
                status = request.POST['status']
                userid =  request.user.id
                instiid = Institution.objects.get( user = userid)      
                course = institutionCourse.objects.create(institutionId = instiid.id,courseCode = code,courseFee = fee, branchId = branch, courseId = course, Status = status)
                course.save()
                return redirect(institutecourse)
            else:
                return HttpResponse("You have No Permission")
    except Exception as e:
        print(str(e))
    if request.user.is_superuser:
        userid = request.session['defaultinstitute']
        userid = int(userid)
        if userid == 1:
            insticou = institutionCourse.objects.all().order_by('id')
            instibranch = instituteBranch.objects.all().order_by('id')
        else:
            instiid = Institution.objects.get( user = userid)  
            insticou = institutionCourse.objects.filter(institutionId = instiid.id)
            instibranch = instituteBranch.objects.filter(institutionId = instiid.id).values()
        paginator = Paginator(insticou,10)
        try:
            page = int(request.GET.get('page','1'))
        except:
            page = 1
        try:
            insticourse = paginator.page(page)
        except(EmptyPage,InvalidPage):
            insticourse = paginator.page(paginator.num_pages)   
        course = Course.objects.all()
        c  = []
        if userid > 1:
            instict = instiid.courseType
            print(len(instict))
            for data in instibranch:
                if len(instict) <= 1:
                    courses = Course.objects.filter(Branch = data['branchId_id']) & Course.objects.filter(CourseType = instict)
                    for i in courses:                
                        courseid  = i.id
                        CourseName = i.CourseName
                        co = {"id" : courseid,"name" : CourseName}
                        c.append(co)
                else:
                    for i in range (0,len(instict)):
                        courses = Course.objects.filter(Branch = data['branchId_id']) & Course.objects.filter(CourseType = int(instict[i]))
                        for i in courses:                
                            courseid  = i.id
                            CourseName = i.CourseName
                            co = {"id" : courseid,"name" : CourseName}
                            c.append(co)   
        branch = Branch.objects.all()    
        sup = SupportingDoc.objects.all()
        return render(request,'institute-course.html',{'insticoures':insticourse,'branch':branch,'instibranch':instibranch,'c':c,'sup':sup})
    elif request.user.is_institute :        
        userid =  request.user.id
        instiid = Institution.objects.get( user = userid) 
        insticou = institutionCourse.objects.filter(institutionId = instiid.id)
        instibran = instituteBranch.objects.all().order_by('id')
        paginator = Paginator(insticou,10)
        try:
            page = int(request.GET.get('page','1'))
        except:
            page = 1
        try:
            insticourse = paginator.page(page)
        except(EmptyPage,InvalidPage):
            insticourse = paginator.page(paginator.num_pages)   
        instibranch = instituteBranch.objects.filter(institutionId = instiid.id).values()
        branch = Branch.objects.all()
        print(instibranch)
        course = Course.objects.all()        
        sup = SupportingDoc.objects.all()
        return render(request,'institute-course.html',{'insticoures':insticourse,'branch':branch,'instibranch':instibranch,'course':course,'sup':sup})
    else:
        return HttpResponse("You dont have enough permission")

@csrf_exempt
def list_institute_branch_courses(request):
    if request.method == "POST":
        # branchId = request.POST['branchId']
        # print(branchId)
        # b = instituteBranch.objects.get(id = branchId)
        # print(b)
        # bran = b[0]['branchId']
        print('-------------------------------------------------------------------------')
        # c = Course.objects.filter(id=id).values()
        # course= []
        # for data in c:
        #     courseid  = data[0]['id']
        #     CourseName = data[0]['CourseName']
        #     c = {"id" : courseid,"name" : CourseName}
        #     course.append(c)

        # data = json.dumps(course)
        # return HttpResponse("hello")

        branch = request.POST['branchId']
        branch = int(branch) 
        print(branch)
        client = pymongo.MongoClient("mongodb://localhost:27017/")
        # Database Name
        db = client["eduvytest"]
        
        # Collection Name
        con = db["Courses"]
        myquery = { "Branch_id": branch }
        x = con.find(myquery)
        print(x)
        course= []
        for data in x:
            courseid  = data['id']
            print("hello")
            courseName = data['CourseName']
            c = {"id" : courseid,"course" : courseName}
            course.append(c)
        print(course)
        data = json.dumps(course)
        
        return HttpResponse(data)


@login_required(login_url="login")
@csrf_exempt
def students(request):
    
    request.session['title'] = "Students"
    try:
        if request.method == "POST":
            if request.user.is_superuser:
                batch = request.POST['batch']
                batch_section = request.POST['batch_section']
                course_id = request.POST['course_id'] 
                name = request.POST['name']
                email = request.POST['email']
                phone = request.POST['phone']
                address = request.POST['address']
                guardian_name = request.POST['guardian_name']
                guardian_phone = request.POST['guardian_phone']
                guardian_phone = request.POST['guardian_phone']
                course_id = int(course_id)
                userid = NewUser.objects.get(id = request.session['defaultinstitute'])
                institution = Institution.objects.get(user = userid)
                course = Course.objects.get(id = course_id)
                print("-----------------------")
                insticourse  = institutionCourse.objects.get(courseId = course,institutionId = institution)
                admission =  insticourse.admissionid + 1
                insticourse.admissionid = admission
                insticourse.save()
                branch = Branch.objects.get(id = insticourse.branchId.id)
                # branch = Branch.objects.get(id = branch_id)
                print(branch)
                branch_code = branch.BranchCode
                print(branch_code)
                userid =  request.session['defaultinstitute']
                userid = int(userid)
                instiid = Institution.objects.get( user = userid)
                print(instiid)
                institutioncode = instiid.institutionCode
                studentid = str(institutioncode) + str(batch) + str(branch_code) + str(course.CourseCode) + str(admission)
                print(studentid)
                randompass = NewUser.objects.make_random_password()
                print(123)
                userreg = NewUser(email = email,is_student = True,is_active =True) 
                userreg.set_password(123)  #change this at the time of deployment   
                userreg.save()
                subject = 'welcome to Eduvy'
                message = f'Hi, thank you for registering in Eduvy.Your Password is {randompass}'
                email_from = settings.EMAIL_HOST_USER
                recipient_list = [email, ]
                send_mail( subject, message, email_from, recipient_list )
                student = Students(user = userreg,batch = batch,batchSection=batch_section,studentID=studentid,institutionId=instiid,name=name,email=email,branchId= branch.id,courseId = course_id,phone = phone,address =address,guardianName = guardian_name,guardianPhone = guardian_phone)
                print(student)
                student.save()
                return redirect(students)
            elif request.user.is_institute:
                batch = request.POST['batch']
                batch_section = request.POST['batch_section']
                course_id = request.POST['course_id'] 
                name = request.POST['name']
                email = request.POST['email']
                phone = request.POST['phone']
                address = request.POST['address']
                guardian_name = request.POST['guardian_name']
                guardian_phone = request.POST['guardian_phone']
                guardian_phone = request.POST['guardian_phone']
                print(course_id)
                course_id = int(course_id)
                # print(course)
                client = pymongo.MongoClient("mongodb://localhost:27017/")
                # Database Name
                db = client["eduvy"]
                
                # Collection Name
                con = db["Institution Course"]
                myquery = { "courseId": course_id }
                x = con.find(myquery)
                for data in x:
                    print("helo")
                    coursecode  = data['courseCode']
                    branch_id = data['branchId']
                    admission = data['admissionid']
                print(coursecode)
                admission = admission + 1
                print(admission)
                newvalues = { "$set": { "admissionid": admission } }

                con.update_one(myquery, newvalues)
                branch = Branch.objects.get(id = branch_id)
                print(branch)
                branch_code = branch.BranchCode
                institutionId = branch.user
                userid =  request.user.id
                instiid = Institution.objects.get( user = userid)
                print(instiid)
                institutioncode = instiid.institutionCode
                studentid = str(institutioncode) + str(batch) + str(branch_code) + str(coursecode) + str(admission)
                print(studentid)
                randompass = NewUser.objects.make_random_password()
                print(123)
                userreg = NewUser(email = email,is_student = True,is_active =True) 
                userreg.set_password(123)  #change this at the time of deployment   
                userreg.save()
                subject = 'welcome to Eduvy'
                message = f'Hi, thank you for registering in Eduvy.Your Password is {randompass}'
                email_from = settings.EMAIL_HOST_USER
                recipient_list = [email, ]
                # send_mail( subject, message, email_from, recipient_list )
                student = Students(batch = batch,batchSection=batch_section,studentID=studentid,institutionId=instiid,name=name,email=email,branchId= branch_id,courseId = course_id,phone = phone,address =address,guardianName = guardian_name,guardianPhone = guardian_phone)
                print(student)
                student.save()
                return redirect(students)
            else:
                return HttpResponse("No Permission")
    except Exception as e:
        print(str(e))
    if request.user.is_superuser:
        userid =  request.session['defaultinstitute']
        userid = int(userid)
        if userid == 1:
            course = Course.objects.all()
            stud = Students.objects.all()
            insticourse = []
            # print(insticourse + "superuser")
        else:
            try:
                instiid = Institution.objects.get(user = userid)
                insticourse = institutionCourse.objects.filter(institutionId = instiid)
                course = Course.objects.all()
                stud = Students.objects.filter(institutionId = instiid)
            except Exception as e:
                print(str(e))
                stud= "No Data"
                instiid = Institution.objects.filter(user = userid)
                insticourse = institutionCourse.objects.filter(institutionId = instiid)
                course = Course.objects.all().order_by('id')
        if stud != "No Data":
            paginator = Paginator(stud,1)
            try:
                page = int(request.GET.get('page','1'))
            except:
                page = 1
            try:
                student = paginator.page(page)
            except(EmptyPage,InvalidPage):
                student = paginator.page(paginator.num_pages)
        else:
            student = stud
        print(insticourse)
        context = {'course':course,'student':student,"insticourse": insticourse}
        return render(request,'students.html',context)
    elif request.user.is_institute:
        institution = Institution.objects.get(user = request.user.id)
        insticourse = institutionCourse.objects.filter(institutionId = institution.id)
        client = pymongo.MongoClient("mongodb://localhost:27017/")
        # Database Name
        db = client["eduvy"]
        
        # Collection Name
        con = db["Institution Course"]
        myquery = { "institutionId": 1 }
        x = con.find(myquery)
        courses= []
        for data in x:
            id  = data['id']
            c = {"id" : id}
            courses.append(c)
        course = Course.objects.all().order_by('id')
        userid =  request.user.id
        instiid = Institution.objects.get( user = userid)
        stud = Students.objects.filter(institutionId = instiid.id)
        paginator = Paginator(stud,1)
        try:
            page = int(request.GET.get('page','1'))
        except:
            page = 1
        try:
            student = paginator.page(page)
        except(EmptyPage,InvalidPage):
            student = paginator.page(paginator.num_pages)
        context = {'course':course,'student':student,'courses':courses}
        return render(request,'students.html',context)

@csrf_exempt
def list_course_duration(request):
    if request.method == "POST":
        cid = request.POST['course']
        course = Course.objects.filter(id = cid).values()
        courseduration = course[0]['CourseDuration']
        data = json.dumps(courseduration)
        
        return HttpResponse(data)


@csrf_exempt
def list_student(request):
    if request.method == "POST":
        id = request.POST['id']
        student = Students.objects.get(id = id)
        batch = student.batch
        batchSection = student.batchSection
        name = student.name
        email = student.email
        guardianName = student.guardianName
        guardianPhone = student.guardianPhone
        address = student.address
        phone = student.phone
        courseId = student.courseId
        studentID = student.id
        context = [batch,batchSection,name,email,guardianName,str(phone),str(guardianPhone),address,courseId,studentID]
        print(context)
        data = json.dumps(context)
        return HttpResponse(data)

        

@csrf_exempt
def delete_student(request):
    if request.method == "POST":
        id = request.POST["id"]
        instance = Students.objects.filter(id=id)
        instance.delete()
        messages.warning(request, 'Student deleted successfully!')
        # return redirect(branch)
        data = {
        'is_taken': "deleted"
        }
        return JsonResponse(data)
    return redirect(students)

import datetime
from json import JSONEncoder

class DateTimeEncoder(JSONEncoder):
        #Override the default method
        def default(self, obj):
            if isinstance(obj, (datetime.date, datetime.datetime)):
                return obj.isoformat()


# search views starts from here

#branch search
@csrf_exempt
def search_branch(request):
    if request.method == "POST":
        searched = request.POST['search']
        bran = Branch.objects.filter(BranchCode__icontains = searched).values()|Branch.objects.filter(BranchName__icontains = searched).values()
        print(bran)
        length = len(list(bran))
        # print(length)
        branch = []
        for i in range(0,length):
            b = list(bran)[i]
            branch.append(b)
        data = json.dumps(branch,indent=4, cls=DateTimeEncoder)
        return HttpResponse(data)

    # return render(request,'demo.html')
    
    
#course search
@csrf_exempt
def search_course(request):
    if request.method == "POST":
        searched = request.POST['search']
        course = Course.objects.filter(CourseName__icontains=searched).values()
        length = len(list(course))
        courses = []
        for i in range(0,length):
            b = list(course)[i]
            courses.append(b)
        data = json.dumps(courses,indent=4, cls=DateTimeEncoder)
        return HttpResponse(data)

@csrf_exempt
def search_institute_branch(request):
    if request.method == "POST":
        searched = request.POST['search']
        insti_bran = instituteBranch.objects.filter(branchId__icontains=searched).values() | instituteBranch.objects.filter(branchCode__icontains=searched).values() | instituteBranch.objects.filter(Status__icontains=searched).values()
        length = len(list(insti_bran))
        # print(length)
        branches = []
        for i in range(0,length):
            b = list(insti_bran)[i]
            branches.append(b)
        data = json.dumps(branches,indent=4, cls=DateTimeEncoder)
        return HttpResponse(data)

@csrf_exempt
def search_document(request):
    if request.method == "POST":
        searched = request.POST['search']
        document = SupportingDoc.objects.filter(DocumentName__icontains=searched).values() | SupportingDoc.objects.filter(Status__icontains=searched).values()
        length = len(list(document))
        documents = []
        for i in range(0, length):
            d = list(document)[i]
            documents.append(d)
        data = json.dumps(documents,indent=4, cls=DateTimeEncoder)
        return HttpResponse(data)

@csrf_exempt
def search_institute(request):
    if request.method == "POST":
        searched = request.POST['search']
        insti = Institution.objects.filter(name__icontains=searched).values() | Institution.objects.filter(institutionCode__icontains=searched).values() | Institution.objects.filter(chairmanName__icontains=searched).values() | Institution.objects.filter(contactPersonEmail__icontains=searched).values() | Institution.objects.filter(contactPersonPhone__icontains=searched).values() | Institution.objects.filter(contactPersonName__icontains=searched).values()
        length = len(list(insti))
        # print(length)
        institutes = []
        for i in range(0,length):
            b = list(insti)[i]
            institutes.append(b)
        data = json.dumps(institutes,indent=4, cls=DateTimeEncoder)
        return HttpResponse(data)


def demo(request):
    return render(request,'demo.html')


@csrf_exempt
def institution_student(request):
    return render(request,'institute_student.html')


@csrf_exempt
def admission(request):
    return render(request,'admission.html')


@csrf_exempt
def institute_requests(request):
    return render(request,'institution-request.html')

@csrf_exempt
def user_group(request):
    
    request.session['title'] = "User Groups"
    try:
        if request.method == "POST":
            name = request.POST['name']
            new_group, created = Group.objects.get_or_create(name = name)
            perms = request.POST.getlist("permissions[]")
            print(perms)
            for i in perms:
                i = int(i)
                if i:
                    permissions_list = Permission.objects.filter(id = i).first()
                    print(permissions_list)
                    new_group.permissions.add(permissions_list)
                    print(new_group)
                    print(type(i))
                    print(i)
            return redirect('user_group')
    except Exception as e:
        print(str(e))
    user_group = Group.objects.all()
    permission = Permission.objects.all()
    context = {'permission': permission,'user_group' : user_group }
    return render(request,'user-groups.html',context)


def new_payment(request):
    return render(request,'payment.html')
def payment_history(request):
    return render(request,'payment-history.html')
def notification(request):
    return render(request,'notification.html')
def notification_history(request):
    return render(request,'notification-history.html')


def institutebranch_modeltocsv(request):
    instibranches = instituteBranch.objects.all() #model to which we are doing the csv conversion
    response = HttpResponse('text/csv')
    response['Content-Disposition'] = 'attachment; filename = Institute-Branches.csv'
    writer = csv.writer(response)
    writer.writerow(['ID','Branch code', 'Branch ID', 'status', 'DateCreated' ])
    insti = instibranches.values_list('id','institutionId', 'branchCode', 'branchId', 'Status', 'dateCreated')#model fields containing the values
    for ins in insti:
        writer.writerow(ins)
    return response

def institutecourses_modeltocsv(request):
    insticourses = institutionCourse.objects.all()
    response = HttpResponse('text/csv')
    response['Content-Disposition'] = 'attachment; filename = Institute-Courses.csv'
    writer = csv.writer(response)
    writer.writerow(['ID', 'institutionId', 'Course Code', 'Course Fee', 'Branch Id', 'Course Id', 'Status', 'Admission id', 'Date Created'])
    insti = insticourses.values_list('id', 'institutionId', 'courseCode', 'courseFee', 'branchId', 'courseId', 'Status', 'admissionid', 'dateCreated')
    for ins in insti:
        writer.writerow(ins)
    return response

def staffs_modeltocsv(request):
    staff = Staff.objects.all()
    response = HttpResponse('text/csv')
    response['Content-Disposition'] = 'attachment; filename = Staff.csv'
    writer = csv.writer(response)
    writer.writerow(['id' ,'institution ID', 'image', 'name', 'Father Name', 'Nationality', 'email', 'phone', 'DOB', 'Gender', 'Marital Status', 'Annual Salary', 'Designation', 'Branch Id', 'Aadhaar Num', 'PAN Number', 'DateofJoin', 'Status', 'date'])
    stf = staff.values_list('id' ,'institutionID', 'image', 'name', 'fatehrName', 'nationality', 'email', 'phone', 'DOB', 'gender', 'maritalStatus', 'annualSalary', 'designation', 'branchId', 'aadhaarNumber', 'panNumber', 'DateofJoin', 'Status', 'date')
    for s in stf:
        writer.writerow(s)
    return response


def students_modeltocsv(request):
    student = Students.objects.all()
    response = HttpResponse('text/csv')
    response['Content-Disposition'] = 'attachment; filename = Students.csv'
    writer = csv.writer(response)
    writer.writerow(['ID','batch', 'batchSection', 'studentID', 'institutionId', 'name', 'email', 'branchId', 'courseId', 'phone', 'documents', 'address', 'guardianName', 'guardianPhone', 'DateOfJoin'])
    std = student.values_list('id','batch', 'batchSection', 'studentID', 'institutionId', 'name', 'email', 'branchId', 'courseId', 'phone', 'documents', 'address', 'guardianName', 'guardianPhone', 'DateOfJoin')
    for s in std:
        writer.writerow(s)
    return response

@csrf_exempt
def update_students(request):
    if request.method =="POST":
        batch = request.POST['batch']
        id = request.POST['id']
        course_id = request.POST['course_id']
        batch_section = request.POST['batch_section']
        name = request.POST['name']
        email = request.POST['email']
        phone = request.POST['phone']
        address = request.POST['address']
        guardian_name = request.POST['guardian_name']
        guardian_phone = request.POST['guardian_phone']
        stud = Students.objects.get(id = id)
        stud.batch = batch
        stud.courseId = course_id
        stud.batchSection = batch_section
        stud.name = name
        stud.email = email
        stud.phone = phone
        stud.address = address
        stud.guardianName = guardian_name
        stud.guardianPhone = guardian_phone
        stud.save()
        messages.warning(request, 'Students updated successfully!')
        
    return redirect('students')

@csrf_exempt
def search_introbanner(request):
    if request.method == "POST":
        searched = request.POST['search']
        introban = introBanner.objects.filter(Title__icontains=searched).values() | introBanner.objects.filter(Description__icontains=searched).values() | introBanner.objects.filter(Status__icontains=searched).values() | introBanner.objects.filter(date__icontains=searched).values()
        length = len(list(introban))
        # print(length)
        introbaner = []
        for i in range(0,length):
            b = list(introban)[i]
            introbaner.append(b)
        data = json.dumps(introbaner,indent=4, cls=DateTimeEncoder)
        return HttpResponse(data)

@csrf_exempt
def search_planbanner(request):
    if request.method == "POST":
        searched = request.POST['search']
        planban = planBanner.objects.filter(Title__icontains=searched).values() | planBanner.objects.filter(Description__icontains=searched).values() | planBanner.objects.filter(Status__icontains=searched).values() | planBanner.objects.filter(date__icontains=searched).values()
        length = len(list(planban))
        # print(length)
        planbaner = []
        for i in range(0,length):
            b = list(planban)[i]
            planbaner.append(b)
        data = json.dumps(planbaner,indent=4, cls=DateTimeEncoder)
        return HttpResponse(data)

@csrf_exempt
def search_instibanner(request):
    if request.method == "POST":
        searched = request.POST['search']
        instiban = instituteBanner.objects.filter(Title__icontains=searched).values() | instituteBanner.objects.filter(Status__icontains=searched).values() 
        length = len(list(instiban))
        # print(length)
        instibaner = []
        for i in range(0,length):
            b = list(instiban)[i]
            instibaner.append(b)
        data = json.dumps(instibaner,indent=4, cls=DateTimeEncoder)
        return HttpResponse(data)


@csrf_exempt
def newinstitutebranch(request):
    if request.method == "POST":
        BranchCode = request.POST["branch_code"]
        Branchname = request.POST["branch_name"]
        Image = request.FILES["branch_image"]
        Status = request.POST["status"]
        users = NewUser.objects.get(id = request.user.id)
        BranchSave = Branch(user = users, BranchCode=BranchCode, BranchName=Branchname, Image=Image, Status=Status)
        BranchSave.save()
        instiid = Institution.objects.get(user = int(request.session['defaultinstitute']))
        instibranch = instituteBranch(institutionId = instiid, branchCode = BranchCode, branchId = BranchSave, Status = Status)
        instibranch.save()
        return redirect('institute_branch')
    else:
        return HttpResponse("You have No Permission")
        
@csrf_exempt  
@login_required(login_url="login")    
def institutecourse_fee(request):
    if request.method == "POST":
        if request.user.is_superuser:
            fee = feeStructure()
            x = request.POST['course']
            course = institutionCourse.objects.get(id = x)
            
            for key, value in request.POST.items():
                try:
                    if key == 'course':
                        fee.institutionCourse = course  
                        fee.save()             
                    elif key == 'addmission_fee':
                        x = int(value)
                        fee.Admissionfee = x
                        print(x)
                        fee.save()                
                    elif key =='tution_fee':
                        x = int(value)
                        fee.Tutionfee = x
                        print(x)
                        fee.save()
                    elif key == 'exam_fee':
                        x = int(value)
                        fee.Examfee = x
                        print(x)
                        fee.save()
                    elif key == 'mark_card_fee':
                        x = int(value)
                        fee.MarksCardfee = x
                        print(x)
                        fee.save()
                    elif key == 'caution_deposit':
                        x = int(value)
                        fee.CautionDeposit = x
                        print(x)
                        fee.save()
                    elif key== 'library_fee':
                        x = int(value)
                        fee.Libraryfee = x
                        print(x)
                        fee.save()
                    elif key == 'sports_fee':
                        x = int(value)
                        fee.Sportsfee = x
                        print(x)
                        fee.save()
                    elif key == 'registration_fee':
                        x = int(value)
                        fee.Registrationfee = x
                        print(x)
                        fee.save()
                    else:
                        y= key
                        y = y.replace("_"," ")
                        y = y.capitalize()
                        z= int(value)
                        print(y,z)
                        oth_fee = otherFeeStructure(parent = course, name = y , value = z)
                        oth_fee.save()
                except:
                    pass
                fee.save()
                
            return redirect('institutecourse_fee')


    if request.user.is_superuser:
        userid = int(request.session['defaultinstitute'])
        if userid > 1:
            feestruct = feeStructure.objects.all()
            instiid = Institution.objects.get(user = userid)
            insticourse = institutionCourse.objects.filter(institutionId = instiid)
            return render(request,'institutioncourse_fee.html',{'feestruct':feestruct,'insticourse':insticourse})
        else:
            
            messages.warning(request, "Change Insitution")
            return redirect('dashboard')
    
    
    
@csrf_exempt
def newinstitutecourse(request):
    try:
        if request.method =="POST":  
            BranchID = request.POST['branch_id']
            CourseCode = request.POST["course_code"]
            Coursename = request.POST["course_name"]
            Duration = request.POST['duration']
            Descrip = request.POST['description']
            Image = request.FILES["course_image"]
            Status = request.POST["status"]
            print("hello")
            Doc = request.POST.getlist("documents[]")
            print(Doc)
            branch = Branch.objects.get(id = BranchID)
            document = ""
            for i in Doc:
                document = document + i
                print(document)            
                document = document + ","

            CourseSave = Course(user = request.user.id,
                Branch=branch, CourseCode=CourseCode, CourseName=Coursename, CourseDuration=Duration, CourseDescription = Descrip, SupDoc = document, CourseImage = Image, Status = Status
            )
            CourseSave.save()
            userid = int(request.session['defaultinstitute'])
            instiid = Institution.objects.get(user = userid)
            course = institutionCourse.objects.create(institutionId = instiid ,courseCode = CourseCode, branchId = branch, courseId = CourseSave, Status = Status)
            course.save()
            return redirect(institutecourse)
    except Exception as e:
        print(e)        
        return redirect(institutecourse)
    
    
@csrf_exempt
def is_branch_code(request):
    if request.method =="POST":
        code = request.POST['code']
        try:
            brancode = Branch.objects.filter(BranchCode__iexact = code).count()
        except:
            brancode = 0
        print(brancode)
        data = json.dumps(brancode)
        if(brancode > 0):
            return HttpResponse(data)
        else:
            return HttpResponse(data)

@csrf_exempt
def is_insti_branch_code(request):
    if request.method =="POST":
        code = request.POST['code']
        try:
            brancode = instituteBranch.objects.filter(branchCode__iexact = code).count()
        except:
            brancode = 0
        print(brancode)
        data = json.dumps(brancode)
        if(brancode > 0):
            return HttpResponse(data)
        else:
            return HttpResponse(data)




@csrf_exempt
def is_branch_name(request):
    if request.method =="POST":
        name = request.POST['name']
        try:
            branname = Branch.objects.filter(BranchName__iexact = name).count()
        except:
            branname = 0
        print(branname)
        data = json.dumps(branname)
        if(branname > 0):
            return HttpResponse(data)
        else:
            return HttpResponse(data)

@csrf_exempt
def is_course_name(request):
    if request.method =="POST":
        corname = request.POST['corname']
        try:
            coursename = Course.objects.filter(CourseName__iexact = corname).count()
        except:
            coursename = 0
        print(coursename)
        data = json.dumps(coursename)
        if(coursename > 0):
            return HttpResponse(data)
        else:
            return HttpResponse(data)

@csrf_exempt
def is_course_code(request):
    if request.method =="POST":
        corcode = request.POST['corcode']
        try:
            coursecode = Course.objects.filter(CourseCode__iexact = corcode).count()
        except:
            coursecode = 0
        print(coursecode)
        data = json.dumps(coursecode)
        if(coursecode > 0):
            return HttpResponse(data)
        else:
            return HttpResponse(data)

@csrf_exempt
def is_doc_name(request):
    if request.method =="POST":
        docname = request.POST['docname']
        try:
            documentname = SupportingDoc.objects.filter(DocumentName__iexact = docname).count()
        except:
            documentname = 0
        print(documentname)
        data = json.dumps(documentname)
        if(documentname > 0):
            return HttpResponse(data)
        else:
            return HttpResponse(data)
@csrf_exempt
def is_email(request):
    if request.method =="POST":
        instemail = request.POST['instemail']
        try:
            email = NewUser.objects.filter(email__iexact = instemail).count()
        except:
            email = 0
        data = json.dumps(email)
        if(email > 0):
            return HttpResponse(data)
        else:
            return HttpResponse(data)

@csrf_exempt
def is_staff_email(request):
    if request.method =="POST":
        staffemail = request.POST['staffemail']
        try:
            email = Staff.objects.filter(email__iexact = staffemail).count()
        except:
            email = 0
        data = json.dumps(email)
        if(email > 0):
            return HttpResponse(data)
        else:
            return HttpResponse(data)

@csrf_exempt
def is_student_email(request):
    if request.method =="POST":
        studentemail = request.POST['studentemail']
        try:
            email = Students.objects.filter(email__iexact = studentemail).count()
        except:
            email = 0
        data = json.dumps(email)
        if(email > 0):
            return HttpResponse(data)
        else:
            return HttpResponse(data)

@csrf_exempt
def is_insti_code(request):
    if request.method =="POST":
        instcode = request.POST['instcode']
        try:
            institutecode = Institution.objects.filter(institutionCode__iexact = instcode).count()
        except:
            institutecode = 0
        print(institutecode)
        data = json.dumps(institutecode)
        if(institutecode > 0):
            return HttpResponse(data)
        else:
            return HttpResponse(data)

@csrf_exempt
def is_insti_name(request):
    if request.method =="POST":
        instname = request.POST['instname']
        try:
            institutename = Institution.objects.filter(name__iexact = instname).count()
        except:
            institutename = 0
        print(institutename)
        data = json.dumps(institutename)
        if(institutename > 0):
            return HttpResponse(data)
        else:
            return HttpResponse(data)

@csrf_exempt
def is_intro_banner(request):
    if request.method =="POST":
        intro = request.POST['intro']
        try:
            introtitle = introBanner.objects.filter(Title__iexact = intro).count()
        except:
            introtitle = 0
        print(introtitle)
        data = json.dumps(introtitle)
        if(introtitle > 0):
            return HttpResponse(data)
        else:
            return HttpResponse(data)

@csrf_exempt
def is_plan_banner(request):
    if request.method =="POST":
        plan = request.POST['plan']
        try:
            plantitle = planBanner.objects.filter(Title__iexact = plan).count()
        except:
            plantitle = 0
        print(plantitle)
        data = json.dumps(plantitle)
        if(plantitle > 0):
            return HttpResponse(data)
        else:
            return HttpResponse(data)

@csrf_exempt
def is_inst_banner(request):
    if request.method =="POST":
        inst = request.POST['inst']
        try:
            insttitle = instituteBanner.objects.filter(Title__iexact = inst).count()
        except:
            insttitle = 0
        print(insttitle)
        data = json.dumps(insttitle)
        if(insttitle > 0):
            return HttpResponse(data)
        else:
            return HttpResponse(data)


@csrf_exempt 
def list_college(request):
    if request.method == "POST":
        id = request.POST['id']
        instance = College.objects.filter(id=id).values()
        print(instance)
        Name = instance[0]['name']
        State = instance[0]['stateID']
        City = instance[0]['cityId']
        Address = instance[0]['address']
        Chairman = instance[0]['chairmanName']
        Chairperson = instance[0]['contactPersonName']
        email = instance[0]['contactPersonEmail']
        phone = instance[0]['contactPersonPhone']
        image = instance[0]['image']
        Status = instance[0]['Status']
        ID = instance[0]['id']
        institutionCode = instance[0]['code']
        context = [ID,Name,State,City,Address,Chairman,Chairperson,email,phone,image,Status,institutionCode]
        data = json.dumps(context)
        print(data)
        return HttpResponse(data)
    
@csrf_exempt
def update_college(request):
    if request.method == "POST":
        ID = request.POST['_id']
        branch = College.objects.get(id = ID)
        name = request.POST['institution_name']
        code = request.POST['institution_code']
        state = request.POST['state']
        city = request.POST['city']
        address = request.POST['address']
        chairman_name = request.POST['chairman_name']
        contact_person_name = request.POST['contact_person_name']
        contact_person_email = request.POST['contact_person_email']
        contact_person_phone = request.POST['contact_person_phone']
        if len(request.FILES) != 0:
            if len(branch.image) > 0:
                os.remove(branch.image.path)
            branch.image = request.FILES['institution_image']
        status = request.POST['status']
        branch.code  = code
        branch.contactPersonEmail  = contact_person_email
        branch.name = name
        branch.stateID = state
        branch.cityId = city
        branch.address = address
        branch.chairmanName = chairman_name
        branch.contactPersonName = contact_person_name
        branch.contactPersonPhone = contact_person_phone
        branch.Status = status
        branch.save()
        college_change(request)
        messages.warning(request, "College updated successfully!")
    return redirect('college')



@login_required(login_url="login")
@csrf_exempt
def college_branch(request):
    if request.method == 'POST':
        if request.user.is_superuser:                
            id_b = request.POST['id']
            id_b = json.loads(id_b)
            print(type(id_b))
            print(id_b)
            print(request.session['defaultcollege'])
            id = request.session['defaultcollege']
            if int(id) > 0:
                user = NewUser.objects.get(id =int(id))
                instiid = College.objects.get(user = user)
                instibran = collegeBranch.objects.filter(college = instiid) 
                print(instibran)
                instibranid = []
                if instibran:
                    for i in instibran:
                        idb = i.branchId.id
                        instibranid.append(idb)
                                
            for i in id_b:
                if i in instibranid:
                    pass
                else:
                    bran = Branch.objects.get(id = i)
                    user = NewUser.objects.get(id =int(id))
                    instiid = College.objects.get( user = user)   
                    instbranch = collegeBranch(college = instiid,branchCode = bran.BranchCode,branchId = bran,Status=bran.Status)
                    instbranch.save()
            print("saved")
            return HttpResponse('Success')
        
        elif request.user.is_college:      
            id_b = request.POST['id']
            id_b = json.loads(id_b)
            print(type(id_b))
            print(id_b)
            id = request.user.id
            instiid = College.objects.get( user = id)   
            for i in id_b:
                bran = Branch.objects.get(id = i)
                instbranch = collegeBranch(institutionId = instiid,branchCode = bran.BranchCode,branchId = bran,Status=bran.Status)
                instbranch.save()
            return redirect('college_branch')
        else:
            return HttpResponse("You have No Permission")
        
        
    if request.user.is_superuser:
        id = request.session['defaultinstitute']
        id = int(id)
        if int(id) == 1:
            instibran = collegeBranch.objects.all()
        elif int(id) > 1: 
            userid = NewUser.objects.get(id = id)   
            instiid = Institution.objects.get( user = userid) 
            print(instiid)
            instibran = collegeBranch.objects.filter(college = instiid.id) 
            
        paginator = Paginator(instibran,10)
        try:
            page = int(request.GET.get('page','1'))
        except:
            page = 1
        try:
            instibranch = paginator.page(page)
        except(EmptyPage,InvalidPage):
            instibranch = paginator.page(paginator.num_pages)   
        branch = Branch.objects.all()
        instibranid = []
        for i in instibran:
            insid = i.branchId.id
            instibranid.append(insid)
        print(instibranid)            
        college_change(request)
        context = {'branch':branch,'insti':instibranch,'instibranch':instibranid}
        return render(request,'college-branch.html',context)
    elif request.user.is_institute:        
        userid =  request.user.id
        instiid = Institution.objects.get( user = userid) 
        instibranch = collegeBranch.objects.filter(college = instiid.id) 
        branch = Branch.objects.all()
        college_change(request)
        context = {'branch':branch,'insti':instibranch}
        return render(request,'college-branch.html',context)
    else:
        return HttpResponse("You have No Permission")

@csrf_exempt
def college_change(request):
    users  = College.objects.all()
    user = [[0,'All College']]
    try:
        for i in users:
            z = []
            z.append(i.user.id)
            z.append(i.name)
            user.append(z)
        print(z)
    except Exception as e:
        print(str(e))
    request.session['college'] = user
    return request.session['college']


@csrf_exempt
def change_college(request):
    if request.method == "POST":
        college = request.POST['institution'] 
        print(college) 
        del request.session['defaultcollege']  
        request.session['defaultcollege']  = 1 
        request.session['defaultcollege'] = college 
        print(request.session['defaultcollege']  )
        print('------------------------------------')
        print(request.session['defaultcollege'])
        return HttpResponse("sucess")
        

@csrf_exempt
def delete_collegebranch(request):
    if request.method == "POST":
        id = request.POST["id"]
        instance = collegeBranch.objects.get(id=id)
        instance.delete()
        messages.warning(request, "College branch deleted successfully!")
        # return redirect(branch)
        data = {
        'is_taken': "deleted"
        }
        
        return JsonResponse(data)
    return redirect(instituteBranch)


@csrf_exempt
def list_college_branch(request):
    if request.method == 'POST':
        id  = request.POST['id']
        instance = collegeBranch.objects.get(id = id)
        Code = instance.branchCode
        Branch = instance.branchId_id
        print(instance.branchId_id)
        # Branch = "hello"
        Status = instance.Status
        ID = instance.id
        # print(Image)
        context = [ID,Code,Branch,Status]
        print(context)
        data = json.dumps(context)
        return HttpResponse(data)


@csrf_exempt
def newcollegebranch(request):
    if request.method == "POST":
        BranchCode = request.POST["branch_code"]
        Branchname = request.POST["branch_name"]
        Image = request.FILES["branch_image"]
        Status = request.POST["status"]
        users = NewUser.objects.get(id = request.user.id)
        BranchSave = Branch(BranchCode=BranchCode, BranchName=Branchname, Status=Status)
        BranchSave.save()   
        BranchSave.Image = Image
        print(Image)
        BranchSave.save()   
        instiid = Institution.objects.get(user = int(request.session['defaultcollege']))
        instibranch = collegeBranch(college = instiid, branchCode = BranchCode, branchId = BranchSave, Status = Status)
        instibranch.save()
        return redirect('institute_branch')
    else:
        return HttpResponse("You have No Permission")



@csrf_exempt
def update_collegebranch(request):
    if request.method == "POST":
        ID = request.POST['id'] 
        ID = int(ID)
        code = request.POST['branch_code']
        branch = request.POST['branch']
        branch = int(branch)
        print("-------------------------------------------")
        print(branch)
        print("-------------------------------------------")
        bran = Branch.objects.get(id = branch)
        print(bran)
        status = request.POST['status']
        branch = collegeBranch.objects.get(id = ID)
        branch.branchId = bran
        branch.branchCode = code
        branch.Status = status
        branch.save()
        messages.warning(request, "Institute branch updated successfully!")

    return redirect(college_branch)



@login_required(login_url="login")
@csrf_exempt
def college_course(request):
    try:
        if request.method == 'POST':
            print("post_college_course")
            if request.user.is_superuser:
                id_b = request.POST['id']
                id_b = json.loads(id_b)
                print(type(id_b))
                print(id_b)
                id = request.session['defaultcollege']
                if int(id) > 0:
                    instiid = College.objects.get(user = int(id))
                    instibran = collegeCourse.objects.filter(college = instiid.id) 
                    instibranid = []
                    for i in instibran:
                        idb = i.courseId.id
                        instibranid.append(idb)
                print('------------------------')
                                    
                for i in id_b:
                    if i in instibranid:
                        pass
                    else:
                        course = Course.objects.get(id = i)
                        bran = Branch.objects.get(id = course.Branch.id)
                        instiid = College.objects.get( user = id)   
                        instbranch = collegeCourse.objects.create(college = instiid ,courseCode = course.CourseCode,branchId = bran, courseId = course, Status = course.Status)
                        instbranch.save()
                print("saved")
                return redirect('college_course')
            elif request.user.is_institute:
                code = request.POST['course_code']
                branch = request.POST['branch']
                course = request.POST['course']
                fee = request.POST['fee']
                status = request.POST['status']
                userid =  request.user.id
                instiid = College.objects.get( user = userid)      
                course = collegeCourse.objects.create(college = instiid.id,courseCode = code,courseFee = fee, branchId = branch, courseId = course, Status = status)
                course.save()
                return redirect(college_course)
            else:
                return HttpResponse("You have No Permission")
    except Exception as e:
        print(str(e))
    if request.user.is_superuser:
        userid = request.session['defaultcollege']
        userid = int(userid)
        if userid == 0:
            insticou = collegeCourse.objects.all().order_by('id')
            instibranch = collegeBranch.objects.all().order_by('id')
        else:
            print(userid)
            instiid = College.objects.get( user = userid)   
            insticou = collegeCourse.objects.filter(college = instiid)
            instibranch = collegeBranch.objects.filter(college = instiid).values()
            print(instibranch)
        paginator = Paginator(insticou,10)
        try:
            page = int(request.GET.get('page','1'))
        except:
            page = 1
        try:
            insticourse = paginator.page(page)
        except(EmptyPage,InvalidPage):
            insticourse = paginator.page(paginator.num_pages)   
        course = Course.objects.all()
        c  = []
        if userid > 0:
            for data in instibranch:
                print(data['branchId_id'])
                branch = Branch.objects.get(id = data['branchId_id'])
                print(branch)
                courses = Course.objects.filter(Branch = branch)
                print(courses)
                for i in courses:                
                    courseid  = i.id
                    CourseName = i.CourseName
                    co = {"id" : courseid,"name" : CourseName}
                    c.append(co)  
        print(insticou)  
        
        branch = Branch.objects.all()    
        sup = SupportingDoc.objects.all()
        return render(request,'college-course.html',{'insticoures':insticou,'branch':branch,'instibranch':instibranch,'c':c,'sup':sup})
    elif request.user.is_institute :        
        userid =  request.user.id
        instiid = Institution.objects.get( user = userid) 
        insticou = institutionCourse.objects.filter(institutionId = instiid.id)
        instibran = instituteBranch.objects.all().order_by('id')
        paginator = Paginator(insticou,10)
        try:
            page = int(request.GET.get('page','1'))
        except:
            page = 1
        try:
            insticourse = paginator.page(page)
        except(EmptyPage,InvalidPage):
            insticourse = paginator.page(paginator.num_pages)   
        instibranch = instituteBranch.objects.filter(institutionId = instiid.id).values()
        branch = Branch.objects.all()
        print(instibranch)
        course = Course.objects.all()        
        sup = SupportingDoc.objects.all()
        return render(request,'college-course.html',{'insticoures':insticourse,'branch':branch,'instibranch':instibranch,'course':course,'sup':sup})
    else:
        return HttpResponse("You dont have enough permission")




@csrf_exempt
def list_college_course(request):
    if request.method == "POST":
        id = request.POST['id']
        courses = institutionCourse.objects.get(id = id)
        code = courses.courseCode
        branch = courses.branchId_id
        course = courses.courseId_id
        fee = 1
        ID = courses.id
        status = courses.Status
        print(status)
        context = [code,branch,course,fee,ID,status]
        print(context)
        data = json.dumps(context)
        return HttpResponse(data)


@csrf_exempt
def list_institue_course_fee(request):
    if request.method == "POST":
        id = request.POST['id']
        fee = feeStructure.objects.filter( id = int(id)).values()
        addmission_fee = fee[0]['Admissionfee']
        tution_fee = fee[0]['Tutionfee'] 
        exam_fee = fee[0]['Examfee'] 
        mark_card_fee = fee[0]['MarksCardfee'] 
        caution_deposit = fee[0]['CautionDeposit'] 
        library_fee = fee[0]['Libraryfee'] 
        sports_fee = fee[0]['Sportsfee'] 
        reg_fee = fee[0]['Registrationfee'] 
        course = fee[0]['institutionCourse_id']
        context = [addmission_fee,tution_fee,exam_fee,mark_card_fee,caution_deposit,library_fee,sports_fee,reg_fee,id,course]
        courses = institutionCourse.objects.get(id = course)
        oth = otherFeeStructure.objects.filter(parent = courses)
        qs_as_dict = serializers.serialize('python', oth)
        data = json.dumps(qs_as_dict)
        cont = json.dumps(context)
        return HttpResponse(cont)

@csrf_exempt
def list_institue_course_otherfee(request):
    if request.method == "POST":
        id = request.POST['id']
        fee = feeStructure.objects.filter( id = int(id)).values()
        course = fee[0]['institutionCourse_id']
        courses = institutionCourse.objects.get(id = course)
        oth = otherFeeStructure.objects.filter(parent = courses)
        qs_as_dict = serializers.serialize('python', oth)
        data = json.dumps(qs_as_dict)
        return HttpResponse(data)



@csrf_exempt  
@login_required(login_url="login")    
def update_institutecourse_fee(request):
    if request.method == "POST":
        if request.user.is_superuser:
            id = request.POST['id']            
            fee = feeStructure.objects.get(id = id)
            co = fee.institutionCourse
            x = request.POST['course']
            course = institutionCourse.objects.get(id = x)
            for key, value in request.POST.items():
                try:
                    if key == 'course':
                        fee.institutionCourse = course
                        fee.save()   
                        oth = otherFeeStructure.objects.filter(parent = co )
                        for o in oth:
                            other = otherFeeStructure.objects.get(id = o.id)
                            course = institutionCourse.objects.get(id = x)
                            other.parent = course
                            other.save()
                    elif key == 'id':
                        pass              
                    elif key == 'addmission_fee':
                        x = int(value)
                        fee.Admissionfee = x
                        fee.save()                
                    elif key =='tution_fee':
                        x = int(value)
                        fee.Tutionfee = x
                        fee.save()
                    elif key == 'exam_fee':
                        x = int(value)
                        fee.Examfee = x
                        fee.save()
                    elif key == 'mark_card_fee':
                        x = int(value)
                        fee.MarksCardfee = x
                        fee.save()
                    elif key == 'caution_deposit':
                        x = int(value)
                        fee.CautionDeposit = x
                        fee.save()
                    elif key== 'library_fee':
                        x = int(value)
                        fee.Libraryfee = x
                        fee.save()
                    elif key == 'sports_fee':
                        x = int(value)
                        fee.Sportsfee = x
                        fee.save()
                    elif key == 'registration_fee':
                        x = int(value)
                        fee.Registrationfee = x
                        fee.save()
                    else:
                        update_institutecourse_otherfee(key,value)
                except:
                    pass
                
            return redirect('institutecourse_fee')


@csrf_exempt
def update_institutecourse_otherfee(pk,value):
    other = otherFeeStructure.objects.get(id = int(pk))
    other.value = value
    other.save()
    return other

@csrf_exempt  
@login_required(login_url="login")  
def course_type(request):
    if request.method == "POST":
        name = request.POST['name']
        status = request.POST['status']
        course_type = courseType(name = name, Status = status)
        course_type.save()
        return redirect('course_type')

    ct = courseType.objects.all
    print(ct)
    return render(request,'course-type.html',{'sup_doc': ct})


@csrf_exempt
def list_course_type(request):
    if request.method == "POST":
        id = request.POST['id']
        instance = courseType.objects.filter(id=id).values()
        Name = instance[0]['name']
        Status = instance[0]['Status']
        ID = instance[0]['id']
        context = [Name,Status,ID]
        print(context)
        data = json.dumps(context)
        return HttpResponse(data)
    return HttpResponse("hello")

@csrf_exempt 
def update_course_type(request):

    if request.method == "POST":
        ID = request.POST['_id']
        
        Name = request.POST['name']
        status = request.POST['status']
        doc = courseType.objects.get(id = ID)
        doc.name = Name
        doc.Status = status
        doc.save()
        messages.warning(request, "Course Type updated successfully!")

    return redirect('course_type')

@csrf_exempt
def delete_course_type(request):
    if request.method == "POST":
        id = request.POST["id"]
        instance = courseType.objects.filter(id=id)
        instance.delete()
        messages.warning(request, "Course Type deleted successfully!")
        # return redirect(branch)
        data = {
        'is_taken': "deleted"
        }
        
        return JsonResponse(data)
    return redirect('course_type')