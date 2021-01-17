#!/bin/fish

function source_venv
    source ./venv/bin/activate.fish
end

function convert_readme_pypi
    emacs --script convert-readme.el README.rst
end

function current_version
    grep -oP "(?<=version\ =\ )[^ ]*" ./setup.cfg
end

function up_version
    current_version | awk '{split($0,ver,"."); version=0; len=length(ver); for (i in ver){version+=ver[i]*10^(len-i); i++}; version++; printf "%03i", version}' | sed 's/./&./g;s/.$//'
end

function replace_version
    sed -i "s/^version = .*\$/version = $argv/" ./setup.cfg
end

function invoke_magit
    emacs --no-splash --eval "(progn (magit) (delete-other-windows))"
end

function clean_build
    rm -r ./*.egg-info
    rm -r ./dist
end

function clean_docs
    rm ./docs -r
end

function clean
    clean_build
    clean_docs
end

function build_docs
    pdoc --html librusapi
    mkdir docs
    mv ./html/librusapi/* docs
    rm ./html -r
end

function build
    python setup.py sdist
end

function run
    clean
    replace_version (up_version)
    convert_readme_pypi
    source_venv
    build_docs
    build
    invoke_magit
end
# 
function yesno
    read -p $argv' [Y/n] ' -l a
    switch $a
        case y Y
            true
        case '*'
            false
    end
end

function upgrade_prompt
    yesno 'set_color blue; printf "[UPGRADE]"; set_color white; printf " from "; set_color brcyan; printf "%s" (current_version); set_color white; printf " --> "; set_color brmagenta; printf "%s" (up_version); set_color white; printf "? [Y/n] "'
end

if not upgrade_prompt
    set_color red; echo "Aborting..."
    exit 0
end

echo "Activating venv..."
source_venv >> /dev/null 2>&1

echo "Cleaning up..."
clean >> /dev/null 2>&1

printf "Upping the version to %s...\n" (up_version)
replace_version (up_version) >> /dev/null 2>&1

echo "Converting README to a Pypi friendly one..."
convert_readme_pypi >> /dev/null 2>&1

echo "Generating docs..."
build_docs >> /dev/null 2>&1

echo "Building for Pypi..."
build >> /dev/null 2>&1

set head_before (git rev-parse --short HEAD)
printf "Current HEAD at %s\n" $head_before

echo "Running Magit..."
invoke_magit  >> /dev/null 2>&1

set head_after (git rev-parse --short HEAD)

if [ $head_before = $head_after ]
    echo "No new commits. Quitting..."
    exit 0
end

printf "HEAD %s --> %s\n" $head_before $head_after

set head_remote (git rev-parse --short origin/master)

if [ $head_after = $head_remote ]
    printf "Local (%s) == Remote (%s)\n" $head_after $head_remote
else
    printf "Local (%s) != Remote (%s)\n" $head_after $head_remote
end

if yesno "echo 'Push update to Pypi?'"
    echo "Uploading to Pypi..."
    twine upload dist/*
end
