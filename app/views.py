from django.shortcuts import render, get_object_or_404
from django.contrib.auth import authenticate
from django.shortcuts import redirect
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib import messages
from django.contrib.auth.models import User, Group
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache, cache_control
from datetime import datetime
from app.models import *
from datetime import date

# Create your views here.
@never_cache
def home(request):
    return render(request, 'home.html')




@login_required(login_url='login')
@never_cache
def logout_user(request):
    logout(request)              # Django logout
    request.session.flush()      # Clear session
    messages.success(request, "Logged out successfully.")
    return redirect('login')     # Redirect to login page




@csrf_exempt
@never_cache
def login(request):
    if request.method == "POST":
        uname = request.POST['uname']
        password = request.POST['password']
        a = User.objects.filter(username=uname).first()
        if a:
            if uname==a.username:

                user = authenticate(request, username=uname, password=password)
                print("USER : ", user)

                if user is not None:
                    auth_login(request, user)
                    request.session['user_id'] = user.id  # Auth user ID

                    if user.groups.filter(name='admin').exists():
                        return redirect('admin_home')
                        
                    elif user.groups.filter(name='user').exists():
                        user_profile  = User_Profile.objects.get(USER=user)
                        request.session['user'] = user_profile.id
                        return redirect('user_home')
                    
                    elif user.groups.filter(name='police').exists():
                        try:
                            police  = Police_Station.objects.get(USER=user)

                            # ✅ Check approval status
                            if police.approval_status.lower() == 'approved':
                                request.session['police'] = police.id
                                return redirect('police_home')
                            else:
                                messages.warning(
                                    request,
                                    f"Your profile is not approved yet."
                                )
                                return redirect('login')

                        except police.DoesNotExist:
                            messages.error(request, "No profile found for this user.")
                            return redirect('login')
                        
                        
                        
                    else:
                        messages.error(request, 'Invalid username or password')
                        return redirect('login')
                else:
                    messages.error(request, 'Username or password incorrect')
            else:
                    messages.error(request, 'Invalid username')
                    return redirect('login')
            
        else:
            messages.error(request, 'No such user exist in this platform')
            return redirect('login')
    return render(request, 'login.html')








# ------------------------------------------ ADMIN ---------------------------------------------------------------------



# @csrf_exempt
# @never_cache
# @cache_control(no_cache=True, must_revalidate=True, no_store=True)

@login_required(login_url='login')
@never_cache
def admin_home(request):
    return render(request, 'admin_home.html')





@login_required(login_url='login')
@never_cache
def admin_verify_police(request):
    a=Police_Station.objects.all()

    return render(request, 'admin_verify_police.html', {'a': a})




def admin_approve_police(request,id):
    a=Police_Station.objects.get(id=id)
    a.approval_status="approved"
    a.save()
    messages.success(request, 'Police station Approved.')
    return redirect('admin_verify_police')


def admin_reject_police(request,id):
    a=Police_Station.objects.get(id=id)
    a.approval_status="rejected"
    a.save()
    messages.success(request, 'Police station Rejected.')
    return redirect('admin_verify_police')



@login_required(login_url='login')
@never_cache
def admin_view_missing_data(request, id):
    police = Police_Station.objects.get(id=id)

    records = Missing_Child_Data.objects.filter(POLICE_STATION=police)

    final_data = {}

    for r in records:
        case = r.CASE_REPORT

        if case.id not in final_data:
            final_data[case.id] = {
                "case": case,
                "progress_list": []
            }

        final_data[case.id]["progress_list"].append(r.progress)

    return render(request, "admin_view_missing_data.html", {"data": final_data.values()})




@login_required(login_url='login')
@never_cache
@csrf_exempt
def admin_manage_awareness(request):
    if request.method == "POST":
        title=request.POST['title']
        desc=request.POST['desc']
        file = request.FILES.get('file')

        # Create care center profile
        Awareness.objects.create(
            title=title,
            description=desc,
            file=file,
            date=date.today(),

        )

        messages.success(request, 'Awareness details added.')
    a = Awareness.objects.all()

    return render(request, 'admin_manage_awareness.html', {'a': a})



