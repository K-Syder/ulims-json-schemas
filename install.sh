#!/usr/bin/env bash

# Colours for output
HEADING='\033[1;32m'  # green
FLAG='\033[1;33m'  # yellow
DOING='\033[1;31m'  # red
RESET='\033[0m'

function heading() {
  echo
  echo -e "${HEADING}$1${RESET}"
}


function doing () {
    echo -e "  ${DOING}$1${RESET}"
}



heading "Install Python packages"
read -p "  Do you want to excute now? " answer

case $answer in
    [Yy] )  doing "Executing command..."
            pip install jsonschema
            pip install typer
            ;;
    [Xx] )  echo "    Exiting script"
            exit 0
            ;;
    * )     echo "    Skipped command"
  esac
