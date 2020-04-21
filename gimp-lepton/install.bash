base=~/.config/GIMP/2.99/plug-ins/file-lepton
bn=file-lepton.py
mkdir -p "$base"
ln -sf $PWD/gimp-2.99/"$bn" "$base"/"$bn"