@login_required(login_url='login')
@never_cache
@csrf_exempt
def admin_update_awareness(request, id):
    a = Awareness.objects.get(id=id)

    if request.method == "POST":
        title = request.POST.get('title')
        desc = request.POST.get('desc')

        uploaded_file = request.FILES.get('file')

        # Update fields
        a.title = title
        a.description = desc
        a.date = date.today()

        # Update file ONLY if user uploaded a new one
        if uploaded_file:
            a.file = uploaded_file

        a.save()

        messages.success(request, 'Awareness details updated')
        return redirect('admin_manage_awareness')

    return render(request, 'admin_update_awareness.html', {'a': a})





@login_required(login_url='login')
@never_cache
def admin_delete_awareness(request,id):
    a=Awareness.objects.get(id=id)
    a.delete()
      
    messages.success(request, 'Awareness details Deleted.')

    return redirect('admin_manage_awareness')




@login_required(login_url='login')
@never_cache
@csrf_exempt
def admin_view_complaints(request):
    a = Complaint.objects.all()

    if request.method == "POST":
        id = request.POST['id']
        reply = request.POST['reply']

        b = Complaint.objects.get(id=id)
        b.reply = reply
        b.save()

        messages.success(request, 'Reply Sent.')

        return redirect("admin_view_complaints")

    return render(request, 'admin_view_complaints.html', {'a': a})



# ------------------------------------------ POLICE ------------------------------------------------------------------------------------

@never_cache
@csrf_exempt
def police_registration(request):
    if request.method == "POST":
        sname = request.POST['sname']
        place = request.POST['place']
        phone = request.POST['phone']
        email = request.POST['email']
        latitude = request.POST['latitude']
        longitude = request.POST['longitude']
        sho_id = request.POST['id']
        username = request.POST['username']
        password = request.POST['password']

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
            return redirect('police_registration')

        # Create user using Django's auth system
        user = User.objects.create_user(username=username, password=password)
        user.save()

        try:
            group = Group.objects.get(name='police')
        except Group.DosNotExist:
            group = Group.objects.create(name='police')
        user.groups.add(group)

        # Create care center profile
        Police_Station.objects.create(
            USER=user,
            station_name=sname,
            place=place,
            phone=phone,
            email=email,
            latitude=latitude,
            longitude=longitude,
            approval_status='pending',
            sho_id=sho_id,
        )

        messages.success(request, 'Registration Completed. Please Wait for the Approval')

    return render(request, 'police_registration.html')


# @csrf_exempt
def police_home(request):
    return render(request, 'police_home.html')



from math import radians, sin, cos, asin, sqrt

def haversine(lat1, lon1, lat2, lon2):
    # convert to radians
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

    # haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    r = 6371  # radius of earth in km
    return c * r



# @login_required(login_url='login')
# @never_cache
# def police_view_case_report(request):
#     police = Police_Station.objects.get(USER=request.user)

#     police_lat = float(police.latitude)
#     police_lon = float(police.longitude)

#     cases = Case_Report.objects.all()

#     # attach distance value to each case
#     nearby_cases = []
#     for c in cases:
#         case_lat = float(c.latitude)
#         case_lon = float(c.longitude)

#         distance = haversine(police_lat, police_lon, case_lat, case_lon)

#         nearby_cases.append({
#             "case": c,
#             "distance": round(distance, 2)
#         })

#     # sort by nearest first
#     nearby_cases = sorted(nearby_cases, key=lambda x: x["distance"])


#     return render(request, 'police_view_case_report.html',  {"cases": nearby_cases})

