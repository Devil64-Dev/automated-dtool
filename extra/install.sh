#!/usr/bin/sh

# author: Devil64-Dev
# This script is only for ArchLinux and Debian based systems.

decoration() {
  LENGTH=$(($(tput cols) - 1))
  DECORATION="-"
  while [ "$LENGTH" -ge 1 ]; do
    DECORATION=${DECORATION}"-"
    LENGTH=$((LENGTH - 1))
  done
}

init_all() {
  clear

  # URL
  REPO="https://github.com/Devil64-Dev/automated-dtool"
  REPO_NAME="automated-dtool"
  # COLORS
  RED="\e[31m"
  GREEN="\e[32m"
  YELLOW="\e[33m"
  BLUE="\e[34m"
  CYAN="\e[36m"

  # TEXT STYLE
  RESET="\e[0m" # normal text, reset all style
  BOLD="\e[1m"
  # FAINT="\e[2m"
  ITALIC="\e[3m"
  UNDERLINE="\e[4m"

  # SLEEP VALUES
  LARGE=0.4
  NORMAL=0.2

  # ECHO VARS
  BS="-e"
  NL="\n"
  CI="\ci"

  # PROGRAM VARIABLES
  # install paths and file names
  DEFAULT_PATH="/usr/bin"
  NEEDED_PACKAGES="git python3 pip3 ffmpeg"
  PYTHON_MODULES="requests lxml selenium pycryptodome"
  EXTRA_URL="https://raw.githubusercontent.com/Devil64-Dev/automated-dtool/extras/"
  # package manager
  PM_LIST="pacman apt-get"
  # if exists a valid package manager it will create PACKAGE_MANAGER var
  get_package_manager
  if [ $? -eq 1 ]; then
    exit_info
    return 1
  fi

  # retries
  install_retries=2
}

exit_info() {
  echo ${BS} "${YELLOW}${NL}For more help visit: ${ITALIC}${UNDERLINE}${REPO}/docs/manual_installation.es.md${RESET}"
  sleep ${NORMAL}
  echo ${BS} "${NL}${RED}${BOLD}ERROR: ${RESET}${RED}Needed packages can't be found or installed. Exiting...${RESET}"
}

success() {
  echo ${BS} "${GREEN}${BOLD}${NL}Installation success${RESET}"
  sleep ${NORMAL}
}

# search in DEFAULT_PATH for valid package manager stored PM_LIST
get_package_manager() {
  echo "${DECORATION}"
  sleep ${NORMAL}
  echo ${BS} "${BLUE}Searching for valid package manager...${RESET}"
  sleep ${LARGE}

  for PACKAGE in ${PM_LIST}; do
    if [ -f "${DEFAULT_PATH}/${PACKAGE}" ]; then
      PACKAGE_MANAGER="${PACKAGE}"
      echo ${BS} "${GREEN}Valid package manager found: ${RESET}${BOLD}${PACKAGE_MANAGER}${RESET} ${GREEN}in ${RESET}${DEFAULT_PATH}"
      sleep ${NORMAL}

      return 0
    else
      echo ${BS} "${RED}Valid package manager not found"
      sleep ${NORMAL}

      return 1
    fi
  done
}

check_packages() {
  PACKAGES=""
  echo "${DECORATION}"
  sleep ${NORMAL}
  echo ${BS} "${BLUE}Searching for needed packages${RESET}"
  sleep ${LARGE}

  # Check if packages are already installed
  for PACKAGE in ${NEEDED_PACKAGES}; do
    if [ -f "${DEFAULT_PATH}/${PACKAGE}" ]; then
      echo ${BS} "${GREEN}Found executable: ${RESET}${BOLD}${PACKAGE}${RESET} ${GREEN}in ${RESET}${DEFAULT_PATH}"
      sleep ${NORMAL}
    else
      echo ${BS} "${YELLOW}Executable ${BOLD}${PACKAGE}${RESET}${YELLOW} not found in ${DEFAULT_PATH}. Adding to installation list...${RESET}"
      PACKAGES="${PACKAGES}${PACKAGE} "
      sleep ${NORMAL}
    fi
  done

  # Check if has packages to install
  if [ "${PACKAGES}" ]; then
    # Install not found packages
    install_packages "${PACKAGES}"
    # Installation fails?, just upgrade system and retry
    if [ $? -eq 1 ]; then
      if [ ${install_retries} -eq 1 ]; then
        exit_info
        return 1
      fi
      echo ${BS} "${YELLOW}Error installing some needed packages, update the system and retry?${RESET}"
      sleep ${LARGE}
      echo ${BS} "${GREEN}    1. Yes, update it."
      sleep ${NORMAL}
      echo ${BS} "${YELLOW}    2. No, cancel installation."
      sleep ${NORMAL}
      echo ${BS} "${RESET}What would you like to do?: ${CI}"
      sleep ${NORMAL}
      read -r OPTION
      if [ "${OPTION}" = "1" ]; then
        echo ${BS} "${NL}${GREEN}Updating system..."
        sleep ${LARGE}
        if update_packages; then
          echo ${BS} "${NL}${GREEN}System updated complete, retrying needed packages installation${RESET}"
          sleep ${LARGE}
          install_retries=$((install_retries - 1))
          if check_packages; then
            # success
            return 0
          fi
        else
          echo ${BS} "${NL}${RED}System updated failed, check your internet connection, or check if your OS is supported."
          sleep ${LARGE}
          exit_info

          return 1
        fi
      else
        echo ${BS} "${YELLOW}${NL}For more help visit: ${ITALIC}${UNDERLINE}${REPO}/docs/manual_installation.es.md${RESET}"
        echo ${BS} "${RED}${NL}Installation aborted. Exiting${RESET}"
        return 1
      fi
    else
      # success
      return 0
    fi
  else
    # success
    return 0
  fi
}

