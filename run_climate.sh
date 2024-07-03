#!/bin/bash
/usr/bin/Rscript climate.r
echo "$(date +%Y-%m-%d_%H:%M:%S)" > ../images/hook.txt
