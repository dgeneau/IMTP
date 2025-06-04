# IMTP
Basic Reporting for IMTP Testing


## Requirements
- Athelte Force Plate TDMS file
- Protocol to inlcude athlete quiet standing to collect body weight.
- Sampling rate is assumed to be 1000Hz, only pulls longer than 2 seconds are detected.

## Interface
- Croping to onset feature will look for body weight before pull.
- You can naviagte to a quiet standing section, detect body weight and then enter body weight into the numerical input.
- Download CSV button will download the summary table at the bottom of the page
- Asymmetry calculation defined as ((Right - Left)/(Right + Left))
