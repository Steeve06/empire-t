#!/usr/bin/env bash
# Shared by the operations scripts: read an env file the way Docker Compose does,
# as literal KEY=value lines, instead of executing it with `source`. Values such as
# `Empire T <no-reply@...>` or passwords with shell characters are then safe.

# load_env FILE: export every KEY=value line (comments and blank lines skipped,
# one pair of surrounding quotes removed).
load_env() {
  local file=$1 line key value
  [[ -f $file ]] || { echo "Missing $file"; return 1; }
  while IFS= read -r line || [[ -n $line ]]; do
    line=${line%$'\r'}
    [[ $line =~ ^[[:space:]]*(#|$) ]] && continue
    [[ $line =~ ^([A-Za-z_][A-Za-z0-9_]*)=(.*)$ ]] || continue
    key=${BASH_REMATCH[1]}
    value=${BASH_REMATCH[2]}
    if [[ $value =~ ^\"(.*)\"$ ]] || [[ $value =~ ^\'(.*)\'$ ]]; then
      value=${BASH_REMATCH[1]}
    fi
    export "$key=$value"
  done < "$file"
}
