#!/bin/bash
DIR="$(cd "$(dirname "$0")" && pwd)"

cd "${DIR}"
for file in *.symlink; do
  dest="${HOME}/.${file%.symlink}"

  if [[ -e "${dest}" ]] && [[ ! -L "${dest}" ]]; then
    read -p "${dest} exists. Overwrite? [yN] " -r
    [[ ! "${REPLY}" =~ ^[Yy]$ ]] && exit 1
  fi

  echo "${dest}"
  ln -snf "${DIR}/${file}" "${dest}"
done

