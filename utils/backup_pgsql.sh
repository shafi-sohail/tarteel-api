DB=tarteeldb
HOST=tarteeldb.ctqaquwebud0.us-west-2.rds.amazonaws.com
PORT=5432
USERNAME=root
PASS=''
OUTFILE='backup-'
OUTFILE+=$(date +%m-%d-%Y)
OUTFILE+='.pgsql'

print_usage() {
  echo "Usage: $0 [ -d DB ] [ -h HOST ]" 1>&2
}

exit_error() {
  print_usage
  exit 1
}

while getopts 'd:h:p:' flag; do
  case "${flag}" in
    d) DB=${OPTARG} ;;
    h) HOST=${OPTARG} ;;
    p) PORT=${OPTARG} ;;
    *) exit_error ;;
  esac
done

# -Fc: Custom file format, compresses data without compromising on time
pg_dump -Fc -h $HOST -d $DB -p $PORT -U $USERNAME > $OUTFILE