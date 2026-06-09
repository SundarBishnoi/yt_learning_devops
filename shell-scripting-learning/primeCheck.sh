#!/bin/bash

read -p "Enter a number: " num

if [ `expr $num < 2` ]
then
	echo "number is not prime number"
fi
