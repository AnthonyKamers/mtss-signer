#!/bin/bash
# qtd benchmarks
QTD=50

# flags
ALGORITHM=rsa
PRIV_KEY=keys/rsa_2048_priv.pem
#PRIV_KEY=keys/rsa_4096_priv.pem

#ALGORITHM=Dilithium2
#PRIV_KEY=keys/dilithium_2_priv.key

#ALGORITHM=Dilithium3
#PRIV_KEY=keys/dilithium_3_priv.key

#ALGORITHM=Dilithium5
#PRIV_KEY=keys/dilithium_5_priv.key

PUB_KEY=keys/rsa_4096_pub.pem

HASHES=(sha256 sha512 sha3-256 sha3-512 blake2b)
FILE_SIGN=msg/sign/q/125_10000.txt
K_SIGN=3
SIGNED_FILE=msg/sample_message_signature.mts

MTSS_COMMAND="python3 mtss_signer.py"
RAW_COMMAND="python3 sign_verify_traditional.py"

for hash in "${HASHES[@]}"; do
  # commands
  SIGN_COMMAND="${MTSS_COMMAND} sign ${ALGORITHM} ${FILE_SIGN} ${PRIV_KEY} -k ${K_SIGN} ${hash} --time-only"
  VERIFY_COMMAND="${MTSS_COMMAND} verify ${ALGORITHM} ${FILE_SIGN} ${PUB_KEY} ${SIGNED_FILE} ${hash} --time-only"
  CORRECT_COMMAND="${MTSS_COMMAND} verify-correct ${ALGORITHM} ${FILE_SIGN} ${PUB_KEY} ${SIGNED_FILE} ${hash} --time-only"
  SIGN_RAW="${RAW_COMMAND} sign ${ALGORITHM} ${FILE_SIGN} ${PRIV_KEY} ${hash}"
  VERIFY_RAW="${RAW_COMMAND} verify ${ALGORITHM} ${FILE_SIGN} ${PUB_KEY} ${SIGNED_FILE} ${hash}"

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

  # create file to keep results
  FILE=benchmark_${hash}.txt
  echo -n "" > $FILE

  # run the benchmark
  echo "Running benchmark for hash $hash..."
  for _ in $(seq 1 $QTD); do
    $COMMAND_EXECUTE >> $FILE
  done

  # parse the results and give the average
  SUM=0
  for line in $(cat $FILE); do
    line=$(echo "scale=3; $line" | bc)
    SUM=$(echo "scale=3; $SUM + $line" | bc)
  done
  AVERAGE=$(echo "scale=5; $SUM / $QTD" | bc)
  echo "Average time for $QTD executions (${ALGORITHM} - ${hash}): $AVERAGE seconds"

  rm "$FILE"
done