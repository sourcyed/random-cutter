import cv2
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.audio.io.AudioFileClip import AudioFileClip
from sys import stdout
from os import remove
from random import randint
from math import ceil

class Random_Cutter():
    def __init__(self,vid_path, mus_path, save_path, vid_length, cut_length): #Sets the class variables.
        self.vid_path = vid_path
        self.mus_path = mus_path
        self.save_path = save_path

        self.cap = cv2.VideoCapture(self.vid_path)
        self.cap.set(cv2.CAP_PROP_POS_AVI_RATIO,1)

        self.length = int(self.cap.get(cv2.CAP_PROP_POS_FRAMES))
        self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.fps = int(self.cap.get(cv2.CAP_PROP_FPS))

        self.vid_length = ceil(vid_length * self.fps)
        self.cut_length = ceil(cut_length * self.fps)

        self.repeatable = False #Defines rather or not the frames on the video can be repeated.
        if self.vid_length > self.length:
            self.repeatable = True
        
        self.cap.set(cv2.CAP_PROP_POS_AVI_RATIO,0)

        self.writer = cv2.VideoWriter("".join(self.save_path.split(".")[:-1]) + "_tmp.avi",cv2.VideoWriter_fourcc(*'XVID'),self.fps,(self.width,self.height))

        self.run_operations()

    def run_operations(self): #Executes primary methods.
        self.read_frames()
        self.add_music()
        remove("".join(self.save_path.split(".")[:-1]) + "_tmp.avi")

    def read_frames(self): #Reads the frames in the source video.
        self.last_progress = 0

        used_frames = list()

        for i in range(ceil(self.vid_length / self.cut_length)):
            cut_location = randint(0,self.length - self.cut_length)

            if self.repeatable:
                cut_location = randint(0,self.length - self.cut_length)

            else:
                y = 0
                while any(x in used_frames for x in list(range(cut_location-self.fps, cut_location + self.cut_length+self.fps+1))) and y < 5:
                    cut_location = randint(0,self.length - self.cut_length)
                    y+=1
            
            used_frames.extend(list(range(cut_location, cut_location + self.cut_length+1)))
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, cut_location)
            
            for x in range(self.cut_length):
                self.write_frame(i,x) 
                self.update_progress(i,x)
                self.display_progress()
        
        self.cap.release()
        self.writer.release()

    def write_frame(self,i,x): #Writes the read frame to the temporary output file.
        ret,self.frame = self.cap.read()
        self.writer.write(self.frame)

    def update_progress(self,i,x): #Updates the progress.
        self.progress = ceil((i*self.cut_length+x) / (self.vid_length) * 100)

    def display_progress(self): #Displays the progress.
        if  self.progress > self.last_progress:
            self.last_progress = self.progress
            stdout.write("\r%d%%" % self.progress)
            stdout.flush()

    def add_music(self): #Creates a new video file from the temporary output file and adds the selected audio the the background.
        my_clip = VideoFileClip("".join(self.save_path.split(".")[:-1]) + "_tmp.avi")
        music = AudioFileClip(self.mus_path)
        if my_clip.duration > music.duration:
            duration = music.duration
        else:
            duration = my_clip.duration
        my_clip = my_clip.set_audio(music.set_duration(duration))
        my_clip.write_videofile(self.save_path, fps=self.fps)