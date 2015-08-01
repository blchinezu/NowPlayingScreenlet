# NowPlayingScreenlet
### An improved version of the NowPlaying Screenlet

New Features Summary:
 + General:   Easy translations through launchpad
 + General:   Wallpaper changer (Sets wallpaper according to the current artist or album) (requires gconftool-2)
 + General:   Cover Copy (Copies the current cover to the song folder) (requires imagemagick)
 + General:   History logging of the played tracks
 + General:   Right click menu: 'Open cover with viewer' and 'Open cover location'
 + General:   Sleep fade (Fade out volume, Quit player and Shutdown computer)
 + Skinning:  Ability to edit the cover image right before showing it (so you can make more flexible skins)
 + Skinning:  Rewritten the PlayerControls tag. (now supports transparency and don't have to be an actual visual group)
 + Skinning:  Added the transparency option for images
 + Eyecandy:  Fade effect for the following actions: screenlet startup, cover change, theme change, mouse hover, player start/quit, player play/stop, manual show/hide
 + API:       Volume control (with mouse scroll wheel up/down/click)
 + API:       Rating control
 + API:       Updated/Improved most of them and added some more

Note for the Screenlets engine developers:
 - The fade effect should be implemented directly into the screenlets engine so that all the screenlets can use it. I do belive that it would look way better.

Supported players:
 - last tested with v0.3.4.2 - Abraca                (XMMS2 GUI)
 - last tested with v0.3.4.2 - Amarok 1
 - last tested with v0.3.3.9 - Amarok 2
 - last tested with v0.3.4.2 - Audacious
 - last tested with v0.3.4.2 - Banshee
 - last tested with v0.3.4.2 - Decibel-Audio-Player  (v1.05 or greater)
 - last tested with v0.3.4.2 - Esperanza             (XMMS2 GUI)
 - last tested with v0.3.4.2 - Exaile                (with MPRIS Plugin enabled)
 - last tested with v0.3.4.2 - gXMMS2                (XMMS2 GUI)
 - last tested with v0.3.4.2 - Jajuk
 - last tested with v0.3.4.2 - Juk
 - last tested with v0.3.4.2 - Listen
 - last tested with v0.3.4.2 - LXMusic               (XMMS2 GUI)
 - last tested with v0.3.3.0 - MPD
 - last tested with v0.3.4.2 - Muine
 - last tested with v0.3.4.2 - qmmp                  (with MPRIS Plugin enabled)
 - last tested with v0.3.4.2 - QuodLibet             (with Picture Saver plugin enabled)
 - last tested with v0.3.4.2 - Rhythmbox
 - last tested with v0.3.4.2 - Songbird              (needs MPRIS Addon)
 - last tested with v0.3.4.2 - XMMS2                 (with/without GUI.. doesn't matter)
                             - Maybe other players with MPRIS support
                             - Definitely other XMMS2 clients
 
Included skins:
 - Border_Fade-200px
 - Border_Fade-400px
 - Broken_Glass
 - corner_tr_b
 - corner_tr_b_only_cover
 - Coversutra-Searchbar-Album-Art
 - Coversutra-Searchbar-Jewel-Case
 - Coversutra-Searchbar-Vinyl-Art
 - default
 - default-old
 - lucid-dark
 - lucid-light

 
Known Bugs:
 - Listen:   Next/Previous buttons don't work (The dbus call is correct but from that to the player something is not working fine.)
 - Songbird: It works but the screenlet lags a lot. Although it uses MPRIS just like Exaile or qmmp which run fine.

For more details please read the [changelog](https://github.com/blchinezu/NowPlayingScreenlet/blob/master/ChangeLog)...

Available at gnome-look.org:
 - http://gnome-look.org/content/show.php?content=136480

Screenshots:

![./screenshots/136480-1.png](https://raw.githubusercontent.com/blchinezu/NowPlayingScreenlet/master/screenshots/136480-1.png)
![./screenshots/136480-3.png](https://raw.githubusercontent.com/blchinezu/NowPlayingScreenlet/master/screenshots/136480-3.png)
![./screenshots/136480-2.jpg](https://raw.githubusercontent.com/blchinezu/NowPlayingScreenlet/master/screenshots/136480-2.jpg)

You can donate through PayPal at [brucelee.duckdns.org/donation/NowPlayingScreenlet](http://brucelee.duckdns.org/donation/NowPlayingScreenlet)

    Since I can't directly add the PayPal donation button here, I've created a simple page
    which has the Donate button.
    
