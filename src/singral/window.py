# window.py
#
# Copyright 2020 Aurnytoraink
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from gi.repository import Gtk, Handy, GObject, GLib, Gdk

from singral.player import Player
from singral.api.session import Session
from singral.help_task import TaskHelper
from singral.art_album import AlbumWidget
from singral.art_track import TrackListBox, TrackRow
from singral.help_artwork import get_cover_from_album

@Gtk.Template(resource_path='/com/github/Aurnytoraink/Singral/ui/window.ui')
class SingralWindow(Handy.ApplicationWindow):
    __gtype_name__ = 'SingralWindow'

    main_stack = Gtk.Template.Child()
    app_stack = Gtk.Template.Child()
    deck_app = Gtk.Template.Child()
    header_switch = Gtk.Template.Child()
    switchbar_bottom = Gtk.Template.Child()

    #Login Page
    log_username = Gtk.Template.Child()
    log_password = Gtk.Template.Child()
    log_button = Gtk.Template.Child()
    log_error_reveal = Gtk.Template.Child()
    log_error_label = Gtk.Template.Child()
    log_button_stack = Gtk.Template.Child()
    create_account_btn = Gtk.Template.Child()
    forget_pwd_btn = Gtk.Template.Child()

    #Home Page
    welcome_label = Gtk.Template.Child()

    #Album Page
    albums_flowbox = Gtk.Template.Child()

    #Songs Page
    songs_viewport = Gtk.Template.Child()

    #Search Page
    search_stack = Gtk.Template.Child()
    popup_searchbar = Gtk.Template.Child()
    popup_searchbar_entry = Gtk.Template.Child()
    topsearch_box = Gtk.Template.Child()
    topsearch_result = Gtk.Template.Child()
    album_flowbox = Gtk.Template.Child()
    album_box = Gtk.Template.Child()
    artist_flowbox = Gtk.Template.Child()
    artist_box = Gtk.Template.Child()
    track_box = Gtk.Template.Child()
    track_flowbox = Gtk.Template.Child()
    playlist_flowbox = Gtk.Template.Child()
    playlist_box = Gtk.Template.Child()

    #Player UI
    duration_scale = Gtk.Template.Child()
    enlarge_player_button = Gtk.Template.Child()
    player_actual_duration = Gtk.Template.Child()
    player_total_duration = Gtk.Template.Child()
    player_duration_scale = Gtk.Template.Child()
    player_play_button = Gtk.Template.Child()
    player_play_image = Gtk.Template.Child()
    player_prev_button = Gtk.Template.Child()
    player_next_button = Gtk.Template.Child()
    player_cover = Gtk.Template.Child()
    player_title = Gtk.Template.Child()
    player_artist = Gtk.Template.Child()
    player_timebar = Gtk.Template.Child()
    player_reveal = Gtk.Template.Child()
    player_songinfo = Gtk.Template.Child()

    #Enlarge player UI
    playerE_actual_duration = Gtk.Template.Child()
    playerE_total_duration = Gtk.Template.Child()
    playerE_duration_scale = Gtk.Template.Child()
    close_player_button = Gtk.Template.Child()
    playerE_play_button = Gtk.Template.Child()
    playerE_play_image = Gtk.Template.Child()
    playerE_prev_button = Gtk.Template.Child()
    playerE_next_button = Gtk.Template.Child()
    playerE_cover = Gtk.Template.Child()
    playerE_title = Gtk.Template.Child()
    playerE_artist = Gtk.Template.Child()
    playerE_shuffle_button = Gtk.Template.Child()
    shuffle_state_img = Gtk.Template.Child()
    playerE_repeat_button = Gtk.Template.Child()
    repeat_state_img = Gtk.Template.Child()
    like_button_img = Gtk.Template.Child()
    like_button = Gtk.Template.Child()

    # TEST ONLY
    test_button = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.connect("check-resize",self.update_scale_interface)
        self.enlarge_player_button.connect("clicked",self.display_player)
        self.close_player_button.connect("clicked",self.display_player)
        self.switchbar_bottom.connect("button-release-event",self.get_page)
        self.header_switch.connect("button-release-event",self.get_page)

        self.log_button.connect("clicked",self.login_username)
        self.log_username.connect("changed",self.update_login_page)
        self.log_password.connect("changed",self.update_login_page)
        self.create_account_btn.connect("clicked",self.create_account)
        self.forget_pwd_btn.connect("clicked",self.forget_pwd)

        # TEST ONLY
        self.test_button.connect("clicked",self.logoff)

        #Init API
        self.session = Session()

        # Init player
        self.player = Player(self,self.session)

        # Init interface
        self.songs_listbox = TrackListBox(self.player)
        self.songs_viewport.add(self.songs_listbox)

    def update_scale_interface(self, *_):
        if self.header_switch.get_title_visible():
            self.switchbar_bottom.set_reveal(True)
            self.player_timebar.set_visible(False)
            self.player_songinfo.set_hexpand(True)
        else:
            self.switchbar_bottom.set_reveal(False)
            self.player_timebar.set_visible(True)
            self.player_songinfo.set_hexpand(False)

    def display_player(self, *_):
        if self.deck_app.get_visible_child_name() == "app_page":
            self.deck_app.set_visible_child_name("player_page")
        elif self.deck_app.get_visible_child_name() == "player_page":
            self.deck_app.set_visible_child_name("app_page")

    def login_username(self,*_):
        self.log_error_reveal.set_reveal_child(False)
        self.log_button.set_sensitive(False)
        self.log_button_stack.set_visible_child_name("try")
        TaskHelper().run(self.session.login,self.log_username.get_text(), self.log_password.get_text(),callback=(self.on_login,))

    def on_login(self,*args):
        def on_login_sucess():
            self.welcome_label.set_text(f"Welcome, {self.session.username}")
            self.main_stack.set_visible_child_name("app_page")
            self.log_username.set_text("")
            self.log_password.set_text("")
            self.log_button.set_sensitive(True)
            self.log_button_stack.set_visible_child_name("icon")

        def on_login_unsucess(error,show):
            self.log_button.set_sensitive(True)
            self.log_button_stack.set_visible_child_name("icon")
            self.log_error_label.set_text(error)
            self.forget_pwd_btn.set_visible(show)
            self.log_error_reveal.set_reveal_child(True)

        if args[0]:
            on_login_sucess()
        else:
            if args[0][1]:
                on_login_unsucess("Wrong email/password",True)
            else:
                on_login_unsucess("A internal error occured",False)

    def update_login_page(self,*_):
        self.log_error_reveal.set_reveal_child(False)

    def logoff(self,*_):
        self.session.logoff()
        self.main_stack.set_visible_child_name("login_page")

    def create_account(self,*_):
        Gtk.show_uri_on_window(self,"https://www.qobuz.com",Gdk.CURRENT_TIME)

    def forget_pwd(self,*_):
        Gtk.show_uri_on_window(self,"https://www.qobuz.com/reset-password",Gdk.CURRENT_TIME)


    # Interface
    
    def clear_all(self,*args):
        for child in self.albums_flowbox.get_children(): child.destroy()
        for child in self.songs_listbox.get_children(): child.destroy()
        self.songs_listbox.queue = []

    def get_page(self,switcher,*arg):
        page = switcher.get_stack().get_visible_child_name()
        if page == "album_page":
            self.get_albums()
        elif page == "artist_page":
            pass
        elif page == "song_page":
            self.get_songs()
        elif page == "playlist_page":
            pass


    # Albums
    def get_albums(self,*args):
        TaskHelper().run(self.session.get_userfav_albums,callback=(self.display_albums,))
    
    def display_albums(self,albums):
        self.clear_all()
        for album in albums:
            row = AlbumWidget(album)
            self.albums_flowbox.add(row)
            TaskHelper().run(get_cover_from_album,row.album,self.session,callback=(row.display_cover,))

    # Songs
    def get_songs(self,*args):
        TaskHelper().run(self.session.get_userfav_tracks,callback=(self.display_songs,))
    
    def display_songs(self,songs):
        self.clear_all()
        self.songs_listbox.queue = songs
        for song in songs:
            row = TrackRow(song)
            self.songs_listbox.add(row)
            TaskHelper().run(get_cover_from_album,row.track,self.session,callback=(row.display_cover,))