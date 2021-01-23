from django.shortcuts import render, redirect, HttpResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Contact, CustomUser
from .Serializer import ContactSerializer
from django.contrib.auth import logout, login, authenticate
from django.core.paginator import Paginator


# Template Provider
def home(request):
    if request.user.is_authenticated:
        user = CustomUser.objects.filter(email=request.user)
        context = {"owner_name": user[0].first_name, "owner_email": user[0].email}
        return render(request, template_name='contact.html', context=context)
    return render(request, template_name='base.html')


# User Methods
def logIn(request):
    if request.user.is_authenticated:
        return redirect('/')
    else:
        cred = request.POST
        email = cred['email']
        passwd = cred['password']

        res = authenticate(request, username=email, password=passwd)

        if res is not None:
            login(request,res)
            return redirect('/')
        else:
            return redirect('/?wrong+email+or+passwd')


def logOut(request):
    if request.user.is_authenticated:
        logout(request)
    return redirect('/')




@api_view(['POST'])
def register(request):
    if request.user.is_authenticated:
        return redirect('/')
    else:
        cred = request.data
        print(cred)
        c = CustomUser.objects.filter(email=cred[1]['value'])
        if len(c) == 0:
            user = CustomUser(first_name=cred[0]['value'], username=cred[1]['value'], email=cred[1]['value'])
            user.set_password(cred[2]['value'])
            user.save()
            return Response("success")
        else:
            return Response("This Email Already Exists!")


# Contact CRUD & Search methods
@api_view(['POST'])
def create(request):
    if request.user.is_authenticated:
        user = CustomUser.objects.get(username=request.user)
        data = request.data
        duplicates = Contact.objects.filter(email=data['email'], owner=user)
        if len(duplicates) == 0:
            newContact = Contact(owner=user, email=data['email'], name=data['name'].capitalize())
            for info in data:
                if info == 'phone1':
                    newContact.phone1 = data[info]
                if info == 'phone2':
                    newContact.phone2 = data[info]
                if info == 'address':
                    newContact.address = data[info]
            newContact.save()
            return Response("ContactAdded")
        else:
            return Response("EmailAddressAlreadyExistsInYourContactBook")


@api_view(['GET'])
def read(request, email):
    if request.user.is_authenticated:
        user = CustomUser.objects.get(username=request.user)
        contact = Contact.objects.filter(email=email)
        if len(contact) == 0:
            return Response("NoSuchContact")
        if contact[0].owner.email == user.email:
            contact = ContactSerializer(contact[0])
            return Response(contact.data)
        else:
            return HttpResponse("InvalidRequest")


@api_view(['GET'])
def readAll(request):
    if request.user.is_authenticated:
        user = CustomUser.objects.filter(email=request.user)
        c = getAllContacts(user[0])
        return Response(c)
    else:
        return Response("un-authenticated")


@api_view(['POST'])
def update(request):
    if request.user.is_authenticated:
        user = CustomUser.objects.get(username=request.user)
        data = request.data
        contact_to_update = Contact.objects.filter(email=data['key'])
        if len(contact_to_update) == 0:
            return Response("NoSuchContactFound")
        elif contact_to_update[0].owner.email != user.email:
            return Response("InvalidRequest")
        else:
            newContact = contact_to_update[0]
            for info in data:
                if info == 'name':
                    newContact.name = data[info].capitalize()
                if info == 'phone1':
                    newContact.phone1 = data[info]
                if info == 'phone2':
                    newContact.phone2 = data[info]
                if info == 'address':
                    newContact.address = data[info]
                if info == 'email':
                    temp = Contact.objects.filter(email=data[info])
                    if len(temp) != 0:
                        if temp[0].email == contact_to_update[0].email:
                            pass
                        else:
                            return Response("UpdateOperationFailedAsEmailAlreadyExistInContactBook")
                    else:
                        newContact.email = data[info]
            newContact.save()
            return Response("ContactUpdated")
    else:
        return Response("un-authenticated")


@api_view(['GET'])
def delete(request, email):
    if request.user.is_authenticated:
        user = CustomUser.objects.get(username=request.user)
        contact = Contact.objects.filter(email=email)
        if len(contact) == 0:
            return Response("NoSuchContact")
        if contact[0].owner.email == user.email:
            Contact.delete(contact[0])
            return Response("Deleted")
        else:
            return HttpResponse("InvalidRequest")
    else:
        return Response("un-authenticated")


@api_view(['GET'])
def search(request):
    key = request.GET['q']
    page = request.GET['page']
    user = CustomUser.objects.filter(username=request.user)
    if "@" in key and "." in key and str(key).count("@") == 1:
        contacts = Contact.objects.filter(owner=user[0], email=key)
    else:
        contacts = Contact.objects.filter(owner=user[0], name__contains=key)

    pagination = Paginator(contacts, 10)
    result = pagination.get_page(page)
    data = ContactSerializer(result.object_list, many=True)

    return Response({"has_next_page": result.has_next(), "has_previous_page": result.has_previous(),
                     "current_page_number": result.number, "end_index":result.end_index(),
                     "total_results_found": len(contacts), "search_results": data.data,
                     })


def getAllContacts(user_obj):
    contacts = Contact.objects.filter(owner=user_obj).order_by('name')
    temp = ContactSerializer(contacts, many=True)
    serial_data = temp.data
    return serial_data

