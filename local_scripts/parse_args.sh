#!/bin/bash

avail="true"
i=0

for ARGUMENT in "$@"
do
	if [[ "$ARGUMENT" == "," ]]; then
		i=0
		avail="false"
		continue
	fi
	if [[ "$avail" == "true" ]]; then
		available_args[i]=$ARGUMENT
	else
		given_args[i]=$ARGUMENT
	fi
		
	let i=i+1
done

for ARGUMENT in "${given_args[@]}"
do

    KEY=$(echo $ARGUMENT | cut -f1 -d=)
    VALUE=$(echo $ARGUMENT | cut -f2 -d=)   

	for AVAIL in "${available_args[@]}"
	do
		if [[ "$KEY" == "$AVAIL" ]]
		then
			export $KEY=$VALUE
			break
		fi
	done
done

unset avail
unset i
unset ARGUMENT
unset KEY
unset VALUE
unset available_args
unset given_args