@login_required(login_url='login')
@never_cache
def police_view_case_report(request):
    police = Police_Station.objects.get(USER=request.user)

    if "accept_id" in request.GET:
        case_id = request.GET.get("accept_id")
        case = Case_Report.objects.get(id=case_id)
        case.status = "accepted"
        case.save()

        exists = Missing_Child_Data.objects.filter(POLICE_STATION=police, CASE_REPORT=case).exists()
        if not exists:
            Missing_Child_Data.objects.create(
                POLICE_STATION=police,
                CASE_REPORT=case,
                progress="missing"
            )

        messages.success(request, "Case accepted successfully!")
        return redirect("police_view_case_report")

    if request.method == "POST":
        case_id = request.POST.get("case_id")
        progress_value = request.POST.get("progress_value")

        case = Case_Report.objects.get(id=case_id)
        mcd = Missing_Child_Data.objects.filter(POLICE_STATION=police, CASE_REPORT=case).first()

        if mcd:
            mcd.progress = progress_value
            mcd.save()

        messages.success(request, "Progress updated successfully!")
        return redirect("police_view_case_report")

    police_lat = float(police.latitude)
    police_lon = float(police.longitude)

    cases = Case_Report.objects.all()
    nearby_cases = []

    for c in cases:
        case_lat = float(c.latitude)
        case_lon = float(c.longitude)
        distance = haversine(police_lat, police_lon, case_lat, case_lon)

        mcd = Missing_Child_Data.objects.filter(POLICE_STATION=police, CASE_REPORT=c).first()
        progress = mcd.progress if mcd else "Not Accepted"

        nearby_cases.append({
            "case": c,
            "distance": round(distance, 2),
            "progress": progress
        })

    nearby_cases = sorted(nearby_cases, key=lambda x: x["distance"])

    return render(request, 'police_view_case_report.html', {"cases": nearby_cases})



@login_required(login_url='login')
def police_accept_report(request, case_id):
    case = Case_Report.objects.get(id=case_id)
    case.status = "accepted"
    case.save()

    police = Police_Station.objects.get(USER=request.user)

    Missing_Child_Data.objects.create(
        POLICE_STATION=police,
        CASE_REPORT=case,
        progress="missing"
    )

    messages.success(request, "Case Accepted Successfully")
    return redirect("police_view_case_report")




@login_required(login_url='login')
def police_view_user(request, case_id):
    case = get_object_or_404(Case_Report, id=case_id)
    user_profile = case.USER_PROFILE  # Reporter details

    return render(request, "police_view_user.html", {
        "case": case,
        "user": user_profile
    })


@login_required(login_url='login')
def police_update_progress(request, case_id):
    if request.method == "POST":
        progress_value = request.POST.get("progress_value")

        police = Police_Station.objects.get(USER=request.user)
        case = Case_Report.objects.get(id=case_id)

        mcd = Missing_Child_Data.objects.get(
            POLICE_STATION=police,
            CASE_REPORT=case
        )

        mcd.progress = progress_value
        mcd.save()

        messages.success(request, "Progress updated successfully!")
        return redirect('police_view_case_report')



@login_required(login_url='login')
@never_cache
def police_view_public_report(request):

    police = Police_Station.objects.get(USER=request.user)

    # --- UPDATE PROGRESS (POST) ---
    if request.method == "POST":
        public_id = request.POST.get("public_id")
        progress_value = request.POST.get("progress_value")

        public_report = Public_Upload.objects.get(id=public_id)
        mcd = public_report.MISSING_CHILD_DATA
        
        mcd.progress = progress_value
        mcd.save()

        messages.success(request, "Progress updated successfully!")
        return redirect("police_view_public_report")

    # --- NEAREST PUBLIC REPORTS ---
    police_lat = float(police.latitude)
    police_lon = float(police.longitude)

    public_reports = Public_Upload.objects.all()

    nearby_reports = []

    for p in public_reports:
        report_lat = float(p.latitude)
        report_lon = float(p.longitude)

        distance = haversine(police_lat, police_lon, report_lat, report_lon)

        nearby_reports.append({
            "report": p,
            "distance": round(distance, 2),
            "progress": p.MISSING_CHILD_DATA.progress
        })

    # sort by nearest
    nearby_reports = sorted(nearby_reports, key=lambda x: x["distance"])

    return render(request, "police_view_public_report.html", {
        "reports": nearby_reports
    })

#POLICE REJECT REPORT
@login_required(login_url='login')
def police_reject_report(request, case_id):
    case = Case_Report.objects.get(id=case_id)
    case.status = "rejected"
    case.save()

    messages.error(request, "Case Rejected.")
    return redirect("police_view_case_report")

