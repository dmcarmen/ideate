#! /bin/sh -
PROGNAME=$0

usage() {
  cat << EOF >&2
Usage: $PROGNAME [-l <lime_dir>]
       -l <lime_dir>: complete path to LIME folder (without ending /).
EOF
  exit 1
}

RED='\033[0;31m'
NC='\033[0m' # No Color
ERROR="${RED}Error:${NC}"
BASEDIR="$( cd "$( dirname "$0" )" && pwd )"

[ $# -eq 0 ] && usage
while getopts ":l:" arg; do
  case $arg in
    l)
      echo "Preparing pylime..."
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
                ./configure && make pylime && . ./pylimerc.sh #&>/dev/null        
            else
                echo -e "\t$ERROR no ./configure file found, make sure it is the correct folder."
                exit 1
            fi
        fi
        cd $BASEDIR 
      fi
      echo "Done preparing pylime!"
      ;;
    h | *) # Display help.
      usage
      exit 0
      ;;
  esac
done

echo -e "\nInstalling Python modules..."
pip install -r ideate_requirements.txt

echo "DONE!"

#chmod +x src/gui.py
#export PATH="$PATH:$HOME/bin"
#ln -s $BASEDIR/src/gui.py $HOME/bin/ideate #add shebang in gui.py

#PAST_PATH=$PATH
#echo $PATH
#export PATH=${PATH}:${BASEDIR}"/src"
#echo $PATH
#python src/gui.py
