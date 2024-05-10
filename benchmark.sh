#!/bin/bash

# create file to store the benchmark results
FILE=benchmark.txt
AWK_AVERAGE=average.awk
echo -n "" > $FILE

# qtd benchmarks
QTD=100

# flags
ALGORITHM=Dilithium2
PRIV_KEY=keys/dilithium_priv.key
PUB_KEY=keys/dilithium_pub.key

#ALGORITHM=rsa
#PRIV_KEY=keys/rsa_1024_priv.pem
#PUB_KEY=keys/rsa_1024_pub.pem

HASH=sha256
FILE_SIGN=msg/sample_message.txt
SIGNED_FILE=msg/sample_message_signature.mts

# commands
VERIFY_COMMAND="verify ${ALGORITHM} ${FILE_SIGN} ${PUB_KEY} ${SIGNED_FILE} ${HASH} --time-only"
SIGN_COMMAND="sign ${ALGORITHM} ${FILE_SIGN} ${PRIV_KEY} -k 1 ${HASH} --time-only"
CORRECT_COMMAND="verify-correct ${ALGORITHM} ${FILE_SIGN} ${PUB_KEY} ${SIGNED_FILE} ${HASH} --time-only"

COMMAND=$1
case "$COMMAND" in
  "sign")
    COMMAND_EXECUTE=$SIGN_COMMAND
    ;;
  "verify")
    COMMAND_EXECUTE=$VERIFY_COMMAND
    ;;
  "correct")
    COMMAND_EXECUTE=$CORRECT_COMMAND
    ;;
  *)
    echo "Invalid command. Use 'sign', 'verify' or 'correct'."
    exit 1
    ;;
esac

SCRIPT="python3 mtss_signer.py ${COMMAND_EXECUTE}"

# run the benchmark
echo "Running benchmark..."
for _ in $(seq 0 $QTD); do
  $SCRIPT >> $FILE
done

echo "Benchmark finished. Results saved in $FILE"


# parse the results and give the averate
SUM=0
for line in $(cat $FILE); do
  line=$(echo "scale=3; $line" | bc)
  SUM=$(echo "scale=3; $SUM + $line" | bc)
done

AVERAGE=$(echo "scale=5; $SUM / $QTD" | bc)
echo "Averate time for $QTD executions: $AVERAGE seconds"