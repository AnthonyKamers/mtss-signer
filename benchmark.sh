#!/bin/bash

# create file to store the benchmark results
FILE=benchmark.txt
echo -n "" > $FILE

# qtd benchmarks
QTD=50

# flags
#ALGORITHM=Dilithium2
#PRIV_KEY=keys/dilithium_priv.key
#PUB_KEY=keys/dilithium_pub.key

ALGORITHM=Dilithium5
PRIV_KEY=keys/dilithium_5_priv.key
PUB_KEY=keys/rsa_4096_pub.pem

HASH=sha512
FILE_SIGN=msg/sign/q/125_10000.txt
K_SIGN=3
SIGNED_FILE=msg/sample_message_signature.mts

# raw commands
MTSS_COMMAND="python3 mtss_signer.py"
RAW_COMMAND="python3 sign_verify_traditional.py"

# commands
SIGN_COMMAND="${MTSS_COMMAND} sign ${ALGORITHM} ${FILE_SIGN} ${PRIV_KEY} -k ${K_SIGN} ${HASH} --time-only"
VERIFY_COMMAND="${MTSS_COMMAND} verify ${ALGORITHM} ${FILE_SIGN} ${PUB_KEY} ${SIGNED_FILE} ${HASH} --time-only"
CORRECT_COMMAND="${MTSS_COMMAND} verify-correct ${ALGORITHM} ${FILE_SIGN} ${PUB_KEY} ${SIGNED_FILE} ${HASH} --time-only"
SIGN_RAW="${RAW_COMMAND} sign ${ALGORITHM} ${FILE_SIGN} ${PRIV_KEY} ${HASH}"
VERIFY_RAW="${RAW_COMMAND} verify ${ALGORITHM} ${FILE_SIGN} ${PUB_KEY} ${SIGNED_FILE} ${HASH}"

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
  "sign-raw")
    COMMAND_EXECUTE=$SIGN_RAW
    ;;
  "verify-raw")
    COMMAND_EXECUTE=$VERIFY_RAW
    ;;
  *)
    echo "Invalid command. Use 'sign', 'verify', 'correct', 'sign-raw' or 'verify-raw'."
    exit 1
    ;;
esac

# run the benchmark
echo "Running benchmark..."
for _ in $(seq 1 $QTD); do
  $COMMAND_EXECUTE >> $FILE
done

echo "Benchmark finished. Results saved in $FILE"


# parse the results and give the average
SUM=0
for line in $(cat $FILE); do
  line=$(echo "scale=3; $line" | bc)
  SUM=$(echo "scale=3; $SUM + $line" | bc)
done

AVERAGE=$(echo "scale=5; $SUM / $QTD" | bc)
echo "Average time for $QTD executions: $AVERAGE seconds"