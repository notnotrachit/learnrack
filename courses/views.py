from django.shortcuts import render, redirect
from django.http import HttpResponse
from courses.models import Course
from googleapiclient.discovery import build
from django.contrib.auth.decorators import login_required
import os
from dotenv import load_dotenv
load_dotenv()

youtube = build('youtube', 'v3', developerKey=os.environ.get('YOUTUBE_API_KEY'))
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


#@login_required
def new_course_page(request):
    return render(request, 'new_course.html')

@login_required
def new_course(request):
    user=request.user
    if request.method=='POST':
        url=request.POST['url']
        tag=request.POST['tag']
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
        return HttpResponse('success')
    else:
        return redirect('home')


@login_required
def course_detail(request, course_id):
    course=Course.objects.get(id=course_id)
    if request.user==course.user:
        
        
        
        if video_id in course.video_ids:
            index=course.video_ids.index(video_id)
            if index==0:
                return redirect('home')
            else:
                previous_video_id=course.video_ids[index-1]
                return redirect('video_page', course_id=course_id, video_id=previous_video_id)
        if video_id in course.video_ids:
            index=course.video_ids.index(video_id)
            if index==len(course.video_ids)-1:
                return redirect('home')
            else:
                next_video_id=course.video_ids[index+1]
                return redirect('video_page', course_id=course_id, video_id=next_video_id)
        if course.watched_videos:
            last_watched_video=course.watched_videos[-1]
            return redirect('video_page', course_id=course_id, video_id=last_watched_video)
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
def video_watch(request, course_id):
    course=Course.objects.get(id=course_id)
    if request.method=='POST':
        video_id=request.POST['video_id']
        if video_id not in course.watched_videos:
            course.watched_videos.append(video_id)
            course.save()
        return HttpResponse('success')
    else:
        return redirect('home')

@login_required
def video_page(request, course_id, video_id):
    course=Course.objects.get(id=course_id)
    if video_id in course.video_ids:
        return render(request, 'video_detail.html', {'course':course, 'video_id':video_id})
    else:
        return redirect('home')

@login_required
def notes_update(request,course_id):
    course=Course.objects.get(id=course_id)
    if request.method=='POST':
        notes=request.POST['notes']
        course.notes=notes
        course.save()
        return HttpResponse('success')
    else:
        return redirect('home')
