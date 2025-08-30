#!/bin/sh

echo "Удаление NixChat"

rm -r ~/.local/share/NixChat
rm ~/.local/bin/nixchat.sh
rm ~/.local/share/applications/nixchat.desktop
rm ~/.local/share/icons/hicolor/64x64/apps/nixchat.png
rm ~/.config/autostart/nixchat.desktop

echo "Удаление завершено"