#POLICE UPDATE STATUS
@login_required(login_url='login')
def police_update_status(request, case_id):
    case = Case_Report.objects.get(id=case_id)
    new_status = request.POST.get("status_value")

    case.status = new_status
    case.save()

    police = Police_Station.objects.get(USER=request.user)

    data = Missing_Child_Data.objects.filter(
        CASE_REPORT=case,
        POLICE_STATION=police
    ).first()

    if not data:
        data = Missing_Child_Data.objects.create(
            CASE_REPORT=case,
            POLICE_STATION=police,
            progress=new_status
        )
    else:
        data.progress = new_status
        data.save()

    messages.success(request, "Status Updated Successfully.")
    return redirect("police_view_case_report")



# ------------------------------------------ USER------------------------------------------------------------------------


def user_home(request):
    return render(request, 'user_home.html')


@never_cache
@csrf_exempt
def user_registration(request):
    if request.method == "POST":
        fname = request.POST['fname']
        lname = request.POST['lname']
        email = request.POST['email']
        phone = request.POST['phone']
        place = request.POST['place']
        address = request.POST['address']
        alt_no = request.POST['alt_no']
        proof = request.FILES['proof']
        username = request.POST['username']
        password = request.POST['password']

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
            return redirect('user_registration')

        # Create user using Django's auth system
        user = User.objects.create_user(username=username, password=password)
        user.save()

        try:
            group = Group.objects.get(name='user')
        except Group.DosNotExist:
            group = Group.objects.create(name='user')
        user.groups.add(group)

        # Create care center profile
        User_Profile.objects.create(
            USER=user,
            fname=fname,
            lname=lname,
            email=email,
            phone=phone,
            place=place,
            id_proof=proof,
            address=address,
            alternative_ph_no=alt_no,
        )

        messages.success(request, 'Registration Completed.')

    return render(request, 'user_registration.html')

#USER PROFILE
@login_required
def user_profile(request):
    user = request.user

    # Get or Create profile if missing
    profile, created = User_Profile.objects.get_or_create(USER=user)

    if request.method == "POST":
        profile.fname = request.POST.get("fname")
        profile.lname = request.POST.get("lname")
        profile.email = request.POST.get("email")
        profile.phone = request.POST.get("phone")
        profile.place = request.POST.get("place")
        profile.address = request.POST.get("address")
        profile.alternative_ph_no = request.POST.get("alternative_ph_no")

        if request.FILES.get("id_proof"):
            profile.id_proof = request.FILES.get("id_proof")

        profile.save()

        user.email = profile.email
        user.save()

        messages.success(request, "Profile updated successfully!")
        return redirect("user_profile")

    return render(request, "user_profile.html", {"profile": profile})

#SUBMIT CASE
# @login_required
# def submit_case(request):
#     user = request.user
#     profile = User_Profile.objects.get(USER=user)
#
#     if request.method == "POST":
#         child_name = request.POST.get("child_name")
#         age = request.POST.get("age")
#         gender = request.POST.get("gender")
#         hair_color = request.POST.get("hair_color")
#         height = request.POST.get("height")
#         scar_mark = request.POST.get("scar_mark")
#         dress_color = request.POST.get("dress_color")
#         missing_place = request.POST.get("missing_place")
#         details = request.POST.get("details")
#         latitude = request.POST.get("latitude")
#         longitude = request.POST.get("longitude")
#         date = request.POST.get("date")
#         time = request.POST.get("time")
#         image = request.FILES.get("image")
#
#         Case_Report.objects.create(
#             USER_PROFILE=profile,
#             child_name=child_name,
#             age=age,
#             gender=gender,
#             hair_color=hair_color,
#             height=height,
#             scar_mark=scar_mark,
#             dress_color=dress_color,
#             image=image,
#             missing_place=missing_place,
#             details=details,
#             latitude=latitude,
#             longitude=longitude,
#             date=date,
#             time=time,
#             status="Pending"
#         )
#
#         messages.success(request, "Case submitted successfully!")
#         return redirect("submit_case")
#
#     return render(request, "submit_case.html")

import os
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.conf import settings
from .models import Case_Report, User_Profile
from .train import MissingChildTrainer


