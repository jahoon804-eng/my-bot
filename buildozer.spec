[app]
title = My AI
package.name = myaimessenger
package.domain = my.ai
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 1.0
requirements = python3,kivy,kivymd,requests
orientation = portrait
fullscreen = 1
android.permissions = INTERNET
android.api = 33
android.minapi = 26
android.archs = arm64-v8a
android.ndk = 25b
p4a.branch = develop
android.skip_update = 1
android.accept_sdk_license = 1

[buildozer]
log_level = 2
warn_on_root = 1
