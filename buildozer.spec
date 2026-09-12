[app]

title = Jarvis AI
package.name = jarvis
package.domain = org.jarvis

source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,json

version = 1.0

requirements = python3,kivy,requests

orientation = portrait

fullscreen = 0

android.permissions = INTERNET,RECORD_AUDIO

android.api = 35
android.minapi = 23

android.archs = arm64-v8a,armeabi-v7a

[buildozer]

log_level = 2

warn_on_root = 1