@login_required
def submit_case(request):
    user = request.user
    profile = User_Profile.objects.get(USER=user)

    if request.method == "POST":
        child_name = request.POST.get("child_name")
        age = request.POST.get("age")
        gender = request.POST.get("gender")
        hair_color = request.POST.get("hair_color")
        height = request.POST.get("height")
        scar_mark = request.POST.get("scar_mark")
        dress_color = request.POST.get("dress_color")
        missing_place = request.POST.get("missing_place")
        details = request.POST.get("details")
        latitude = request.POST.get("latitude")
        longitude = request.POST.get("longitude")
        date = request.POST.get("date")
        time = request.POST.get("time")
        image = request.FILES.get("image")

        case = Case_Report.objects.create(
            USER_PROFILE=profile,
            child_name=child_name,
            age=age,
            gender=gender,
            hair_color=hair_color,
            height=height,
            scar_mark=scar_mark,
            dress_color=dress_color,
            image=image,
            missing_place=missing_place,
            details=details,
            latitude=latitude,
            longitude=longitude,
            date=date,
            time=time,
            status="pending"
        )

        train_folder = os.path.join(settings.MEDIA_ROOT, "missing_train", str(case.id))
        os.makedirs(train_folder, exist_ok=True)

        img_path = case.image.path
        new_path = os.path.join(train_folder, os.path.basename(img_path))

        with open(img_path, "rb") as src:
            with open(new_path, "wb") as dst:
                dst.write(src.read())

        try:
            trainer = MissingChildTrainer(
                model_path=os.path.join(settings.BASE_DIR, "missing_child_model.pkl")
            )

            trainer.add_person(
                person_id=case.id,
                person_name=case.child_name,
                folder_path=train_folder
            )

            trainer.save_model()
            messages.success(request, "Case submitted and model trained successfully!")

        except Exception as e:
            messages.error(request, f"Case saved, but training failed: {e}")

        return redirect("submit_case")

    return render(request, "submit_case.html")


# USER VIEW PROGRESS
@login_required
def view_case_progress(request):
    profile = User_Profile.objects.get(USER=request.user)
    case_reports = Case_Report.objects.filter(USER_PROFILE=profile)

    data = []
    for case in case_reports:
        progress_records = Missing_Child_Data.objects.filter(CASE_REPORT=case)
        data.append({
            "case": case,
            "progress": progress_records
        })

    return render(request, "view_case_progress.html", {"data": data})


#USER VIEW AWARENESS
@login_required
def user_view_awareness(request):
    awareness_items = Awareness.objects.all().order_by('-id')
    return render(request, "user_view_awareness.html", {"items": awareness_items})

#USER SEND COMPLAINTS
@login_required
def user_complaint(request):
    profile = User_Profile.objects.get(USER=request.user)

    # Submit complaint
    if request.method == "POST":
        complaint_text = request.POST.get("complaint")

        Complaint.objects.create(
            USER_PROFILE=profile,
            complaint=complaint_text,
            reply="pending",
            date=datetime.now().strftime("%Y-%m-%d")
        )

        messages.success(request, "Complaint submitted successfully!")
        return redirect("user_complaint")

    # Fetch all complaints by this user
    complaints = Complaint.objects.filter(USER_PROFILE=profile).order_by('-id')

    return render(request, "user_complaint.html", {"complaints": complaints})


#PREDICT MISSING CHILD
from .predict import MissingChildPredictor

def predict_child(request):
    result = None

    if request.method == "POST":
        uploaded = request.FILES.get("photo")

        if not uploaded:
            messages.error(request, "Please upload an image!")
            return render(request, "predict_child.html", {"result": None})

        temp_path = os.path.join(settings.MEDIA_ROOT, "predict_temp.jpg")

        # Save temp uploaded image
        with open(temp_path, "wb+") as f:
            for chunk in uploaded.chunks():
                f.write(chunk)

        try:
            predictor = MissingChildPredictor(
                model_path=os.path.join(settings.BASE_DIR, "missing_child_model.pkl")
            )
            result = predictor.predict(temp_path)

        except Exception as e:
            messages.error(request, f"Prediction failed: {e}")
            result = {"status": "error", "message": str(e)}

    return render(request, "predict_child.html", {"result": result})
