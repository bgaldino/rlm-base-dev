# Interactive welcome banner for the RLM build container.
# Sourced by /etc/profile for login shells. Only print for interactive shells.
case "$-" in
  *i*) ;;
  *) return 2>/dev/null || exit 0 ;;
esac

printf '\n'
printf '\033[1;35m  Revenue Cloud Base Foundations\033[0m \033[2m— build environment\033[0m\n'
printf '\033[2m  ---------------------------------------------------------------\033[0m\n'
printf '  Two ways to work — run \033[36mrlm start\033[0m for a guided setup, or:\n\n'
printf '  \033[1m① Build a brand-new org\033[0m  (create your own scratch orgs)\n'
printf '       \033[36mrlm login --devhub\033[0m   connect a Salesforce Dev Hub\n'
printf '       \033[36mrlm build\033[0m            create + configure a new org\n'
printf '       \033[36mrlm open\033[0m             open it in your browser\n\n'
printf '  \033[1m② Customize an org you already have\033[0m  (sandbox / dev / scratch)\n'
printf '       \033[36mrlm login\033[0m            connect that org\n'
printf '       \033[36mrlm deploy\033[0m           apply the full RLM build to it\n'
printf '       \033[36mrlm customize\033[0m        run individual steps\n'
printf '       \033[36mrlm ask "..."\033[0m        change it with the AI assistant\n\n'
printf '  All commands: \033[36mrlm help\033[0m\n'
printf '\n'
