from django.shortcuts import render, redirect
from django.http import HttpResponse
from courses.models import Course
from googleapiclient.discovery import build
from learnrack.decorators import login_required
import os
from dotenv import load_dotenv
load_dotenv()
import http.client
import json
youtube = build('youtube', 'v3', developerKey=os.environ.get('YOUTUBE_API_KEY'),static_discovery=False)
# Create your views here.
def video_list(PLAYLIST_ID):
    request_params = {
        'playlistId': PLAYLIST_ID,
        'part': 'snippet',
        'maxResults': 50,
    }
    video_ids=[]
    while True:
    # Call the playlistItems().list() method to retrieve the list of videos in the playlist
        request = youtube.playlistItems().list(**request_params)
        # Execute the request and get the response
        response = request.execute()
        # Iterate through the items in the response and store the video IDs
        for item in response['items']:
            video_id = item['snippet']['resourceId']['videoId']
            video_ids.append(video_id)
        # Check if there are more pages to process
        if 'nextPageToken' in response:
            # Update the request parameters with the next page token
            request_params['pageToken'] = response['nextPageToken']
        else:
            # If there are no more pages, break out of the loop
            break
    return video_ids


@login_required
def new_course_page(request):
    return render(request, 'new_course.html')

@login_required
def new_course(request):
    user=request.user
    print(request.POST)
    if request.method=='POST':
        url=request.POST['url']
        playlist_id=url.replace('https://www.youtube.com/playlist?list=', '')
        video_ids=video_list(playlist_id)
        request = youtube.playlists().list(
        part='id,snippet',
        id=playlist_id
        )
        response = request.execute()
        title=response['items'][0]['snippet']['title']
        description=response['items'][0]['snippet']['description']
        thumbnail_url=response['items'][0]['snippet']['thumbnails']['high']['url']
        channel_name=response['items'][0]['snippet']['channelTitle']
        course=Course.objects.create(
            url=url,
            playlist_id=playlist_id,
            user=user,
            title=title,
            description=description,
            channel_name=channel_name,
            thumbnail_url=thumbnail_url,
            video_ids=video_ids)
        return redirect('dashboard')
    else:
        return redirect('home')


@login_required
def course_detail(request, course_id):
    course=Course.objects.get(id=course_id)
    if request.user==course.user:
        all_videos=Course.objects.get(id=course_id).video_ids
        watched_videos=Course.objects.get(id=course_id).watched_videos
        unwatched_videos=[]
        for video in all_videos:
            if video not in watched_videos:
                unwatched_videos.append(video)
        if watched_videos==[]:
            previous_video="False"
        else:
            previous_video=watched_videos[0]
        if len(watched_videos)==1:
            next_video="False"
        else:
            next_video=unwatched_videos[1]
        current_video=unwatched_videos[0]
        return render(request, 'course_detail.html', {
            'course': course,
            'previous_video': previous_video,
            'next_video': next_video,
            'current_video': current_video,})

    else:
        return redirect('dashboard')

@login_required
def course_delete(request, course_id):
    course=Course.objects.get(id=course_id)
    course.delete()
    return redirect('home')

@login_required
def course_update(request, course_id):
    course=Course.objects.get(id=course_id)
    if request.method=='POST':
        notes=request.POST['notes']
        course.notes=notes
        course.save()
        return HttpResponse('success')
    else:
        return render(request, 'course_update.html', {'course':course})

@login_required
def course_notes(request, course_id):
    course=Course.objects.get(id=course_id)
    if request.user==course.user:
        return render(request, 'course_notes.html', {'course':course})
    else:
        return redirect('dashboard')

@login_required
def video_watch(request, course_id, video_id):
    course=Course.objects.get(id=course_id)
    if request.user==course.user:
        if video_id not in course.watched_videos:
            course.watched_videos.append(video_id)
            course.save()
            next_video_id=course.video_ids[course.video_ids.index(video_id)+1]
            return redirect('video_page', course_id=course_id, video_id=next_video_id)
        return redirect('dashboard ')
    else:
        return redirect('dashboard')


@login_required
def video_page(request, course_id, video_id):
    course=Course.objects.get(id=course_id)
    if video_id in course.video_ids:
        request_f = youtube.videos().list(
            part='id,snippet',
            id=video_id
        )
        response = request_f.execute()
        title = response['items'][0]['snippet']['title']
        description = response['items'][0]['snippet']['description']
        video_list=[]
        init_in=course.video_ids.index(video_id)-5
        if init_in<0:
            init_in=0
        final_in=course.video_ids.index(video_id)+5
        for i in course.video_ids[init_in:final_in]:
            request_f = youtube.videos().list(
                part='id,snippet',
                id=i
            )
            response = request_f.execute()
            video_list.append((i,response['items'][0]['snippet']['title']))

        return render(request, 'vid.html', {
            'course':course,
            'video_id':video_id,
            'title':title,
            'description':description,
            'video_names':video_list,})
    else:
        return redirect('dashboard')
    return render(request, 'video.html', {'course_id':course_id, 'video_id':video_id})

@login_required
def notes_update(request):
    course_id=request.POST['course_id']
    course=Course.objects.get(id=course_id)
    if request.method=='POST':
        if request.user==course.user:
            notes=request.POST['textarea']
            course.notes=notes
            course.save()
            if request.POST['sub']=="download":
                ret_url=notes_to_pdf(course.title,course.notes)
                return redirect(ret_url)
            return redirect(request.META.get('HTTP_REFERER', f'/courses/{course_id}/notes/'))
        else:
            return redirect('dashboard')
    else:
        return redirect('dashboard')


def notes_to_pdf(title,text):
    conn = http.client.HTTPSConnection("api.apyhub.com")

    headersList = {
    "Accept": "*/*",
    "User-Agent": "Thunder Client (https://www.thunderclient.com)",
    "apy-token": f"{os.getenv('APY_TOKEN')}",
    "Content-Type": "application/json" 
    }

    payload = json.dumps({

        "content":f" <html> <body> <h1> {title} </h1> {text} </body> </html> "

    })

    conn.request("POST", f"/generate/html-content/pdf-url?output=.pdf", payload, headersList)
    response = conn.getresponse()
    result = response.read()
    d=eval(result.decode("utf-8"))
    return d['data']


@login_required
def dashboard(request):
    user = request.user
    courses = Course.objects.filter(user=user)
    return render(request, 'dashboard.html', {'user':user, 'courses':courses})