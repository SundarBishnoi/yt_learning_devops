#!/bin/bash

for i in {1..100}; do
if [ `expr $i % 2` == 0 ]
then
	echo "Number $i is even"
fi;
done

