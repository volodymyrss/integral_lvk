set -x

mode=${1:-"process"}


case $mode in
  "streaming-gcn")
    echo "Running in dev mode"
    python3 -m engine.cli streaming gcn
    ;;
  "streaming-scimma")
    echo "Running in dev mode"
    python3 -m engine.cli streaming scimma
    ;;    
  "process")
    echo "Running in batch mode"
    export TMPDIR=/cache/tmp
    export HOME=/cache/home
    python3 -m engine.cli process-inbox /app/messages --publish
    ;;
  "babysit-realtime")
    echo "Running in babysit mode"
    python3 -m engine.cli babysit-realtime
    ;;
esac
    

