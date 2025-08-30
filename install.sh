#!/bin/bash

DIR=~/.local/share/NixChat
OLD_DIR=$(pwd) 

echo "Установка NixChat"


# Get ready
echo "Подготовка..."

mkdir -p $DIR
mkdir -p ~/.local/share/applications
mkdir -p ~/.local/bin
mkdir -p ~/.local/share/icons/hicolor/64x64/apps
mkdir -p ~/.config/autostart


# Copy files
echo "Копирование файлов..."

cp main.py $DIR/main.py 
cp -r assets $DIR
cp assets/logo.png ~/.local/share/icons/hicolor/64x64/apps/nixchat.png


# Setup venv
echo "Настройка venv..."

cd $DIR
python3 -m venv venv
source venv/bin/activate


# Setup libraries
echo "Установка библиотек..."

pip install -r "$OLD_DIR/requirements.txt"


# Setup entries
echo "Создание ярлыков..."

cat > ~/.local/bin/nixchat.sh <<EOF
#!/bin/bash
DIR=~/.local/share/NixChat
cd $DIR
source $DIR/venv/bin/activate
python3 $DIR/main.py \$@
EOF

cat > ~/.local/share/applications/nixchat.desktop <<EOF
[Desktop Entry]
Name=NixChat
Comment=Простой и безопасный мессенджер
Exec=$HOME/.local/bin/nixchat.sh
Path=$HOME/.local/share/NixChat
Icon=nixchat
Type=Application
Categories=Network;
EOF

cat > ~/.config/autostart/nixchat.desktop <<EOF
[Desktop Entry]
Name=NixChat
Comment=Автозапуск NixChat
Exec=$HOME/.local/bin/nixchat.sh -H
Path=$HOME/.local/share/NixChat
Type=Application
X-GNOME-Autostart-enabled=true
EOF

chmod +x ~/.local/share/applications/nixchat.desktop
chmod +x ~/.local/bin/nixchat.sh
chmod +x ~/.config/autostart/nixchat.desktop

echo "Установка завершена!"
