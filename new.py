import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from tkinter import ttk
from tkinter import Tk, Button, Label
import pygame
import os
from PIL import ImageTk, Image
import sys
import mutagen
import random
import math
import heapq

class Song:
    def __init__(self, name, composer, singer, movie, director, artist, lyricist):
        self.name = name
        self.composer = composer
        self.singer = singer
        self.movie = movie
        self.director = director
        self.artist = artist
        self.lyricist = lyricist
        self.path = None
        self.image = None
        self.next = None
        self.previous = None
        self.count=0

    def __lt__(self, other):
        # Compare two songs based on their count
        return self.count < other.count

class Playlist:
    def __init__(self):
        self.start = None
        self.last = None
        self.current_song = None
        self.paused = False
        self.volume = 0.5
        self.loaded_playlist = False
        self.loaded_filename = ""

    def addaudio(self, name, composer, singer, movie, director, artist, lyricist, path, image,count):
        newsong = Song(name, composer, singer, movie,
                       director, artist, lyricist)
        newsong.path = path
        newsong.image = image
        newsong.count = count
        self.addsong(newsong)
        if self.loaded_playlist:
            print("\n Song Added to the Playlist \n")
            self.save_playlist(self.loaded_filename)

    def addsong(self, song):
        if self.start is None:
            self.start = song
            self.start.previous = self.last = self.start
            self.start.next = self.last = self.start
        else:
            song.previous = self.last
            song.next = self.start
            self.last.next = song
            self.start.previous = song
            self.last = song

    def removesong(self, song):
        if self.start is None:
            return

        temp = self.start
        while temp.next != self.start:
            if temp.name == song:
                if temp == self.start:
                    self.start = temp.next
                temp.previous.next = temp.next
                temp.next.previous = temp.previous
                self.save_playlist(self.loaded_filename)  # Call save_playlist function after removing the song
                return
            temp = temp.next

        if temp.name == song:
            self.last = temp.previous
            temp.previous.next = temp.next
            temp.next.previous = temp.previous
            self.save_playlist(self.loaded_filename)  # Call save_playlist function after removing the song

    def removeall(self):
        self.start = None
        self.last = None
        self.current_song = None
        self.paused = False
        if self.loaded_playlist:
            print("\n Playlist Deleted \n")
            os.remove(self.loaded_filename)

    def showplaylist(self):
        if self.start is None:
            print("\nPlaylist is empty.\n")
        else:
            print("\nPLAYLIST:\n")
            temp = self.start
            while True:
                print("Name:", temp.name)
                print("Composer:", temp.composer)
                print("Singer:", temp.singer)
                print("Movie:", temp.movie)
                print("Director:", temp.director)
                print("Artist:", temp.artist)
                print("Lyricist:", temp.lyricist)
                print()
                temp = temp.next
                if temp == self.start:
                    break

    def search_song(self, song):
        if self.start is None:
            print("\nPlaylist is empty.\n")
        else:
            temp = self.start
            while True:
                if temp.name == song:
                    print("Song Found:")
                    print("Name:", temp.name)
                    print("Composer:", temp.composer)
                    print("Singer:", temp.singer)
                    print("Movie:", temp.movie)
                    print("Director:", temp.director)
                    print("Artist:", temp.artist)
                    print("Lyricist:", temp.lyricist)
                    print()
                    break
                temp = temp.next
                if temp == self.start:
                    print("\nSong not found in the playlist.\n")
                    break

    def skip_to_time(self, time):
        if self.current_song is None:
            print("\nNo song is currently playing.\n")
        else:
            pygame.mixer.music.set_pos(time)
            print("\nSkipped to time:", time, "\n")

    def get_total_duration(self):
        if self.start is None:
            print("\nPlaylist is empty.\n")
            return None

        total_duration = 0
        temp = self.start
        while True:
            metadata = mutagen.File(temp.path)
            if metadata is not None and metadata.info.length:
                total_duration += metadata.info.length
            temp = temp.next
            if temp == self.start:
                break

        total_minutes = math.floor(total_duration / 60)
        total_seconds = math.floor(total_duration % 60)
        print("\nTotal Duration: {} mins {} secs\n".format(
            total_minutes, total_seconds))
        return "{} mins {} secs".format(total_minutes, total_seconds)

    def select_song(self, song):
        if self.start is None:
            print("\nPlaylist is empty.\n")
        else:
            temp = self.start
            found_song = False
            while True:
                if temp.name == song:
                    found_song = True
                    break
                temp = temp.next
                if temp == self.start:
                    break

            if found_song:
                print("\nSelected Song:\n")
                self.current_song = temp
                self.play_song(temp.path)
                return self.current_song.image
            else:
                print("\nSong not found in the playlist.\n")

    def play_song(self, path):
        self.current_song.count+=1
        pygame.mixer.music.load(path)
        pygame.mixer.music.set_volume(self.volume)
        pygame.mixer.music.play()
        self.get_current_song_info()
        if self.loaded_playlist:
            self.save_playlist(self.loaded_filename)

    def get_current_song_info(self):
        if self.current_song is None or pygame.mixer.music.get_busy() == 0:
            print("\nNo song is currently playing.\n")
        else:
            print("\nCurrent Song:\n")
            print("Name:", self.current_song.name)
            file = pygame.mixer.music.get_busy()
            metadata = mutagen.File(self.current_song.path)
            duration = metadata.info.length if metadata else 0
            total_minutes = math.floor(duration / 60)
            total_seconds = math.floor(duration % 60)
            print("Duration: {} mins {} secs".format(
                total_minutes, total_seconds))
            print("Composer:", self.current_song.composer)
            print("Singer:", self.current_song.singer)
            print("Movie:", self.current_song.movie)
            print("Director:", self.current_song.director)
            print("Artist:", self.current_song.artist)
            print("Lyricist:", self.current_song.lyricist)
            print()
            total = "{} mins {} secs".format(total_minutes, total_seconds)
            return "{},{},{},{},{},{},{},{}".format(self.current_song.name, total, self.current_song.composer, self.current_song.singer, self.current_song.movie, self.current_song.director, self.current_song.artist, self.current_song.lyricist)
        
    def pause(self):
        if self.current_song is None and not self.paused:
            self.current_song = self.start
            self.play_song(self.current_song.path)
            return self.current_song.image
        else:
            if not self.paused:
                pygame.mixer.music.pause()
                self.paused = True
                print("\nSong paused.\n")
            else:
                pygame.mixer.music.unpause()
                self.paused = False
                print("\nSong resumed.\n")

    def set_volume(self, volume):
        if volume < 0 or volume > 1:
            print("\nVolume value should be between 0 and 1.\n")
        else:
            self.volume = volume
            if self.current_song is not None:
                pygame.mixer.music.set_volume(self.volume)
                print("\nVolume set to", volume, "\n")

    def playnext(self):
        if self.current_song is None:
            print("\nNo song is currently playing.\n")
        else:
            self.current_song = self.current_song.next
            self.play_song(self.current_song.path)
            return self.current_song.image

    def playprevious(self):
        if self.current_song is None:
            print("\nNo song is currently playing.\n")
        else:
            self.current_song = self.current_song.previous
            self.play_song(self.current_song.path)
            return self.current_song.image

    def playfirst(self):
        if self.start is None:
            print("\nPlaylist is empty.\n")
        else:
            self.current_song = self.start
            self.play_song(self.current_song.path)
            return self.current_song.image

    def playlast(self):
        if self.last is None:
            print("\nPlaylist is empty.\n")
        else:
            self.current_song = self.last
            self.play_song(self.current_song.path)
            return self.current_song.image

    def shuffle(self):
        if self.start is None:
            print("\nPlaylist is empty.\n")
        else:
            import random
            songs = []
            temp = self.start
            while True:
                songs.append(temp)
                temp = temp.next
                if temp == self.start:
                    break
            random.shuffle(songs)
            self.start = songs[0]
            self.last = songs[-1]
            for i in range(len(songs)):
                songs[i].next = songs[(i + 1) % len(songs)]
                songs[i].previous = songs[i - 1]
            print("\nPlaylist shuffled.\n")

    def sortsong(self):
        if self.start is None:
            print("\nPlaylist is empty.\n")
        else:
            sorted_playlist = []
            temp = self.start
            while True:
                sorted_playlist.append(temp.name)
                temp = temp.next
                if temp == self.start:
                    break
            sorted_playlist.sort()
            print(sorted_playlist)
            print("\nSorted Playlist:")
            for song in sorted_playlist:
                print(song)
            print()
            return sorted_playlist
        
    def repeat(self):
        if self.current_song is None:
            print("\nNo song is currently playing.\n")
        else:
            # Set the value to -1 to repeat the current song indefinitely
            pygame.mixer.music.play(-1)

    def loop_playlist(self):
        if self.start is None:
            print("\nPlaylist is empty.\n")
        else:
            self.last.next = self.start
            self.start.previous = self.last
            self.current_song = self.start

    def save_playlist(self, filename):
        print(filename)
        if self.start is None:
            print("\nPlaylist is empty.\n")
        else:
            with open(filename, "w") as file:
                temp = self.start
                while True:
                    print(temp.name)
                    file.write(temp.name + "\n")
                    file.write(temp.composer + "\n")
                    file.write(temp.singer + "\n")
                    file.write(temp.movie + "\n")
                    file.write(temp.director + "\n")
                    file.write(temp.artist + "\n")
                    file.write(temp.lyricist + "\n")
                    file.write(temp.path + "\n")
                    file.write(temp.image + "\n")
                    file.write(str(temp.count)+ "\n")
                    if temp.name=="jimikki ponnu":
                        print("check",temp.count)
                    temp = temp.next
                    if temp == self.start:
                        break
            print("\nPlaylist saved to", filename, "\n")

    def load_playlist(self, filename):
        try:
            with open(filename, "r") as file:
                lines = file.readlines()
                print(len(lines))
                for i in range(0, len(lines), 10):
                    name = lines[i].strip()
                    composer = lines[i + 1].strip()
                    singer = lines[i + 2].strip()
                    movie = lines[i + 3].strip()
                    director = lines[i + 4].strip()
                    artist = lines[i + 5].strip()
                    lyricist = lines[i + 6].strip()
                    path = lines[i + 7].strip()
                    image = lines[i + 8].strip()
                    count=lines[i + 9].strip()
                    song = Song(name, composer, singer, movie,
                                director, artist, lyricist)
                    song.path = path
                    song.image = image
                    song.count=int(count)
                    self.addsong(song)
            self.loaded_playlist = True
            self.loaded_filename = filename
            print("\nPlaylist loaded from", filename, "\n")
            self.current_song = self.start
            self.play_song(self.current_song.path)
            return self.current_song.image
        except FileNotFoundError:
            print("\nFile", filename, "not found.\n")

    def create_max_heap(self):
        if self.start is None:
            print("\nPlaylist is empty.\n")
        else:
            songs = []
            temp = self.start
            while True:
                songs.append(temp)
                temp = temp.next
                if temp == self.start:
                    break
            heapq.heapify(songs)
            top_song = max(songs, key=lambda x: x.count)
            print("\nTop Song (based on count):")
            print("Name:", top_song.name)
            print("Count:", top_song.count)
            return "{},{}".format(top_song.name, top_song.count)



