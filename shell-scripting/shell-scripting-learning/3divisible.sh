#!/bin/bash

for i in {1..100};do
if [ `expr $i % 3` == 0 ]
then
	echo "Number $i is factor of 3"
fi;
done