install_packages() {
  if [ "${PACKAGE_MANAGER}" = "pacman" ] || [ "${PACKAGE_MANAGER}" = "apt-get" ]; then
    echo "${DECORATION}"
    sleep ${NORMAL}
    echo ${BS} "${BLUE}Installing not found packages${RESET}"
    sleep "${LARGE}"
  else sleep ${NORMAL};
  fi


  PACKAGES=$1
  for PACKAGE in ${PACKAGES}; do
    if [ "${PACKAGE_MANAGER}" = "pacman" ]; then
      INSTALL_OPTION="-S"
      EXTRA_OPTION="--confirm"
      if [ "${PACKAGE}" = "python3" ]; then PACKAGE="python"; fi
      if [ "${PACKAGE}" = "pip3" ]; then PACKAGE="python-pip"; fi
    else
      INSTALL_OPTION="install"
      EXTRA_OPTION="-y"
      if [ "${PACKAGE}" = "pip3" ]; then PACKAGE="python3-pip"; fi
    fi

    echo ${BS} "${CYAN}Installing ${BOLD}${PACKAGE}${RESET}${CYAN}, using ${BOLD}${PACKAGE_MANAGER}${RESET}"
    sleep ${NORMAL}
    retries=3
    while [ ${retries} -ge 1 ]; do
      if [ "${PACKAGE_MANAGER}" = "pip3" ]; then
        sudo "${PACKAGE_MANAGER}" "install" "${PACKAGE}"
      elif [ "${PACKAGE_MANAGER}" = "git" ]; then
        "${PACKAGE_MANAGER}" "clone" "--branch=${VERSION}" "${REPO}"
      elif [ "${PACKAGE_MANAGER}" = "wget" ]; then
        "${PACKAGE_MANAGER}" "${EXTRA_URL}${PACKAGE}"
      else
        sudo "${PACKAGE_MANAGER}" ${INSTALL_OPTION} ${EXTRA_OPTION} ${PACKAGE}
      fi
      RESULT=$?
      if [ ${RESULT} -ne 0 ]; then
        retries=$((retries - 1))
        if [ "${PACKAGE_MANAGER}" = "git" ] || [ "${PACKAGE_MANAGER}" = "wget" ] ; then
          echo ${BS} "${YELLOW}Error downloading program, Retries ${retries}...${RESET}"
        else
          echo ${BS} "${YELLOW}Error in package installation, Retries ${retries}...${RESET}"
        fi
        sleep ${LARGE}

        if [ ${retries} -eq 0 ]; then return 1; fi
      else
        break
      fi
    done
    if [ "${PACKAGE_MANAGER}" = "git" ] || [ "${PACKAGE_MANAGER}" = "wget" ]; then
      echo ${BS} "${GREEN}Program download success."
    else
      echo ${BS} "${GREEN}Package installation success."
    fi
    sleep ${LARGE}
  done
}

update_packages() {
  if [ "${PACKAGE_MANAGER}" = "pacman" ]; then
    sudo "${PACKAGE_MANAGER}" "-Syu" "--noconfirm"
  else
    sudo "${PACKAGE_MANAGER}" "update"
    sudo "${PACKAGE_MANAGER}" "upgrade" "-y"
  fi
}