class PlaylistGUI:
    def __init__(self):
        self.playlist = Playlist()
        self.current_song_label = None
        pygame.init()
        self.remove=1
        self.window = tk.Tk()
        self.most_played_song_label = None
       
        
        self.frame2 = tk.Frame(self.window,width=200, height=200, bg='WHITE')
        self.frame2.pack(side=tk.LEFT, padx=(340, 0), pady=20)

        self.frame = tk.Frame(self.window,width=200, height=200, bg='WHITE')
        self.frame.pack(side=tk.LEFT, padx=(10, 0), pady=20)

        self.frame1 = tk.Frame(self.window,width=500, height=200,highlightthickness=0)
        self.frame1.pack(side=tk.LEFT, padx=(10, 5), pady=0)

        style = ttk.Style()
        style.configure("Custom.TButton", font=("Open Sans", 15),width=15 )

        style = ttk.Style()
        style.configure("Custom1.TButton", font=("Open Sans", 20),width=8 )

        self.window.title("Playlist GUI")
        self.window.state('zoomed')  
        self.update_background_color()
        font = ("Open Sans", 15)
        self.label = tk.Label(self.frame, text="MUSIC PLAYER",width=20,font=font)
        self.label.pack()

        #frame2

        self.play_first_button = ttk.Button(
            self.frame2, text="Play first", command=self.play_first,style="Custom.TButton")
        self.play_first_button.pack()

        self.play_last_button = ttk.Button(
            self.frame2, text="Play Last", command=self.play_last,style="Custom.TButton")
        self.play_last_button.pack()
        
        self.remove_all_button = ttk.Button(
            self.frame2, text="Remove All Songs", command=self.remove_all_songs,style="Custom.TButton")
        self.remove_all_button.pack()
        
        self.add_button = ttk.Button(
            self.frame2, text="Add Music", command=self.add_music,style="Custom.TButton")
        self.add_button.pack()

        self.display_total_playlist_time_button = ttk.Button(
            self.frame2, text="Total Playlist Time", command=self.display_total_playlist_time,style="Custom.TButton")
        self.display_total_playlist_time_button.pack()
        

        self.load_button = ttk.Button(
            self.frame2, text="Load Playlist", command=self.load_playlist,style="Custom.TButton")
        self.load_button.pack(pady=5)
        self.load_entry = tk.Entry(self.frame2,font=("Arial", 12))
        self.load_entry.pack(pady=5)

        self.select_song_button = ttk.Button(
            self.frame2, text="Select Song", command=self.select_song,style="Custom.TButton")
        self.select_song_button.pack(pady= 5)
        self.select_entry = tk.Entry(self.frame2,font=("Arial", 12))
        self.select_entry.pack(pady= 5)

       
        self.save_button = ttk.Button(
            self.frame2, text="Save Playlist", command=self.save_playlist,style="Custom.TButton")
        self.save_button.pack(pady= 5)
        self.save_entry = tk.Entry(self.frame2,font=("Arial", 12))
        self.save_entry.pack(pady= 5)

        self.remove_button = ttk.Button(
            self.frame2, text="Remove Music", command=self.remove_music,style="Custom.TButton")
        self.remove_button.pack(pady= 5)
        self.remove_entry = tk.Entry(self.frame2,font=("Arial", 12))
        self.remove_entry.pack(pady= 5)

        self.set_volume_button = ttk.Button(
            self.frame2, text="Set Volume", command=self.set_volume,style="Custom.TButton")
        self.set_volume_button.pack(pady= 5)
        self.volume_entry = tk.Entry(self.frame2,font=("Arial", 12))
        self.volume_entry.pack(pady= 5)

        self.skip_duration_button = ttk.Button(
            self.frame2, text="Skip Duration", command=self.skip_duration,style="Custom.TButton")
        self.skip_duration_button.pack(pady= 5)
        self.duration_entry = tk.Entry(self.frame2,font=("Arial", 12))
        self.duration_entry.pack(pady= 5)
        
        self.show_button = ttk.Button(
            self.frame2, text="Show Playlist", command=self.show_playlist,style="Custom.TButton")
        self.show_button.pack()

        self.sort_playlist_button = ttk.Button(
            self.frame2, text="Sort Playlist", command=self.sort_playlist,style="Custom.TButton")
        self.sort_playlist_button.pack()

        self.shuffle_playlist_button = ttk.Button(
            self.frame2, text="Shuffle Playlist", command=self.shuffle_playlist,style="Custom.TButton")
        self.shuffle_playlist_button.pack()

        self.loop_playlist_button = ttk.Button(
            self.frame2, text="Loop Playlist", command=self.loop_playlist,style="Custom.TButton")
        self.loop_playlist_button.pack()

        self.most_played_button = ttk.Button(
            self.frame1, text="Most Played", command=self.most_played,style="Custom.TButton")
        self.most_played_button.pack()
        
        #frame2


        self.image = Image.open(
            r"C:\Users\MADHAV\OneDrive\Desktop\DSA project\d.png")
        self.image = self.image.resize((500, 600))
        self.photo = ImageTk.PhotoImage(self.image)
        self.image_label = tk.Label(self.frame, image=self.photo)
        self.image_label.pack()

        # Create a label for song details
        self.song_details_label = tk.Label(
            self.frame1, text="", font=("Helvetica", 14), wraplength=300)
        self.song_details_label.pack()
       

        # Create buttons
        #frame
        self.play_previous_button = ttk.Button(
            self.frame, text="|◁", command=self.play_previous,style="Custom1.TButton")
        self.play_previous_button.pack(side="left",fill=tk.BOTH, expand=True, padx=1)

        self.pause_resume_button = ttk.Button(
            self.frame, text="▶", command=self.pause_resume,style="Custom1.TButton")
        self.pause_resume_button.pack(side="left",fill=tk.BOTH, expand=True, padx=1)

        self.play_next_button = ttk.Button(
            self.frame, text="▷|", command=self.play_next,style="Custom1.TButton")
        self.play_next_button.pack(side="left",fill=tk.BOTH, expand=True, padx=1)

        self.repeat_current_song_button = ttk.Button(
            self.frame, text="🔁", command=self.repeat_current_song,style="Custom1.TButton")
        self.repeat_current_song_button.pack(side="top",fill=tk.BOTH, expand=True, padx=1)
        #frame
        
        # Create more buttons for other functions

    def update_song_details_label(self):
        if self.remove==1:
            """Updates the song details label with the current song details"""
            if self.current_song_label:
                self.current_song_label.config(
                    font=("Bodoni", 14), fg="white", bg="black",width="15")

            if self.playlist.current_song:
                song_info = self.playlist.get_current_song_info()

                details = song_info.split(",")
                details_text = ""

                text = ["Name", "Duration", "Composer", "Singer",
                        "Movie", "Director", "Artists", "Lyricist"]

                for i, label in enumerate(text):
                    if i < len(details):
                        value = details[i]
                        label_text = f"{label}: {value}\n\n"
                        details_text += label_text

                if self.current_song_label:
                    self.current_song_label.destroy()

                self.current_song_label = tk.Label(
                    self.frame1, text=details_text, font=("Comic Sans MS", 14, "bold"), fg="white", bg="black")
                self.current_song_label.pack()  # Change the font to "Comic Sans MS"
                #self.current_song_label.grid(
                    #row=1, column=1, padx=20, pady=10, sticky="w")

                # Configure grid row and column to expand dynamically
                self.window.grid_rowconfigure(1, weight=1)
                self.window.grid_columnconfigure(1, weight=1)
        else:
            if self.current_song_label:
                self.current_song_label.config(
                    font=("Bodoni", 14), fg="white", bg="white",width="25")

            if self.playlist.current_song:
                song_info = " "

                details = song_info.split(",")
                details_text = " "

                text = [" "]

                for i, label in enumerate(text):
                    if i < len(details):
                        value = details[i]
                        label_text = f"{label}: {value}\n\n"
                        details_text += label_text

                if self.current_song_label:
                    self.current_song_label.destroy()

                self.current_song_label = tk.Label(
                    self.frame1, text=details_text, font=("Comic Sans MS", 14, "bold"), fg="white", bg="white")
                self.current_song_label.pack()  # Change the font to "Comic Sans MS"
                #self.current_song_label.grid(
                    #row=1, column=1, padx=20, pady=10, sticky="w")

                # Configure grid row and column to expand dynamically
                self.window.grid_rowconfigure(1, weight=1)
                self.window.grid_columnconfigure(1, weight=1)
            self.remove=1

    def most_played_song_details(self):
            if self.most_played_song_label:
                self.most_played_song_label.config(
                    font=("Bodoni", 14), fg="white", bg="black",width="15")

            if self.playlist.current_song:
                song_info = self.playlist.create_max_heap()

                details = song_info.split(",")
                details_text = ""

                text = ["Name", "Count"]

                for i, label in enumerate(text):
                    if i < len(details):
                        value = details[i]
                        label_text = f"{label}: {value}\n\n"
                        details_text += label_text

                if self.most_played_song_label:
                    self.most_played_song_label.destroy()

                self.most_played_song_label = tk.Label(
                    self.frame1, text=details_text, font=("Comic Sans MS", 14, "bold"), fg="white", bg="black")
                self.most_played_song_label.pack()  # Change the font to "Comic Sans MS"
                #self.current_song_label.grid(
                    #row=1, column=1, padx=20, pady=10, sticky="w")

                # Configure grid row and column to expand dynamically
                self.window.grid_rowconfigure(0, weight=1)
                self.window.grid_columnconfigure(1, weight=1)

    def update_background_color(self):
        # Generate random gradient colors
        num_combinations = random.randint(10, 20)
        gradient_colors = []

        for _ in range(num_combinations):
            # Randomly select if dark or light color should be used first
            is_dark = random.choice([True, False])
            start_color = self.generate_color(is_dark)
            end_color = self.generate_color(not is_dark)

            # Calculate intermediate colors for gradient effect
            num_intermediates = 50
            colors = [
                self.interpolate_color(
                    start_color, end_color, j / num_intermediates)
                for j in range(num_intermediates + 1)
            ]
            gradient_colors.extend(colors)

        # Update the background color of the window
        self.window.configure(background=gradient_colors[0])

        # Update the background color periodically
        delay = 50  # Delay in milliseconds for smoother transition
        color_index = 0
        num_colors = len(gradient_colors)

        def update_color():
            nonlocal color_index
            self.window.configure(background=gradient_colors[color_index])
            color_index = (color_index + 1) % num_colors
            self.window.after(delay, update_color)

        self.window.after(delay, update_color)

    def generate_color(self, is_dark):
        # Generate a random color based on whether it should be dark or light
        if is_dark:
            color_range = (0, 0)
        else:
            color_range = (65,125)

        return "#{:02x}{:02x}{:02x}".format(
            random.randint(*color_range),
            random.randint(*color_range),
            random.randint(*color_range)
        )

    def interpolate_color(self, start_color, end_color, ratio):
        # Interpolate between start and end colors based on a ratio
        start_rgb = self.hex_to_rgb(start_color)
        end_rgb = self.hex_to_rgb(end_color)

        interpolated_rgb = [
            int(start + (end - start) * ratio)
            for start, end in zip(start_rgb, end_rgb)
        ]

        return "#{:02x}{:02x}{:02x}".format(*interpolated_rgb)

    @staticmethod
    def hex_to_rgb(color_hex):
        # Convert color from hex format to RGB format
        return [
            int(color_hex[i:i + 2], 16)
            for i in (1, 3, 5)
        ]

    def add_music(self):
        name = input("Enter name of the song: ")
        composer = input("Enter name of the composer: ")
        singer = input("Enter name of the singer: ")
        movie = input("Enter movie name: ")
        director = input("Enter name of the director: ")
        artist = input("Enter name of the artist: ")
        lyricist = input("Enter name of the lyricist: ")
        path = input("Enter path of the song: ")
        image = input("Enter path of the image: ")
        self.playlist.addaudio(name, composer, singer, movie,
                               director, artist, lyricist, path, image)

    def display(self, show):
        self.image = Image.open(show)
        self.image = self.image.resize((490, 600))
        self.photo = ImageTk.PhotoImage(self.image)
        self.label1= tk.Label(self.window, image=self.photo)
        self.label1.place(x=550, y=90)
        self.image_label.pack()

    def remove_music(self):
        self.playlist.pause()
        song_name = self.remove_entry.get()
        self.playlist.removesong(song_name)
        show=r"C:\Users\MADHAV\OneDrive\Desktop\DSA project\d.png"
        self.display(show)
        self.song_details_label.config(text="")
        self.remove=0
        self.update_song_details_label()

    def remove_all_songs(self):
        self.playlist.pause()
        self.playlist.removeall()
        show=r"C:\Users\MADHAV\OneDrive\Desktop\DSA project\d.png"
        self.display(show)
        self.song_details_label.config(text="")
        self.remove=0
        self.update_song_details_label()

    def show_playlist(self):
        if self.playlist.start is None:
            self.song_details_label.config(text="\nPlaylist is empty.\n")
        else:
            playlist_text = "\nPLAYLIST:\n"
            temp = self.playlist.start
            while True:
                playlist_text += "Name: {}\n".format(temp.name)
                temp = temp.next
                if temp == self.playlist.start:
                    break
            self.song_details_label.config(text=playlist_text)

    def search_song(self):
        song_name = self.search_entry.get()
        self.playlist.search_song(song_name)

    def play_next(self):
        show = self.playlist.playnext()
        self.display(show)
        self.update_song_details_label()

    def play_previous(self):
        show = self.playlist.playprevious()
        self.display(show)
        self.update_song_details_label()

    def play_first(self):
        show = self.playlist.playfirst()
        self.display(show)
        self.update_song_details_label()

    def play_last(self):
        show = self.playlist.playlast()
        self.display(show)
        self.update_song_details_label()

    def select_song(self):
        song_name = self.select_entry.get()
        show = self.playlist.select_song(song_name)
        self.display(show)
        self.update_song_details_label()

    def sort_playlist(self):
        list = self.playlist.sortsong()
        if not list:
            self.song_details_label.config(text="\nPlaylist is empty.\n")
        else:
            playlist_text = "\nSORTED PLAYLIST:\n"
            for songs in list:
                playlist_text += "Name: {}\n".format(songs)
            self.song_details_label.config(text=playlist_text)

    def shuffle_playlist(self):
        self.playlist.shuffle()

    def pause_resume(self):
        show = self.playlist.pause()
        if show:
            self.display(show)
            self.update_song_details_label()

    def set_volume(self):
        volume = self.volume_entry.get()
        self.playlist.set_volume(float(volume))

    def repeat_current_song(self):
        self.playlist.repeat()

    def skip_duration(self):
        duration = self.duration_entry.get()
        self.playlist.skip_to_time(int(duration))

    def display_total_playlist_time(self):
        total = ""
        total = self.playlist.get_total_duration()
        if total == 0:
            self.song_details_label.config(text="\nPlaylist is empty.\n")
        else:
            playlist_text = "\nTOTAL PLAYLIST DURATION TIME:\n"
            self.song_details_label.config(text=playlist_text+total)

    def loop_playlist(self):
        self.playlist.loop_playlist()

    def most_played(self):
        self.most_played_song_details()

    def save_playlist(self):
        filename = self.save_entry.get()
        self.playlist.save_playlist(filename)

    def load_playlist(self):
        filename = self.load_entry.get()
        show = self.playlist.load_playlist(filename)
        if show:
            self.display(show)
            self.update_song_details_label()
            self.playlist.pause()

    def run(self):
        self.window.mainloop()


if __name__ == "__main__":
    playlist_gui = PlaylistGUI()
    playlist_gui.run()
    playlist_gui.window.mainloop()
    pygame.quit()