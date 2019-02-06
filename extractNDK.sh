#!/bin/bash
mkdir NDK
for dir in SPUD_*/Moment*;do
cp $dir/C* NDK
done
