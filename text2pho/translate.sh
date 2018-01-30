arg1="$1"
filename=$(basename "$1")
filepath=$(dirname "$1")
extension="${filename##*.}"
filenoex="${filename%.*}"

procPath="mbrola/petr/"
pas="iluminat"

sshpass -p $pas scp $arg1 outsider@baiku.cz:$procPath"input.pho"
sshpass -p $pas ssh outsider@baiku.cz "cd $procPath && ./build2.sh"
sshpass -p $pas scp outsider@baiku.cz:$procPath"output.wav" "$filepath/$filenoex"".wav"