install_modules() {
  PACKAGE_MANAGER="pip3"
  echo "${DECORATION}"
  sleep ${NORMAL}
  echo ${BS} "${BLUE}Installing python modules${RESET}"
  sleep ${LARGE}
  install_packages "${PYTHON_MODULES}"
}

# clone project repository
clone_repo() {
  echo "${DECORATION}"
  sleep ${NORMAL}
  echo ${BS} "${BLUE}Installing program...${RESET}"
  sleep ${LARGE}

  # ends if project exists in this path
  if [ -f "${REPO_NAME}/dtool.py" ]; then
    echo ${BS} "${GREEN}Program already downloaded in this path."
    sleep ${NORMAL}
    return 0;
  elif [ -d "${REPO_NAME}" ]; then
    echo ${BS} "${YELLOW}Directory ${REPO_NAME} found, but no contains needed files, deleting..."
    "sudo" "rm" "-r" "${REPO_NAME}"
    sleep ${NORMAL}
  fi
  # Program branch
  # select
  echo ${BS} "${CYAN}Select your favourite program version"
  sleep ${NORMAL}
  echo ${BS} "${GREEN}    1. master (~6MB)"
  sleep ${NORMAL}
  echo ${BS} "${YELLOW}    2. full (~55MB)"
  sleep ${NORMAL}
  echo ${BS} "${RESET}Version => ${CI}"
  read -r VERSION
  sleep ${NORMAL}
  # check program version, default to master if is none
  if [ "${VERSION}" = "2" ]; then VERSION="full"; else VERSION="master"; fi
  echo ${BS} "${CYAN}Downloading ${VERSION} version using ${BOLD}git${RESET}${CYAN}..."
  sleep ${NORMAL}

  # download
  PACKAGE_MANAGER="git"
  if install_packages ${REPO_NAME}; then
    return 0
  else
    exit_info
    return 1
  fi
}

download(){
  sleep ${NORMAL}
  echo ${BS} "${BLUE}Download binaries...${RESET}"
  sleep ${LARGE}
  if [ -f "geckodriver" ]; then
    echo ${BS} "${GREEN}Firefox driver found. Skipping this step"
    EXTRA="${EXTRA} geckodriver"
    return 0
  elif [ -d "chromedriver" ]; then
    echo ${BS} "${GREEN}Chromium driver found. Skipping this step"
    EXTRA="${EXTRA} geckodriver"
    return 0
  fi

  echo ${BS} "${CYAN}Select your favourite browser"
  sleep ${NORMAL}
  echo ${BS} "${GREEN}    1. Firefox"
  sleep ${NORMAL}
  echo ${BS} "${YELLOW}    2. Chromium"
  sleep ${NORMAL}
  echo ${BS} "${RESET}Version => ${CI}"
  read -r BROWSER
  sleep ${NORMAL}
  if ${BROWSER} = "2"; then EXTRA="${EXTRA} chromedriver"; BROWSER="Chromium";
  else EXTRA="${EXTRA} geckodriver"; BROWSER="Firefox"; fi

  echo ${BS} "${CYAN}Downloading needed files for ${BOLD}${BROWSER}${RESET}${CYAN}..."
  sleep ${NORMAL}

  PACKAGE_MANAGER="wget"
  if install_packages "${EXTRA}"; then return 0; else exit_info; return 1; fi
}

install(){
  echo "${DECORATION}"
  sleep ${NORMAL}
  echo ${BS} "${BLUE}Installing...${RESET}"
  sleep ${LARGE}

  if [ -f "${DEFAULT_PATH}/geckodriver" ]; then
    echo ${BS} "${GREEN}Firefox driver found in ${DEFAULT_PATH}. Skipping this step"
    return 0
  elif [ -f "${DEFAULT_PATH}/chromedriver" ]; then
    echo ${BS} "${GREEN}Firefox driver found in ${DEFAULT_PATH}. Skipping this step"
    return 0
  fi

  if download; then
    for FILE in ${EXTRA}; do
      sudo "mv" "${FILE}" "${DEFAULT_PATH}"
    done
  else
    return 1
  fi

  echo ${BS} "${CYAN}Installing script."
  if sudo "ln" "-srf" "${REPO_NAME}/dtool.py" "${DEFAULT_PATH}"; then
    echo ${BS} "${GREEN}Script installed, run ${RESET}${BOLD}automated-dtool${RESET}${GREEN} command"
    return 0
  else
    exit_info
    return 1
  fi
}

decoration
init_all

if ! check_packages; then exit; fi
if ! install_modules; then exit; fi
if ! clone_repo; then exit; fi
if ! install; then exit; fi
success
