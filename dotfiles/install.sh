#!/bin/sh
DIR="$(cd "$(dirname "$0")" && pwd)"

cd "${DIR}"
for file in *.symlink; do
  dest="${HOME}/.${file%.symlink}"

  if [ -r "${dest}" ] && [ ! -h "${dest}" ]; then
    printf "${dest} exists. Overwrite? [yN] "
    read -r reply
    case "${reply}" in
      y*|Y*) ;;
      *) continue;;
    esac
  fi

  echo "${dest}"
  ln -snf "${DIR}/${file}" "${dest}"
done

