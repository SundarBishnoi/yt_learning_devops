#!/bin/bash

x=mississippi

read -p "Enter the word to be searched on: " word
read -p "Enter the word to be counted: " index
grep -o "$index" <<<"$word" | wc -l
