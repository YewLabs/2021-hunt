#!/bin/bash
set -eu

OUTPUT_DIR="../../game"

npx webpack
rm -rf "${OUTPUT_DIR}/dist"
mv -T dist "${OUTPUT_DIR}/dist"
cp dseg7.woff "${OUTPUT_DIR}/dseg7.woff"
cp -rT audio "${OUTPUT_DIR}/audio"
cp yweiyst.html "${OUTPUT_DIR}/yweiyst.html"
sed -i 's/js\/init.js/dist\/main.js/g' "${OUTPUT_DIR}/yweiyst.html"
sed -i 's/audio\//{{sroot}}game\/audio\//g' "${OUTPUT_DIR}/yweiyst.html"
sed -i 's/dseg7\.woff/{{sroot}}dseg7\.woff/g' "${OUTPUT_DIR}/yweiyst.html"
