FILE='backup.pgsql'
USERNAME='root'
DBNAME='tarteeldb'
NUM_JOBS=4
LOCAL=true
print_usage() {
  echo "Usage: $0 [ -f FILE ]" 1>&2
}

exit_error() {
  print_usage
  exit 1
}

while getopts 'f:d:n:u:p' flag; do
  case "${flag}" in
    f) FILE=${OPTARG} ;;
    d) DBNAME=${OPTARG} ;;
    n) NUM_JOBS=${OPTARG} ;;
    p) PROD=true ;;
    u) USERNAME=${OPTARG} ;;
    *) exit_error ;;
  esac
done

# C: Creates the database
pg_restore -C -j $NUM_JOBS -h localhost -p 5432 -U $USERNAME -d $DBNAME $FILE