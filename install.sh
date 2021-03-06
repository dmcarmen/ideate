#! /bin/sh -
PROGNAME=$0

usage() {
  cat << EOF >&2
Usage: $PROGNAME [-l <lime_path>] [-m <mol_path>] [-p]
       -l <lime_path>: complete path to LIME folder (without trailing /). By default it will try to find the command pylime in PATH.
       -m <mol_path>: complete path where to save the molecules information (without trailing /). By default they will be saved in ideate/mols/.
       -p: if -p is provided required Python packages will be installed.
EOF
  exit 1
}

RED='\033[0;31m'
NC='\033[0m' # No Color
ERROR="${RED}Error:${NC}"
BASEPATH="$( cd "$( dirname "$0" )" && pwd )"
echo "[CONFIG]" > ideate_config.ini

unset -v LIME_PATH

#[ $# -eq 0 ] && usage
while getopts ":l:m:hp" arg; do
  case $arg in
    l)
      echo -e "\nPreparing pylime..."
      LIME_PATH=${OPTARG}
      if [ ! -d $LIME_PATH ]
      then
          echo -e "\t$ERROR Directory $LIME_PATH does not exists."
          exit 1
      else
        cd "$LIME_PATH"
        if [ -f pylime ]
        then
            echo -e "\tpylime file already exists. Good!"
            . ./pylimerc.sh
        else
            if [ -f configure ]
            then
                (./configure && make pylime && . ./pylimerc.sh) #&>/dev/null        
            else
                echo -e "\t$ERROR no ./configure file found, make sure it is the correct folder."
                exit 1
            fi
        fi
        cd $BASEPATH

      fi
      echo lime_path = $LIME_PATH >> ideate_config.ini
      echo "Done preparing pylime!"
      ;;
    m)
      echo mol_path = ${OPTARG} >> ideate_config.ini
      ;;
    p)
      echo -e "\nInstalling Python modules..."
      pip install -r ideate_requirements.txt
      pip install python-dateutil
      ;;
    h) # Display help.
      usage
      exit 1
      ;;
    :)
      echo -e "$ERROR -${OPTARG} requires an argument. Run ./install.sh -h to see the possible parameters."
      exit 1           
      ;;
  esac
done

if [ -z "$LIME_PATH" ]; then
    echo -e "\nLooking for pylime..."
    if ! command -v pylime &> /dev/null
    then
        echo -e "$ERROR Missing -l <lime_path> parameter and pylime could not be found" >&2
        rm ideate_config.ini
        exit 1
    else
        PYLIME=$(command -v pylime)
        echo -e "\t$PYLIME found"
        LIME_PATH="$(dirname "${PYLIME}")"
        echo lime_path = $LIME_PATH >> ideate_config.ini
    fi
fi


echo ideate_path = $BASEPATH >> ideate_config.ini

echo "DONE!"

#chmod +x src/ideate.py
#export PATH="$PATH:$HOME/bin"
#ln -s $BASEPATH/src/ideate.py $HOME/bin/ideate #add shebang in ideate.py

#PAST_PATH=$PATH
#echo $PATH
#export PATH=${PATH}:${BASEPATH}"/src"
#echo $PATH
#python src/ideate.py
