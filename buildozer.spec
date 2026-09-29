[app]

title = Yemen4G
package.name = yemen4g
package.domain = org.yemen4g

source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,atlas

version = 1.0

requirements = python3,kivy,requests,beautifulsoup4,pillow

orientation = portrait
fullscreen = 0

android.permissions = INTERNET

android.api = 35
android.minapi = 24
android.archs = arm64-v8a

android.accept_sdk_license = True
android.skip_update = False

android.debug_artifact = apk


[buildozer]

log_level = 2
warn_on_root = 1
